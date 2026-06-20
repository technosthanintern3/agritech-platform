from functools import wraps

from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth import get_user_model
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import AuthenticationForm
from django.core.paginator import Paginator
from django.shortcuts import render
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils import timezone
from accounts.models import Farmer, Doctor, Consultant, IdentityChangeRequest, AdminProfile, RegistrationField, Role, VerificationHistory
from products.models import SeedVariety
from dashboard.forms import ProductForm
from machinery.models import Machinery, TractorBooking
from dashboard.forms import MachineryForm
from orders.models import Order
from consultation.models import ConsultationRequest, ConsultationTopic
from services.models import ServiceInfo
from farmer_support.models import CropProblem, CropProblemGuide
from farmer_support.models import (
    CropProblem,
    AdminReply
)
from django.db.models import Count, Avg
from django.db.models import Q
from services.models import ServiceRequest
from products.models import Crop, Review, SeedVariety
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils.text import slugify
from company.models import SiteSettings
from accounts.models import (
    SiteSettings,
    WhyChooseUs,
    FooterSettings,
    RolePageSettings
)
from accounts.models import AccessCode

from dashboard.forms import (
    SiteSettingsForm,
    WhyChooseUsForm,
    FooterSettingsForm,
    RolePageSettingsForm,
    AdminCreateForm,
    AdminProfileForm,
    AccessCodeManagementForm,
    RegistrationFieldForm,
    RoleManagementForm,
    ServiceInfoForm,
    ConsultationTopicForm,
    CropProblemGuideForm,
    CropForm,
)
from accounts.forms import PasswordChangeForm


User = get_user_model()

CONTENT_MODELS = {
    'services': (ServiceInfo, ServiceInfoForm, 'service_form'),
    'products': (SeedVariety, ProductForm, 'product_form'),
    'consultations': (ConsultationTopic, ConsultationTopicForm, 'consultation_form'),
    'crop-problems': (CropProblemGuide, CropProblemGuideForm, 'crop_problem_form'),
}


def admin_required(view_func):

    @wraps(view_func)
    def wrapper(request, *args, **kwargs):

        if not request.user.is_authenticated:
            return redirect('admin_login')

        if not (request.user.is_staff or request.user.is_superuser):

            messages.error(
                request,
                'Access denied.'
            )

            return redirect('home')

        return view_func(
            request,
            *args,
            **kwargs
        )

    return wrapper


def _is_super_admin(user):
    profile = getattr(user, 'agritech_profile', None)
    return bool(user.is_superuser or (profile and profile.is_super_admin))


def _can_manage_admin(request_user, target_profile):
    if not target_profile.is_super_admin:
        return True
    return _is_super_admin(request_user)


def admin_login_view(request):

    if request.user.is_authenticated and (
        request.user.is_staff or request.user.is_superuser
    ):

        return redirect('admin_dashboard')

    if request.method == 'POST':

        form = AuthenticationForm(
            request,
            data=request.POST
        )

        if form.is_valid():

            user = form.get_user()

            if user.is_staff or user.is_superuser:

                login(
                    request,
                    user
                )

                return redirect('admin_dashboard')

            form.add_error(
                None,
                'Access denied.'
            )

    else:

        form = AuthenticationForm(request)

    form.fields['username'].widget.attrs.update({
        'class': 'form-control',
        'placeholder': 'Enter username'
    })
    form.fields['password'].widget.attrs.update({
        'class': 'form-control',
        'placeholder': 'Enter password'
    })

    return render(
        request,
        'dashboard/admin_login.html',
        {
            'form': form
        }
    )


def admin_logout_view(request):

    logout(request)

    return redirect('admin_login')


@admin_required


def admin_dashboard(request):

    verification_rows = []

    for farmer in Farmer.objects.order_by('-created_at')[:5]:
        verification_rows.append({
            'role': 'Farmer',
            'name': farmer.name,
            'email_verified': farmer.email_verified,
            'phone_verified': farmer.phone_verified,
        })

    for doctor in Doctor.objects.order_by('-registration_date')[:5]:
        verification_rows.append({
            'role': 'Doctor',
            'name': doctor.full_name,
            'email_verified': doctor.email_verified,
            'phone_verified': doctor.phone_verified,
        })

    for consultant in Consultant.objects.order_by('-registration_date')[:5]:
        verification_rows.append({
            'role': 'Consultant',
            'name': consultant.full_name,
            'email_verified': consultant.email_verified,
            'phone_verified': consultant.phone_verified,
        })

    for profile in AdminProfile.objects.select_related('user').order_by('-created_at')[:5]:
        verification_rows.append({
            'role': 'Admin',
            'name': profile.full_name,
            'email_verified': profile.email_verified,
            'phone_verified': profile.phone_verified,
        })

    context = {
        "total_farmers": Farmer.objects.count(),
        "total_doctors": Doctor.objects.count(),
        "online_doctors": Doctor.objects.filter(is_online=True).count(),
        "offline_doctors": Doctor.objects.filter(is_online=False).count(),
        "total_consultants": Consultant.objects.count(),
        "online_consultants": Consultant.objects.filter(is_online=True).count(),
        "offline_consultants": Consultant.objects.filter(is_online=False).count(),
        "total_products": SeedVariety.objects.count(),
        "total_orders": Order.objects.count(),
        "total_machinery": Machinery.objects.count(),
        "total_consultations": ConsultationRequest.objects.count(),
        "recent_farmers": Farmer.objects.order_by("-id")[:5],
        "recent_orders": Order.objects.order_by("-id")[:5],
        # Analytics
        "pending_orders": Order.objects.filter(status="Pending").count(),
        "shipped_orders": Order.objects.filter(status="Shipped").count(),
        "delivered_orders": Order.objects.filter(status="Delivered").count(),
        "confirmed_orders": Order.objects.filter(status="Confirmed").count(),
        "pending_services": ServiceRequest.objects.count(),
        "crop_problems": CropProblem.objects.count(),
        "consultations": ConsultationRequest.objects.count(),
        "identity_change_requests": IdentityChangeRequest.objects.filter(
            status=IdentityChangeRequest.STATUS_PENDING
        ).count(),
        "total_admins": AdminProfile.objects.count(),
        "pending_verifications": (
            Doctor.objects.exclude(verification_status=Doctor.STATUS_VERIFIED).count()
            + Consultant.objects.exclude(verification_status=Consultant.STATUS_VERIFIED).count()
        ),
        "verification_rows": verification_rows,
    }

    return render(
        request,
        "dashboard/admin_dashboard.html",
        context
    )


