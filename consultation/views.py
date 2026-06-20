from django.contrib import messages
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.views.decorators.http import require_POST

from .forms import ConsultationForm
from .models import ConsultationRequest, ConsultationTopic
from agritech.utils import login_required_session
from agritech.utils import doctor_required, consultant_required
from accounts.models import Doctor, Consultant


def _auto_assign_staff():

    doctor = Doctor.objects.filter(
        is_approved=True,
        is_active_status=True,
        is_online=True,
    ).order_by('-last_seen', 'registration_date').first()

    consultant = Consultant.objects.filter(
        is_approved=True,
        is_active_status=True,
        is_online=True,
    ).order_by('-last_seen', 'registration_date').first()

    return doctor, consultant


def _dashboard_filter_label(raw_filter):

    valid_filters = {'all', 'pending', 'completed', 'farmers'}

    if raw_filter not in valid_filters:
        return 'all'

    return raw_filter


def _filtered_consultation_queryset(base_queryset, search_query, active_filter):

    queryset = base_queryset

    if active_filter == 'pending':
        queryset = queryset.filter(status='Pending')
    elif active_filter == 'completed':
        queryset = queryset.filter(status='Completed')

    if search_query:
        queryset = queryset.filter(
            Q(name__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(phone__icontains=search_query) |
            Q(farmer__name__icontains=search_query)
        )

    return queryset.order_by('-created_at')


def _dashboard_context(request, owner_field_name, owner_id, role_label):

    active_filter = _dashboard_filter_label(request.GET.get('filter', 'all'))
    search_query = request.GET.get('q', '').strip()

    base_queryset = ConsultationRequest.objects.filter(
        **{owner_field_name: owner_id}
    ).select_related('farmer')

    filtered_queryset = _filtered_consultation_queryset(
        base_queryset,
        search_query,
        active_filter,
    )

    if active_filter == 'farmers':
        seen_farmer_ids = set()
        requests_list = []

        for request_obj in filtered_queryset:
            if not request_obj.farmer_id:
                continue

            if request_obj.farmer_id in seen_farmer_ids:
                continue

            seen_farmer_ids.add(request_obj.farmer_id)
            requests_list.append(request_obj)
    else:
        requests_list = filtered_queryset

    return {
        'requests': requests_list,
        'total_requests': base_queryset.count(),
        'pending_requests': base_queryset.filter(status='Pending').count(),
        'completed_requests': base_queryset.filter(status='Completed').count(),
        'active_farmers': base_queryset.values('farmer_id').distinct().count(),
        'search_query': search_query,
        'active_filter': active_filter,
        'active_filter_label': role_label,
    }



@login_required_session
def consultation(request):

    consultation_topics = ConsultationTopic.objects.filter(
        is_active=True
    ).order_by('display_order', 'title')

    if request.method == 'POST':

        form = ConsultationForm(request.POST)

        if form.is_valid():

            consultation = form.save(commit=False)

            farmer_id = request.session.get('farmer_id')

            if farmer_id:
                consultation.farmer_id = farmer_id

            assigned_doctor, assigned_consultant = _auto_assign_staff()
            consultation.assigned_doctor = assigned_doctor
            consultation.assigned_consultant = assigned_consultant
            consultation.status = 'Pending'

            consultation.save()

            return render(
                request,
                'consultation/consultation.html',
                {
                    'form': ConsultationForm(),
                    'success': True,
                    'consultation_topics': consultation_topics
                }
            )

        else:
            print(form.errors)

    else:
        form = ConsultationForm()

    return render(
        request,
        'consultation/consultation.html',
        {
            'form': form,
            'consultation_topics': consultation_topics,
            'doctors': Doctor.objects.filter(
                is_approved=True, is_active_status=True
            ).order_by('-is_online', 'full_name'),
            'consultants': Consultant.objects.filter(
                is_approved=True, is_active_status=True
            ).order_by('-is_online', 'full_name'),
        }
    )


@login_required_session
def consultation_topic_detail(request, slug):

    topic = get_object_or_404(
        ConsultationTopic,
        slug=slug,
        is_active=True
    )

    related_topics = ConsultationTopic.objects.filter(
        is_active=True
    ).exclude(
        id=topic.id
    ).order_by('display_order', 'title')[:3]

    return render(
        request,
        'consultation/consultation_detail.html',
        {
            'topic': topic,
            'related_topics': related_topics,
        }
    )


def _parse_status_value(value):

    if value is None:
        return None

    normalized_value = str(value).strip().lower()

    if normalized_value in {'true', '1', 'yes', 'on'}:
        return True

    if normalized_value in {'false', '0', 'no', 'off'}:
        return False

    return None


def _update_availability(request, model, session_key, dashboard_name, role_label):

    account = get_object_or_404(model, id=request.session.get(session_key))
    next_status = _parse_status_value(request.POST.get('is_online'))

    if next_status is None:
        messages.error(request, 'Invalid availability status.')
        return redirect(dashboard_name)

    now = timezone.now()
    account.is_online = next_status
    account.is_active_status = next_status
    account.last_seen = now
    if hasattr(account, 'last_login_time') and next_status:
        account.last_login_time = now
        account.save(update_fields=['is_online', 'is_active_status', 'last_seen', 'last_login_time'])
    else:
        account.save(update_fields=['is_online', 'is_active_status', 'last_seen'])

    messages.success(request, f'{role_label} availability updated.')
    return redirect(dashboard_name)


@require_POST
@doctor_required
def update_doctor_availability(request):
    return _update_availability(
        request, Doctor, 'doctor_id', 'doctor_dashboard', 'Doctor'
    )


@require_POST
@consultant_required
def update_consultant_availability(request):
    return _update_availability(
        request, Consultant, 'consultant_id', 'consultant_dashboard', 'Consultant'
    )


@doctor_required
def doctor_dashboard(request):

    doctor_id = request.session.get('doctor_id')
    context = {
        'doctor': Doctor.objects.filter(id=doctor_id).first(),
        **_dashboard_context(request, 'assigned_doctor_id', doctor_id, 'Doctor'),
    }

    return render(request, 'doctor/dashboard.html', context)


@consultant_required
def consultant_dashboard(request):

    consultant_id = request.session.get('consultant_id')
    context = {
        'consultant': Consultant.objects.filter(id=consultant_id).first(),
        **_dashboard_context(request, 'assigned_consultant_id', consultant_id, 'Consultant'),
    }

    return render(request, 'consultant/dashboard.html', context)


@doctor_required
def doctor_consultation_detail(request, pk):

    consultation = get_object_or_404(
        ConsultationRequest,
        pk=pk,
        assigned_doctor_id=request.session.get('doctor_id')
    )

    if request.method == 'POST':

        consultation.status = request.POST.get('status', consultation.status)
        consultation.doctor_reply = request.POST.get('reply', consultation.doctor_reply)
        consultation.save()

        messages.success(request, 'Consultation updated successfully.')

        return redirect('doctor_dashboard')

    return render(
        request,
        'doctor/consultation_detail.html',
        {'consultation': consultation}
    )


@consultant_required
def consultant_consultation_detail(request, pk):

    consultation = get_object_or_404(
        ConsultationRequest,
        pk=pk,
        assigned_consultant_id=request.session.get('consultant_id')
    )

    if request.method == 'POST':

        consultation.status = request.POST.get('status', consultation.status)
        consultation.consultant_reply = request.POST.get('reply', consultation.consultant_reply)
        consultation.save()

        messages.success(request, 'Consultation updated successfully.')

        return redirect('consultant_dashboard')

    return render(
        request,
        'consultant/consultation_detail.html',
        {'consultation': consultation}
    )


@login_required_session
def my_consultations(request):

    farmer_id = request.session.get('farmer_id')

    consultations = ConsultationRequest.objects.filter(
        farmer_id=farmer_id
    ).order_by('-created_at')

    return render(
        request,
        'consultation/my_consultations.html',
        {
            'consultations': consultations
        }
    )
    
def doctor_status_toggle(request):

    if request.method != 'POST':
        return redirect('doctor_dashboard')

    doctor_id = request.session.get('doctor_id')

    if not doctor_id:
        return redirect('login')

    doctor = Doctor.objects.filter(id=doctor_id).first()

    if doctor:
        next_status = _parse_status_value(request.POST.get('is_online'))

        if next_status is not None:
            now = timezone.now()
            doctor.is_online = next_status
            doctor.is_active_status = next_status
            doctor.last_seen = now
            if next_status:
                doctor.last_login_time = now
                doctor.save(update_fields=['is_online', 'is_active_status', 'last_seen', 'last_login_time'])
            else:
                doctor.save(update_fields=['is_online', 'is_active_status', 'last_seen'])

    return redirect('doctor_dashboard')


def consultant_status_toggle(request):

    if request.method != 'POST':
        return redirect('consultant_dashboard')

    consultant_id = request.session.get('consultant_id')

    if not consultant_id:
        return redirect('login')

    consultant = Consultant.objects.filter(id=consultant_id).first()

    if consultant:
        next_status = _parse_status_value(request.POST.get('is_online'))

        if next_status is not None:
            now = timezone.now()
            consultant.is_online = next_status
            consultant.is_active_status = next_status
            consultant.last_seen = now
            if next_status:
                consultant.last_login_time = now
                consultant.save(update_fields=['is_online', 'is_active_status', 'last_seen', 'last_login_time'])
            else:
                consultant.save(update_fields=['is_online', 'is_active_status', 'last_seen'])

    return redirect('consultant_dashboard')
