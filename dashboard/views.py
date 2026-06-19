from functools import wraps

from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from accounts.models import Farmer, Doctor, Consultant, IdentityChangeRequest, AdminProfile
from products.models import SeedVariety
from dashboard.forms import ProductForm
from machinery.models import Machinery, TractorBooking
from dashboard.forms import MachineryForm
from orders.models import Order
from consultation.models import ConsultationRequest
from services.models import ServiceInfo
from farmer_support.models import CropProblem
from farmer_support.models import (
    CropProblem,
    AdminReply
)
from django.db.models import Count, Avg
from django.db.models import Q
from services.models import ServiceRequest
from products.models import Crop, Review, SeedVariety
from django.http import JsonResponse
from django.utils.text import slugify
from company.models import SiteSettings
from accounts.models import (
    SiteSettings,
    WhyChooseUs,
    FooterSettings,
    RolePageSettings
)

from dashboard.forms import (
    SiteSettingsForm,
    WhyChooseUsForm,
    FooterSettingsForm,
    RolePageSettingsForm
)


User = get_user_model()


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
        "verification_rows": verification_rows,
    }

    return render(
        request,
        "dashboard/admin_dashboard.html",
        context
    )


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
        }
    )


def doctor_action(request, pk, action):

    doctor = get_object_or_404(Doctor, pk=pk)

    if action == 'approve':
        doctor.is_approved = True
        messages.success(request, 'Doctor approved successfully.')
    elif action == 'reject':
        doctor.is_approved = False
        doctor.is_active_status = False
        doctor.is_online = False
        messages.success(request, 'Doctor rejected successfully.')
    elif action == 'activate':
        doctor.is_active_status = True
        messages.success(request, 'Doctor activated successfully.')
    elif action == 'deactivate':
        doctor.is_active_status = False
        doctor.is_online = False
        messages.success(request, 'Doctor deactivated successfully.')

    doctor.save()

    return redirect('doctors_management')


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
        }
    )


def consultant_action(request, pk, action):

    consultant = get_object_or_404(Consultant, pk=pk)

    if action == 'approve':
        consultant.is_approved = True
        messages.success(request, 'Consultant approved successfully.')
    elif action == 'reject':
        consultant.is_approved = False
        consultant.is_active_status = False
        consultant.is_online = False
        messages.success(request, 'Consultant rejected successfully.')
    elif action == 'activate':
        consultant.is_active_status = True
        messages.success(request, 'Consultant activated successfully.')
    elif action == 'deactivate':
        consultant.is_active_status = False
        consultant.is_online = False
        messages.success(request, 'Consultant deactivated successfully.')

    consultant.save()

    return redirect('consultant_management')


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
