from functools import wraps

from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render
from django.shortcuts import get_object_or_404, redirect
from accounts.models import Farmer
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
from django.db.models import Count
from services.models import ServiceRequest
from products.models import Crop
from django.http import JsonResponse


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

    context = {
        "total_farmers": Farmer.objects.count(),
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

    return render(
        request,
        "dashboard/products_list.html",
        {"products": products}
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
    
def orders_list(request):

    orders = Order.objects.all()

    context = {

        "orders": orders,

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