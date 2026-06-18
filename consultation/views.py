from django.contrib import messages
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone

from .forms import ConsultationForm
from .models import ConsultationRequest
from agritech.utils import login_required_session
from agritech.utils import doctor_required, consultant_required
from accounts.models import Doctor, Consultant


def _auto_assign_staff():

    doctor = Doctor.objects.filter(
        is_approved=True,
        is_active_status=True
    ).order_by('-last_login_time', 'registration_date').first()

    consultant = Consultant.objects.filter(
        is_approved=True,
        is_active_status=True
    ).order_by('-last_login_time', 'registration_date').first()

    return doctor, consultant


@login_required_session
def consultation(request):

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
                    'success': True
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
            'form': form
        }
    )


@doctor_required
def doctor_dashboard(request):

    doctor_id = request.session.get('doctor_id')
    status_filter = request.GET.get('status', '')
    search_query = request.GET.get('q', '')

    requests_qs = ConsultationRequest.objects.filter(
        assigned_doctor_id=doctor_id
    ).select_related('farmer').order_by('-created_at')

    if status_filter:
        requests_qs = requests_qs.filter(status=status_filter)

    if search_query:
        requests_qs = requests_qs.filter(
            Q(name__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(phone__icontains=search_query) |
            Q(message__icontains=search_query)
        )

    context = {
        'doctor': Doctor.objects.filter(id=doctor_id).first(),
        'requests': requests_qs,
        'total_requests': ConsultationRequest.objects.filter(
            assigned_doctor_id=doctor_id
        ).count(),
        'pending_requests': ConsultationRequest.objects.filter(
            assigned_doctor_id=doctor_id,
            status='Pending'
        ).count(),
        'completed_requests': ConsultationRequest.objects.filter(
            assigned_doctor_id=doctor_id,
            status='Completed'
        ).count(),
        'active_farmers': ConsultationRequest.objects.filter(
            assigned_doctor_id=doctor_id
        ).values('farmer_id').distinct().count(),
        'status_filter': status_filter,
        'search_query': search_query,
    }

    return render(request, 'doctor/dashboard.html', context)


@consultant_required
def consultant_dashboard(request):

    consultant_id = request.session.get('consultant_id')
    status_filter = request.GET.get('status', '')
    search_query = request.GET.get('q', '')

    requests_qs = ConsultationRequest.objects.filter(
        assigned_consultant_id=consultant_id
    ).select_related('farmer').order_by('-created_at')

    if status_filter:
        requests_qs = requests_qs.filter(status=status_filter)

    if search_query:
        requests_qs = requests_qs.filter(
            Q(name__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(phone__icontains=search_query) |
            Q(message__icontains=search_query)
        )

    context = {
        'consultant': Consultant.objects.filter(id=consultant_id).first(),
        'requests': requests_qs,
        'total_requests': ConsultationRequest.objects.filter(
            assigned_consultant_id=consultant_id
        ).count(),
        'pending_requests': ConsultationRequest.objects.filter(
            assigned_consultant_id=consultant_id,
            status='Pending'
        ).count(),
        'completed_requests': ConsultationRequest.objects.filter(
            assigned_consultant_id=consultant_id,
            status='Completed'
        ).count(),
        'active_farmers': ConsultationRequest.objects.filter(
            assigned_consultant_id=consultant_id
        ).values('farmer_id').distinct().count(),
        'status_filter': status_filter,
        'search_query': search_query,
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