@admin_required
def content_management(request):

    active_tab = request.GET.get('tab', 'services')
    if active_tab not in CONTENT_MODELS:
        active_tab = 'services'

    editing_type = request.GET.get('type', active_tab)
    editing_pk = request.GET.get('id')
    editing_obj = None

    if editing_type in CONTENT_MODELS and editing_pk:
        model, _, _ = CONTENT_MODELS[editing_type]
        editing_obj = get_object_or_404(model, pk=editing_pk)
        active_tab = editing_type

    forms = {}
    for content_type, (_, form_class, form_key) in CONTENT_MODELS.items():
        instance = editing_obj if editing_type == content_type else None
        forms[form_key] = form_class(instance=instance)

    if request.method == 'POST':
        content_type = request.POST.get('content_type', active_tab)

        if content_type not in CONTENT_MODELS:
            messages.error(request, 'Invalid content type.')
            return redirect('content_management')

        model, form_class, form_key = CONTENT_MODELS[content_type]
        instance = None
        object_id = request.POST.get('object_id')

        if object_id:
            instance = get_object_or_404(model, pk=object_id)

        form = form_class(request.POST, request.FILES, instance=instance)
        forms[form_key] = form

        if form.is_valid():
            form.save()
            messages.success(request, 'Content saved successfully.')
            return redirect(f'{reverse("content_management")}?tab={content_type}')

        active_tab = content_type
        editing_obj = instance

    context = {
        'active_tab': active_tab,
        'editing_type': editing_type,
        'editing_obj': editing_obj,
        'services': ServiceInfo.objects.all(),
        'products': SeedVariety.objects.select_related('crop').all(),
        'consultation_topics': ConsultationTopic.objects.all(),
        'crop_problem_guides': CropProblemGuide.objects.all(),
        'crops': Crop.objects.annotate(product_count=Count('seedvariety')).order_by('name'),
        'crop_form': CropForm(),
        **forms,
    }

    return render(request, 'dashboard/content_management.html', context)


def _serialize_crop(crop):

    product_count = getattr(crop, 'product_count', None)

    if product_count is None:
        product_count = SeedVariety.objects.filter(crop=crop).count()

    return {
        'id': crop.id,
        'name': crop.name,
        'description': crop.description,
        'image_url': crop.image.url if crop.image else '',
        'is_active': crop.is_active,
        'product_count': product_count,
        'label': f"{crop.name} {'(Inactive)' if not crop.is_active else ''}".strip(),
    }


@admin_required
def crop_detail(request, pk):

    crop = get_object_or_404(Crop, pk=pk)

    return JsonResponse({
        'success': True,
        'crop': _serialize_crop(crop),
    })


@admin_required
@require_POST
def crop_save(request):

    crop_id = request.POST.get('crop_id')
    instance = get_object_or_404(Crop, pk=crop_id) if crop_id else None
    form = CropForm(request.POST, request.FILES, instance=instance)

    if form.is_valid():
        crop = form.save()
        return JsonResponse({
            'success': True,
            'crop': _serialize_crop(crop),
            'message': 'Crop saved successfully.',
        })

    return JsonResponse({
        'success': False,
        'errors': form.errors,
    }, status=400)


@admin_required
@require_POST
def crop_toggle_status(request, pk):

    crop = get_object_or_404(Crop, pk=pk)
    crop.is_active = not crop.is_active
    crop.save(update_fields=['is_active'])

    return JsonResponse({
        'success': True,
        'crop': _serialize_crop(crop),
        'message': f"Crop {'activated' if crop.is_active else 'deactivated'} successfully.",
    })


@admin_required
@require_POST
def crop_delete(request, pk):

    crop = get_object_or_404(Crop, pk=pk)
    linked_products = SeedVariety.objects.filter(crop=crop).count()

    if linked_products:
        crop.is_active = False
        crop.save(update_fields=['is_active'])
        return JsonResponse({
            'success': True,
            'crop': _serialize_crop(crop),
            'warning': True,
            'message': 'Crop is linked to products. It has been deactivated instead of deleted.',
        })

    crop.delete()
    return JsonResponse({
        'success': True,
        'deleted': True,
        'crop_id': pk,
        'message': 'Crop deleted successfully.',
    })


@admin_required
def content_toggle_status(request, content_type, pk):

    if content_type not in CONTENT_MODELS:
        messages.error(request, 'Invalid content type.')
        return redirect('content_management')

    model, _, _ = CONTENT_MODELS[content_type]
    obj = get_object_or_404(model, pk=pk)

    if hasattr(obj, 'is_active'):
        obj.is_active = not obj.is_active
        obj.save(update_fields=['is_active'])
        messages.success(request, 'Status updated successfully.')

    return redirect(f'{reverse("content_management")}?tab={content_type}')


@admin_required
def content_delete(request, content_type, pk):

    if content_type not in CONTENT_MODELS:
        messages.error(request, 'Invalid content type.')
        return redirect('content_management')

    model, _, _ = CONTENT_MODELS[content_type]
    obj = get_object_or_404(model, pk=pk)

    if request.method == 'POST':
        obj.delete()
        messages.success(request, 'Content deleted successfully.')

    return redirect(f'{reverse("content_management")}?tab={content_type}')


@admin_required
def admins_management(request):

    search_query = request.GET.get('q', '')
    role_filter = request.GET.get('role', '')
    status_filter = request.GET.get('status', '')

    admins = AdminProfile.objects.select_related('user').all()

    if search_query:
        admins = admins.filter(
            Q(full_name__icontains=search_query) |
            Q(user__username__icontains=search_query) |
            Q(user__email__icontains=search_query)
        )

    if role_filter:
        admins = admins.filter(role=role_filter)

    if status_filter == 'active':
        admins = admins.filter(user__is_active=True)
    elif status_filter == 'inactive':
        admins = admins.filter(user__is_active=False)

    paginator = Paginator(admins, 10)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(
        request,
        'dashboard/admins_management.html',
        {
            'page_obj': page_obj,
            'admins': page_obj.object_list,
            'search_query': search_query,
            'role_filter': role_filter,
            'status_filter': status_filter,
            'role_choices': AdminProfile.ROLE_CHOICES,
            'total_admins': AdminProfile.objects.count(),
            'active_admins': AdminProfile.objects.filter(user__is_active=True).count(),
            'inactive_admins': AdminProfile.objects.filter(user__is_active=False).count(),
        }
    )


@admin_required
def access_code_management(request):

    if not _is_super_admin(request.user):
        messages.error(request, 'Only Super Admins can manage access codes.')
        return redirect('admin_dashboard')

    access_codes = AccessCode.objects.all()
    form = AccessCodeManagementForm(request.POST or None)
    generated_code = None

    if request.method == 'POST' and form.is_valid():
        code_type = form.cleaned_data['code_type']
        action = form.cleaned_data['action']
        code_value = form.cleaned_data['code_value']
        access_code = get_object_or_404(AccessCode, code_type=code_type)

        if action == AccessCodeManagementForm.ACTION_UPDATE:
            generated_code = access_code.update_code(code_value, updated_by=request.user)
            messages.success(request, f'{access_code.code_label} updated successfully.')
        elif action in (AccessCodeManagementForm.ACTION_ROTATE, AccessCodeManagementForm.ACTION_REGENERATE):
            generated_code = access_code.rotate_code(updated_by=request.user)
            messages.success(request, f'{access_code.code_label} rotated successfully.')

    return render(
        request,
        'dashboard/access_code_management.html',
        {
            'access_codes': access_codes,
            'form': form,
            'generated_code': generated_code,
        }
    )


@admin_required
def admin_create(request):

    form = AdminCreateForm(request.POST or None, request.FILES or None, request_user=request.user)

    if request.method == 'POST' and form.is_valid():
        profile = form.save()
        messages.success(request, f'{profile.full_name} was created successfully.')
        return redirect('admins_management')

    return render(request, 'dashboard/admin_form.html', {'form': form, 'title': 'Create Admin'})


@admin_required
def admin_detail(request, pk):

    profile = get_object_or_404(AdminProfile.objects.select_related('user'), pk=pk)

    return render(request, 'dashboard/admin_detail.html', {'profile': profile})


@admin_required
def admin_edit(request, pk):

    profile = get_object_or_404(AdminProfile.objects.select_related('user'), pk=pk)

    if not _can_manage_admin(request.user, profile):
        messages.error(request, 'Normal Admins cannot modify Super Admin permissions.')
        return redirect('admins_management')

    form = AdminProfileForm(
        request.POST or None,
        request.FILES or None,
        instance=profile,
        request_user=request.user,
    )

    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Admin updated successfully.')
        return redirect('admins_management')

    return render(request, 'dashboard/admin_form.html', {'form': form, 'title': 'Edit Admin'})


@admin_required
def admin_delete(request, pk):

    profile = get_object_or_404(AdminProfile.objects.select_related('user'), pk=pk)

    if profile.is_super_admin:
        messages.error(request, 'Super Admin cannot be deleted.')
        return redirect('admins_management')

    if request.method == 'POST':
        user = profile.user
        profile.delete()
        user.delete()
        messages.success(request, 'Admin deleted successfully.')

    return redirect('admins_management')


def farmers_list(request):

    farmers = Farmer.objects.all()

    return render(
        request,
        "dashboard/farmers_list.html",
        {"farmers": farmers}
    )


def products_list(request):

    products = SeedVariety.objects.all()
    total_reviews = Review.objects.count()
    visible_reviews = Review.objects.filter(is_hidden=False)

    return render(
        request,
        "dashboard/products_list.html",
        {
            "products": products,
            "total_reviews": total_reviews,
            "visible_reviews": visible_reviews.count(),
            "hidden_reviews": Review.objects.filter(is_hidden=True).count(),
            "average_rating": visible_reviews.aggregate(avg=Avg('rating'))['avg'],
        }
    )


def machinery_list(request):

    machinery = Machinery.objects.all()

    return render(
        request,
        "dashboard/machinery_list.html",
        {"machinery": machinery}
    )


def services_list(request):

    services = ServiceInfo.objects.all()

    return render(
        request,
        "dashboard/services_list.html",
        {"services": services}
    )


def consultations_list(request):

    consultations = ConsultationRequest.objects.all()
    
    context = {
        "consultations": consultations,
        
        "pending_orders":
        Order.objects.filter(
            status="Pending"
        ).count(),
        
        "pending_services":
        ServiceRequest.objects.filter(
            status="Pending"
        ).count(),
        
        "crop_problems":
        CropProblem.objects.count(),
        
    }

    return render(
        request,
        "dashboard/consultations_list.html",
        context
    )


def add_product(request):

    if request.method == "POST":

        form = ProductForm(
            request.POST,
            request.FILES
        )

        if form.is_valid():

            form.save()

            return redirect(
                "products_list"
            )

    else:

        form = ProductForm()

    return render(
        request,
        "dashboard/add_product.html",
        {
            "form": form
        }
    )


def edit_product(request, pk):

    product = get_object_or_404(
        SeedVariety,
        id=pk
    )

    if request.method == "POST":

        form = ProductForm(
            request.POST,
            request.FILES,
            instance=product
        )

        if form.is_valid():

            form.save()

            return redirect(
                "products_list"
            )

    else:

        form = ProductForm(
            instance=product
        )

    return render(
        request,
        "dashboard/edit_product.html",
        {
            "form": form,
            "product": product
        }
    )


def delete_product(request, pk):

    product = get_object_or_404(
        SeedVariety,
        id=pk
    )

    if request.method == "POST":

        product.delete()

        return redirect(
            "products_list"
        )

    return render(
        request,
        "dashboard/delete_product.html",
        {
            "product": product
        }
    )
def add_machinery(request):

    if request.method == "POST":

        form = MachineryForm(
            request.POST,
            request.FILES
        )

        if form.is_valid():

            form.save()

            return redirect(
                "machinery_list"
            )

    else:

        form = MachineryForm()

    return render(
        request,
        "dashboard/add_machinery.html",
        {
            "form": form
        }
    )
def edit_machinery(request, pk):

    machinery = get_object_or_404(
        Machinery,
        id=pk
    )

    if request.method == "POST":

        form = MachineryForm(
            request.POST,
            request.FILES,
            instance=machinery
        )

        if form.is_valid():

            form.save()

            return redirect(
                "machinery_list"
            )

    else:

        form = MachineryForm(
            instance=machinery
        )

    return render(
        request,
        "dashboard/edit_machinery.html",
        {
            "form": form,
            "machinery": machinery
        }
    )
def delete_machinery(request, pk):

    machinery = get_object_or_404(
        Machinery,
        id=pk
    )

    if request.method == "POST":

        machinery.delete()

        return redirect(
            "machinery_list"
        )

    return render(
        request,
        "dashboard/delete_machinery.html",
        {
            "machinery": machinery
        }
    )
def update_order_status(request, pk):

    order = get_object_or_404(
        Order,
        id=pk
    )

    if request.method == "POST":

        order.status = request.POST.get(
            "status"
        )

        order.save()

    return redirect(
        "orders_list"
    )
    
def farmer_details(request, pk):

    farmer = get_object_or_404(
        Farmer,
        id=pk
    )

    orders = Order.objects.filter(
        farmer=farmer
    )

    consultations = ConsultationRequest.objects.filter(
        farmer=farmer
    )

    bookings = TractorBooking.objects.filter(
        farmer=farmer
    )

    return render(
        request,
        "dashboard/farmer_details.html",
        {
            "farmer": farmer,
            "orders": orders,
            "consultations": consultations,
            "bookings": bookings,
        }
    )


def farmer_orders(request, pk):

    farmer = get_object_or_404(Farmer, pk=pk)
    orders = Order.objects.filter(farmer=farmer).order_by('-id')

    return render(
        request,
        'dashboard/orders_list.html',
        {
            'orders': orders,
            'selected_status': None,
            'pending_count': orders.filter(status='Pending').count(),
            'shipped_count': orders.filter(status='Shipped').count(),
            'delivered_count': orders.filter(status='Delivered').count(),
            'farmer': farmer,
        }
    )


def farmer_consultations(request, pk):

    farmer = get_object_or_404(Farmer, pk=pk)
    consultations = ConsultationRequest.objects.filter(farmer=farmer).order_by('-id')

    return render(
        request,
        'dashboard/consultations_list.html',
        {
            'consultations': consultations,
            'farmer': farmer,
        }
    )


def farmer_bookings(request, pk):

    farmer = get_object_or_404(Farmer, pk=pk)
    bookings = TractorBooking.objects.filter(farmer=farmer).order_by('-id')

    return render(
        request,
        'dashboard/farmer_bookings.html',
        {
            'bookings': bookings,
            'farmer': farmer,
        }
    )
# def update_consultation_status(
#     request,
#     pk
# ):

#     consultation = ConsultationRequest.objects.get(
#         id=pk
#     )

#     consultation.status = request.POST.get(
#         "status"
#     )

#     consultation.save()

#     return redirect(
#         "consultations_list"
#     )
def add_service(request):

    if request.method == "POST":

        ServiceInfo.objects.create(

            title=request.POST.get("title"),

            slug=request.POST.get("slug"),

            short_description=request.POST.get(
                "short_description"
            ),

            full_description=request.POST.get(
                "full_description"
            ),

            benefits=request.POST.get(
                "benefits"
            ),

            why_choose=request.POST.get(
                "why_choose"
            ),

            image=request.FILES.get(
                "image"
            )

        )

        return redirect(
            "services_list"
        )

    return render(
        request,
        "dashboard/service_form.html"
    )
def edit_service(
    request,
    pk
):

    service = ServiceInfo.objects.get(
        id=pk
    )

    if request.method == "POST":

        service.title = request.POST.get(
            "title"
        )

        service.slug = request.POST.get(
            "slug"
        )

        service.short_description = request.POST.get(
            "short_description"
        )

        service.full_description = request.POST.get(
            "full_description"
        )

        service.benefits = request.POST.get(
            "benefits"
        )

        service.why_choose = request.POST.get(
            "why_choose"
        )

        if request.FILES.get(
            "image"
        ):
            service.image = request.FILES.get(
                "image"
            )

        service.save()

        return redirect(
            "services_list"
        )

    return render(

        request,

        "dashboard/service_form.html",

        {

            "service": service

        }

    )
def delete_service(
    request,
    pk
):

    service = ServiceInfo.objects.get(
        id=pk
    )

    service.delete()

    return redirect(
        "services_list"
    )
def update_consultation_status(
    request,
    pk
):

    consultation = ConsultationRequest.objects.get(
        id=pk
    )

    consultation.status = request.POST.get(
        "status"
    )

    consultation.admin_note = request.POST.get(
        "admin_note"
    )

    consultation.save()

    return redirect(
        "consultations_list"
    )
def reply_crop_problem(request, pk):

    problem = get_object_or_404(
        CropProblem,
        id=pk
    )

    if request.method == "POST":

        reply_text = request.POST.get(
            "reply"
        )

        AdminReply.objects.update_or_create(

            crop_problem=problem,

            defaults={
                "reply": reply_text
            }

        )

    return redirect(
        "crop_problems_list"
    )
def crop_problems_list(request):

    problems = CropProblem.objects.all()

    context = {

        "problems": problems,

        "pending_orders":
        Order.objects.filter(
            status="Pending"
        ).count(),

        "pending_services":
        ServiceRequest.objects.count(),

        "consultations":
        ConsultationRequest.objects.count(),

        "crop_problems":
        CropProblem.objects.count(),

    }

    return render(
        request,
        "dashboard/crop_problems_list.html",
        context
    )
def crops_list(request):

    crops = Crop.objects.all()

    return render(
        request,
        "dashboard/crops_list.html",
        {
            "crops": crops
        }
    )


def add_crop(request):

    if request.method == "POST":

        Crop.objects.create(
            name=request.POST.get("name")
        )

        return redirect(
            "crops_list"
        )

    return render(
        request,
        "dashboard/add_crop.html"
    )
def add_crop_ajax(request):

    if request.method == "POST":

        crop_name = request.POST.get("crop_name")

        crop = Crop.objects.create(
            name=crop_name
        )

        return JsonResponse({
            "id": crop.id,
            "name": crop.name
        })

    return JsonResponse({
        "error": True
    })
def site_settings(request):

    settings_obj, created = SiteSettings.objects.get_or_create(id=1)

    if request.method == "POST":

        form = SiteSettingsForm(
            request.POST,
            request.FILES,
            instance=settings_obj
        )

        if form.is_valid():

            form.save()

            return redirect("site_settings")

    else:

        form = SiteSettingsForm(
            instance=settings_obj
        )

    return render(
        request,
        "dashboard/site_settings.html",
        {"form": form}
    )
def why_choose_list(request):

    items = WhyChooseUs.objects.all()

    return render(
        request,
        "dashboard/why_choose_list.html",
        {"items": items}
    )
def add_why_choose(request):

    form = WhyChooseUsForm(
        request.POST or None
    )

    if form.is_valid():

        form.save()

        return redirect("why_choose_list")

    return render(
        request,
        "dashboard/add_why_choose.html",
        {"form": form}
    )
def footer_settings(request):

    footer_obj, created = FooterSettings.objects.get_or_create(id=1)

    if request.method == "POST":

        form = FooterSettingsForm(
            request.POST,
            instance=footer_obj
        )

        if form.is_valid():

            form.save()

            return redirect("footer_settings")

    else:

        form = FooterSettingsForm(
            instance=footer_obj
        )

    return render(
        request,
        "dashboard/footer_settings.html",
        {"form": form}
    )


def role_page_settings(request, pk=None):

    settings_qs = RolePageSettings.objects.all().order_by('role_name')
    role_obj = get_object_or_404(RolePageSettings, pk=pk) if pk else None

    if request.method == "POST":

        form = RolePageSettingsForm(
            request.POST,
            instance=role_obj
        )

        if form.is_valid():

            saved = form.save(commit=False)

            if not saved.slug:
                saved.slug = slugify(saved.role_name)

            saved.save()

            messages.success(
                request,
                'Role page settings saved successfully.'
            )

            return redirect("role_page_settings")

    else:

        form = RolePageSettingsForm(
            instance=role_obj
        )

    return render(
        request,
        "dashboard/role_page_settings.html",
        {
            "form": form,
            "settings_list": settings_qs,
            "editing_setting": role_obj,
        }
    )


def role_page_settings_delete(request, pk):

    role_obj = get_object_or_404(RolePageSettings, pk=pk)

    if request.method == 'POST':
        role_obj.delete()
        messages.success(request, 'Role page settings deleted successfully.')

    return redirect('role_page_settings')
    
def orders_list(request):

    status = request.GET.get("status")

    orders = Order.objects.all().order_by("-id")

    if status:
        orders = orders.filter(status=status)

    context = {

        "orders": orders,

        "selected_status": status,

        "pending_count":
        Order.objects.filter(
            status="Pending"
        ).count(),

        "shipped_count":
        Order.objects.filter(
            status="Shipped"
        ).count(),

        "delivered_count":
        Order.objects.filter(
            status="Delivered"
        ).count(),

    }

    return render(
        request,
        "dashboard/orders_list.html",
        context
    )


def doctors_management(request):

    search_query = request.GET.get('q', '')
    status_filter = request.GET.get('status', '')
    availability_filter = request.GET.get('availability', '')

    doctors = Doctor.objects.all().order_by('-registration_date')

    if search_query:
        doctors = doctors.filter(
            Q(full_name__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(phone__icontains=search_query)
        )

    if status_filter == 'approved':
        doctors = doctors.filter(is_approved=True)
    elif status_filter == 'pending':
        doctors = doctors.filter(is_approved=False)
    elif status_filter in dict(Doctor.VERIFICATION_STATUS_CHOICES):
        doctors = doctors.filter(verification_status=status_filter)

    if availability_filter == 'online':
        doctors = doctors.filter(is_online=True)
    elif availability_filter == 'offline':
        doctors = doctors.filter(is_online=False)

    return render(
        request,
        'dashboard/doctors_management.html',
        {
            'doctors': doctors,
            'search_query': search_query,
            'status_filter': status_filter,
            'availability_filter': availability_filter,
            'verification_status_choices': Doctor.VERIFICATION_STATUS_CHOICES,
        }
    )


@require_POST
def doctor_action(request, pk, action):

    doctor = get_object_or_404(Doctor, pk=pk)

    if action == 'approve':
        doctor.is_approved = True
        doctor.verification_status = Doctor.STATUS_VERIFIED
        messages.success(request, 'Doctor approved successfully.')
    elif action == 'reject':
        doctor.is_approved = False
        doctor.is_active_status = False
        doctor.is_online = False
        doctor.verification_status = Doctor.STATUS_REJECTED
        messages.success(request, 'Doctor rejected successfully.')
    elif action == 'review':
        doctor.verification_status = Doctor.STATUS_UNDER_REVIEW
        messages.success(request, 'Doctor marked under review.')
    elif action == 'request-documents':
        doctor.verification_status = Doctor.STATUS_UNDER_REVIEW
        doctor.verification_note = request.POST.get('note', '').strip()
        messages.success(request, 'Additional documents requested from doctor.')
    elif action == 'activate':
        doctor.is_active_status = True
        messages.success(request, 'Doctor activated successfully.')
    elif action == 'deactivate':
        doctor.is_active_status = False
        doctor.is_online = False
        messages.success(request, 'Doctor deactivated successfully.')

    doctor.verification_note = request.POST.get('note', doctor.verification_note)
    doctor.save()

    if action in {'approve', 'reject', 'review', 'request-documents'}:
        VerificationHistory.objects.create(
            role=VerificationHistory.ROLE_DOCTOR,
            account_id=doctor.id,
            action={
                'approve': VerificationHistory.ACTION_APPROVED,
                'reject': VerificationHistory.ACTION_REJECTED,
                'review': VerificationHistory.ACTION_UNDER_REVIEW,
                'request-documents': VerificationHistory.ACTION_REQUESTED_DOCUMENTS,
            }[action],
            note=request.POST.get('note', ''),
            performed_by=request.user,
        )

    return redirect('doctors_management')


def doctor_detail(request, pk):

    doctor = get_object_or_404(Doctor, pk=pk)
    history = VerificationHistory.objects.filter(role=VerificationHistory.ROLE_DOCTOR, account_id=doctor.id)

    return render(
        request,
        'dashboard/verification_detail.html',
        {
            'account': doctor,
            'role_label': 'Doctor',
            'history': history,
            'action_url_name': 'doctor_action',
        }
    )


def consultant_management(request):

    search_query = request.GET.get('q', '')
    status_filter = request.GET.get('status', '')
    availability_filter = request.GET.get('availability', '')

    consultants = Consultant.objects.all().order_by('-registration_date')

    if search_query:
        consultants = consultants.filter(
            Q(full_name__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(phone__icontains=search_query)
        )

    if status_filter == 'approved':
        consultants = consultants.filter(is_approved=True)
    elif status_filter == 'pending':
        consultants = consultants.filter(is_approved=False)
    elif status_filter in dict(Consultant.VERIFICATION_STATUS_CHOICES):
        consultants = consultants.filter(verification_status=status_filter)

    if availability_filter == 'online':
        consultants = consultants.filter(is_online=True)
    elif availability_filter == 'offline':
        consultants = consultants.filter(is_online=False)

    return render(
        request,
        'dashboard/consultants_management.html',
        {
            'consultants': consultants,
            'search_query': search_query,
            'status_filter': status_filter,
            'availability_filter': availability_filter,
            'verification_status_choices': Consultant.VERIFICATION_STATUS_CHOICES,
        }
    )


@require_POST
def consultant_action(request, pk, action):

    consultant = get_object_or_404(Consultant, pk=pk)

    if action == 'approve':
        consultant.is_approved = True
        consultant.verification_status = Consultant.STATUS_VERIFIED
        messages.success(request, 'Consultant approved successfully.')
    elif action == 'reject':
        consultant.is_approved = False
        consultant.is_active_status = False
        consultant.is_online = False
        consultant.verification_status = Consultant.STATUS_REJECTED
        messages.success(request, 'Consultant rejected successfully.')
    elif action == 'review':
        consultant.verification_status = Consultant.STATUS_UNDER_REVIEW
        messages.success(request, 'Consultant marked under review.')
    elif action == 'request-documents':
        consultant.verification_status = Consultant.STATUS_UNDER_REVIEW
        consultant.verification_note = request.POST.get('note', '').strip()
        messages.success(request, 'Additional documents requested from consultant.')
    elif action == 'activate':
        consultant.is_active_status = True
        messages.success(request, 'Consultant activated successfully.')
    elif action == 'deactivate':
        consultant.is_active_status = False
        consultant.is_online = False
        messages.success(request, 'Consultant deactivated successfully.')

    consultant.verification_note = request.POST.get('note', consultant.verification_note)
    consultant.save()

    if action in {'approve', 'reject', 'review', 'request-documents'}:
        VerificationHistory.objects.create(
            role=VerificationHistory.ROLE_CONSULTANT,
            account_id=consultant.id,
            action={
                'approve': VerificationHistory.ACTION_APPROVED,
                'reject': VerificationHistory.ACTION_REJECTED,
                'review': VerificationHistory.ACTION_UNDER_REVIEW,
                'request-documents': VerificationHistory.ACTION_REQUESTED_DOCUMENTS,
            }[action],
            note=request.POST.get('note', ''),
            performed_by=request.user,
        )

    return redirect('consultant_management')


def consultant_detail(request, pk):

    consultant = get_object_or_404(Consultant, pk=pk)
    history = VerificationHistory.objects.filter(role=VerificationHistory.ROLE_CONSULTANT, account_id=consultant.id)

    return render(
        request,
        'dashboard/verification_detail.html',
        {
            'account': consultant,
            'role_label': 'Consultant',
            'history': history,
            'action_url_name': 'consultant_action',
        }
    )


@admin_required
def registration_fields(request, pk=None):

    field_obj = get_object_or_404(RegistrationField, pk=pk) if pk else None
    form = RegistrationFieldForm(request.POST or None, instance=field_obj)

    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Registration field saved successfully.')
        return redirect('registration_fields')

    return render(
        request,
        'dashboard/registration_fields.html',
        {
            'form': form,
            'fields': RegistrationField.objects.all(),
            'editing_field': field_obj,
        }
    )


@admin_required
def registration_field_delete(request, pk):

    field_obj = get_object_or_404(RegistrationField, pk=pk)

    if request.method == 'POST':
        field_obj.delete()
        messages.success(request, 'Registration field deleted successfully.')

    return redirect('registration_fields')


@admin_required
def roles_management(request, pk=None):

    role_obj = get_object_or_404(Role, pk=pk) if pk else None
    form = RoleManagementForm(request.POST or None, instance=role_obj)

    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Role saved successfully.')
        return redirect('roles_management')

    return render(
        request,
        'dashboard/roles_management.html',
        {
            'form': form,
            'roles': Role.objects.all(),
            'editing_role': role_obj,
        }
    )


@admin_required
def role_delete(request, pk):

    role_obj = get_object_or_404(Role, pk=pk)

    if role_obj.is_system:
        messages.error(request, 'System roles cannot be deleted.')
        return redirect('roles_management')

    if request.method == 'POST':
        role_obj.delete()
        messages.success(request, 'Role deleted successfully.')

    return redirect('roles_management')


@admin_required
def delete_farmer(request, pk):

    farmer = get_object_or_404(Farmer, pk=pk)

    if request.method != 'POST':
        return redirect('farmers_list')

    farmer_id = farmer.id
    farmer.delete()

    if request.session.get('farmer_id') == farmer_id:
        for session_key in ('farmer_id', 'farmer_name', 'profile_picture', 'user_role'):
            request.session.pop(session_key, None)

    messages.success(request, 'Farmer deleted permanently.')
    return redirect('farmers_list')


@admin_required
def delete_doctor(request, pk):

    doctor = get_object_or_404(Doctor, pk=pk)

    if request.method != 'POST':
        return redirect('doctors_management')

    doctor_id = doctor.id
    doctor.delete()

    if request.session.get('doctor_id') == doctor_id:
        for session_key in ('doctor_id', 'doctor_name', 'doctor_photo', 'user_role'):
            request.session.pop(session_key, None)

    messages.success(request, 'Doctor deleted permanently.')
    return redirect('doctors_management')


@admin_required
def delete_consultant(request, pk):

    consultant = get_object_or_404(Consultant, pk=pk)

    if request.method != 'POST':
        return redirect('consultant_management')

    consultant_id = consultant.id
    consultant.delete()

    if request.session.get('consultant_id') == consultant_id:
        for session_key in ('consultant_id', 'consultant_name', 'consultant_photo', 'user_role'):
            request.session.pop(session_key, None)

    messages.success(request, 'Consultant deleted permanently.')
    return redirect('consultant_management')


@admin_required
def admin_profile(request):

    profile = getattr(request.user, 'agritech_profile', None)
    password_form = PasswordChangeForm(request.POST or None)

    if request.method == 'POST' and request.POST.get('change_password'):

        if password_form.is_valid():

            current_password = password_form.cleaned_data['current_password']
            new_password = password_form.cleaned_data['new_password']

            if not request.user.check_password(current_password):
                password_form.add_error('current_password', 'Current password is incorrect.')
            else:
                request.user.set_password(new_password)
                request.user.save(update_fields=['password'])
                update_session_auth_hash(request, request.user)
                messages.success(request, 'Password changed successfully.')
                return redirect('admin_profile')

    return render(
        request,
        'dashboard/admin_profile.html',
        {
            'profile': profile,
            'password_form': password_form,
        }
    )


def product_reviews_management(request):

    search_query = request.GET.get('q', '')
    status_filter = request.GET.get('filter', request.GET.get('status', 'all'))
    product_filter = request.GET.get('product', '')

    reviews = Review.objects.select_related('product', 'farmer').all()

    if search_query:
        reviews = reviews.filter(
            Q(name__icontains=search_query) |
            Q(review_text__icontains=search_query) |
            Q(product__name__icontains=search_query)
        )

    if status_filter == 'visible':
        reviews = reviews.filter(is_hidden=False)
    elif status_filter == 'hidden':
        reviews = reviews.filter(is_hidden=True)

    if product_filter:
        reviews = reviews.filter(product_id=product_filter)

    visible_reviews = Review.objects.filter(is_hidden=False)

    return render(
        request,
        'dashboard/product_reviews_management.html',
        {
            'reviews': reviews.order_by('-created_at'),
            'products': SeedVariety.objects.all().order_by('name'),
            'search_query': search_query,
            'status_filter': status_filter,
            'product_filter': product_filter,
            'total_reviews': Review.objects.count(),
            'visible_reviews': visible_reviews.count(),
            'hidden_reviews': Review.objects.filter(is_hidden=True).count(),
            'average_rating': visible_reviews.aggregate(avg=Avg('rating'))['avg'],
        }
    )


def product_review_action(request, pk, action):

    review = get_object_or_404(Review, pk=pk)

    if action not in {'hide', 'unhide', 'delete'}:
        return redirect('product_reviews_management')

    if action == 'hide':
        review.is_hidden = True
        messages.success(request, 'Review hidden successfully.')
    elif action == 'unhide':
        review.is_hidden = False
        messages.success(request, 'Review restored successfully.')
    elif action == 'delete':
        review.delete()
        messages.success(request, 'Review deleted permanently.')
        return redirect('product_reviews_management')

    review.save()
    return redirect('product_reviews_management')


def product_reviews_analytics(request):

    reviews = Review.objects.select_related('product').all()
    visible_reviews = reviews.filter(is_hidden=False)

    rating_breakdown = [
        {
            'rating': rating,
            'count': visible_reviews.filter(rating=rating).count(),
        }
        for rating in range(5, 0, -1)
    ]

    product_summary = (
        visible_reviews.values('product__name')
        .annotate(total=Count('id'), average=Avg('rating'))
        .order_by('-total', 'product__name')[:8]
    )

    return render(
        request,
        'dashboard/product_reviews_analytics.html',
        {
            'total_reviews': reviews.count(),
            'visible_reviews': visible_reviews.count(),
            'hidden_reviews': reviews.filter(is_hidden=True).count(),
            'average_rating': visible_reviews.aggregate(avg=Avg('rating'))['avg'],
            'rating_breakdown': rating_breakdown,
            'product_summary': product_summary,
        }
    )


def identity_change_requests(request):

    doctor_requests = IdentityChangeRequest.objects.filter(
        role=IdentityChangeRequest.ROLE_DOCTOR
    ).order_by('-created_at')

    consultant_requests = IdentityChangeRequest.objects.filter(
        role=IdentityChangeRequest.ROLE_CONSULTANT
    ).order_by('-created_at')

    return render(
        request,
        'dashboard/identity_change_requests.html',
        {
            'doctor_requests': doctor_requests,
            'consultant_requests': consultant_requests,
        }
    )


def identity_change_request_action(request, pk, action):

    change_request = get_object_or_404(IdentityChangeRequest, pk=pk)

    if action not in {'approve', 'reject'}:
        return redirect('identity_change_requests')

    change_request.status = IdentityChangeRequest.STATUS_APPROVED if action == 'approve' else IdentityChangeRequest.STATUS_REJECTED
    change_request.resolved_at = timezone.now()

    model = Doctor if change_request.role == IdentityChangeRequest.ROLE_DOCTOR else Consultant
    account = model.objects.filter(id=change_request.account_id).first()

    if account:
        account.identity_edit_allowed = action == 'approve'
        account.save(update_fields=['identity_edit_allowed'])

    messages.success(
        request,
        f'Identity change request {"approved" if action == "approve" else "rejected"}.'
    )
    change_request.save()
    return redirect('identity_change_requests')
