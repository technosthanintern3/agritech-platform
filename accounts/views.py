from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, get_user_model, login as auth_login
from django.utils import timezone
import re

from .forms import (
    FarmerRegistrationForm,
    DoctorRegistrationForm,
    ConsultantRegistrationForm,
    CommonLoginForm,
)
from .models import Farmer, Doctor, Consultant

from consultation.models import ConsultationRequest
from machinery.models import TractorBooking
from services.models import ServiceRequest
from farmer_support.models import CropProblem
from .forms import EditProfileForm


User = get_user_model()


def choose_role(request):
    return render(request, 'accounts/choose_role.html')


def _set_farmer_session(request, farmer):

    request.session['user_role'] = 'farmer'
    request.session['farmer_id'] = farmer.id
    request.session['farmer_name'] = farmer.name
    request.session['profile_picture'] = (
        farmer.profile_picture.url if farmer.profile_picture else ''
    )


def _set_doctor_session(request, doctor):

    doctor.is_active_status = True
    doctor.last_login_time = timezone.now()
    doctor.save(update_fields=['is_active_status', 'last_login_time'])

    request.session['user_role'] = 'doctor'
    request.session['doctor_id'] = doctor.id
    request.session['doctor_name'] = doctor.full_name
    request.session['doctor_photo'] = (
        doctor.profile_photo.url if doctor.profile_photo else ''
    )


def _set_consultant_session(request, consultant):

    consultant.is_active_status = True
    consultant.last_login_time = timezone.now()
    consultant.save(update_fields=['is_active_status', 'last_login_time'])

    request.session['user_role'] = 'consultant'
    request.session['consultant_id'] = consultant.id
    request.session['consultant_name'] = consultant.full_name
    request.session['consultant_photo'] = (
        consultant.profile_photo.url if consultant.profile_photo else ''
    )


def _set_admin_session(request, user):

    request.session['user_role'] = 'admin'
    request.session['admin_id'] = user.id
    request.session['admin_name'] = user.get_full_name() or user.username


def _try_common_login(email, password):

    farmer = Farmer.objects.filter(email=email, password=password).first()
    if farmer:
        return 'farmer', farmer

    doctor = Doctor.objects.filter(
        email=email,
        password=password,
        is_approved=True,
        is_active_status=True,
    ).first()
    if doctor:
        return 'doctor', doctor

    consultant = Consultant.objects.filter(
        email=email,
        password=password,
        is_approved=True,
        is_active_status=True,
    ).first()
    if consultant:
        return 'consultant', consultant

    admin_user = User.objects.filter(
        email=email,
        is_staff=True,
    ).first()

    if not admin_user:
        admin_user = User.objects.filter(
            username=email,
            is_staff=True,
        ).first()

    if admin_user and authenticate(
        username=admin_user.username,
        password=password
    ):
        return 'admin', admin_user

    return None, None


def register(request):

    success = False

    if request.method == 'POST':

        form = FarmerRegistrationForm(
            request.POST
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                'Registration successful. Please log in to continue.'
            )

            return redirect('home')

    else:

        form = FarmerRegistrationForm()

    return render(
        request,
        'accounts/register.html',
        {
            'form': form,
            'success': success
        }
    )


def doctor_register(request):

    success = False

    if request.method == 'POST':

        form = DoctorRegistrationForm(request.POST, request.FILES)

        if form.is_valid():

            doctor = form.save(commit=False)
            doctor.is_active_status = False
            doctor.is_approved = False
            doctor.save()

            messages.success(
                request,
                'Doctor registration submitted. Wait for admin approval.'
            )

            return redirect('choose_role')

    else:

        form = DoctorRegistrationForm()

    return render(
        request,
        'accounts/doctor_register.html',
        {
            'form': form,
            'success': success
        }
    )


def consultant_register(request):

    success = False

    if request.method == 'POST':

        form = ConsultantRegistrationForm(request.POST, request.FILES)

        if form.is_valid():

            consultant = form.save(commit=False)
            consultant.is_active_status = False
            consultant.is_approved = False
            consultant.save()

            messages.success(
                request,
                'Consultant registration submitted. Wait for admin approval.'
            )

            return redirect('choose_role')

    else:

        form = ConsultantRegistrationForm()

    return render(
        request,
        'accounts/consultant_register.html',
        {
            'form': form,
            'success': success
        }
    )


def login_view(request):

    error = None

    if request.method == 'POST':

        form = CommonLoginForm(request.POST)

        if form.is_valid():

            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            role, user = _try_common_login(email, password)

            if role == 'farmer':
                _set_farmer_session(request, user)
                return redirect('dashboard')

            if role == 'doctor':
                _set_doctor_session(request, user)
                return redirect('doctor_dashboard')

            if role == 'consultant':
                _set_consultant_session(request, user)
                return redirect('consultant_dashboard')

            if role == 'admin':
                auth_login(request, user)
                _set_admin_session(request, user)
                return redirect('admin_dashboard')

            error = "Invalid Email or Password"

    else:

        form = CommonLoginForm()

    return render(
        request,
        'accounts/login.html',
        {
            'form': form,
            'error': error
        }
    )


def dashboard(request):

    farmer_id = request.session.get(
        'farmer_id'
    )

    if not farmer_id:

        return redirect('login')

    farmer = Farmer.objects.get(
        id=farmer_id
    )

    consultations = ConsultationRequest.objects.filter(
        farmer_id=farmer_id
    ).count()

    bookings = TractorBooking.objects.filter(
        farmer_id=farmer_id
    ).count()

    services = ServiceRequest.objects.filter(
        farmer_id=farmer_id
    ).count()

    problems = CropProblem.objects.filter(
        farmer_id=farmer_id
    ).count()

    return render(
        request,
        'accounts/dashboard.html',
        {
            'farmer': farmer,
            'consultations': consultations,
            'bookings': bookings,
            'services': services,
            'problems': problems
        }
    )


def logout_view(request):

    request.session.flush()

    return redirect('home')
  
    
# def edit_profile(request):

#     farmer_id = request.session.get('farmer_id')

#     if not farmer_id:
#         return redirect('login')

#     farmer = Farmer.objects.get(id=farmer_id)

#     if request.method == 'POST':

#         form = EditProfileForm(
#             request.POST,
#             request.FILES,
#             instance=farmer
#         )

#         if form.is_valid():

#             farmer = form.save()

#             # Update session data
#             request.session['farmer_name'] = farmer.name

#             if farmer.profile_picture:
#                 request.session['profile_picture'] = farmer.profile_picture.url
#             else:
#                 request.session['profile_picture'] = ''

#             return redirect('dashboard')

#     else:

#         form = EditProfileForm(
#             instance=farmer
#         )

#     return render(
#         request,
#         'accounts/edit_profile.html',
#         {
#             'form': form
#         }
#     )
def edit_profile(request):

    farmer_id = request.session.get('farmer_id')

    if not farmer_id:
        return redirect('login')

    farmer = Farmer.objects.get(id=farmer_id)

    if request.method == 'POST':

        # CHANGE PASSWORD SECTION
        if request.POST.get('change_password'):

            current_password = request.POST.get(
                'current_password'
            )

            new_password = request.POST.get(
                'new_password'
            )

            confirm_password = request.POST.get(
                'confirm_password'
            )

            if current_password != farmer.password:

                return render(
                    request,
                    'accounts/edit_profile.html',
                    {
                        'form': EditProfileForm(instance=farmer),
                        'password_error': 'Current password is incorrect.'
                    }
                )

            if new_password != confirm_password:

                return render(
                    request,
                    'accounts/edit_profile.html',
                    {
                        'form': EditProfileForm(instance=farmer),
                        'password_error': 'New passwords do not match.'
                    }
                )

            farmer.password = new_password
            farmer.save()

            return redirect('login')

        # PROFILE UPDATE SECTION

        form = EditProfileForm(
            request.POST,
            request.FILES,
            instance=farmer
        )

        if form.is_valid():

            farmer = form.save()

            request.session['farmer_name'] = farmer.name

            if farmer.profile_picture:
                request.session['profile_picture'] = farmer.profile_picture.url
            else:
                request.session['profile_picture'] = ''

            return redirect('dashboard')

        else:

            print(form.errors)

    else:

        form = EditProfileForm(
            instance=farmer
        )

    return render(
        request,
        'accounts/edit_profile.html',
        {
            'form': form
        }
    )
    
def change_password(request):

    farmer_id = request.session.get('farmer_id')

    if not farmer_id:
        return redirect('login')

    farmer = Farmer.objects.get(id=farmer_id)

    error = None

    if request.method == 'POST':

        current_password = request.POST.get(
            'current_password'
        )

        new_password = request.POST.get(
            'new_password'
        )

        confirm_password = request.POST.get(
            'confirm_password'
        )

        if current_password != farmer.password:

            error = "Current password is incorrect."
            
        elif len(new_password) < 8:
            error = "Password must be at least 8 characters long."
            
        elif not re.search(r'[A-Z]', new_password):
            error = "Password must contain at least one uppercase letter."
            
        elif not re.search(r'[a-z]', new_password):
            error = "Password must contain at least one lowercase letter."
            
        elif not re.search(r'[0-9]', new_password):
            error = "Password must contain at least one number."
            
        elif not re.search(r'[@$!%*?&#]', new_password):
            error = "Password must contain at least one special character."
         
        elif new_password != confirm_password:

            error = "Passwords do not match."

        else:

            farmer.password = new_password
            farmer.save()
            # Logout useer after password change
            request.session.flush()

            return redirect('login')

    return render(
        request,
        'accounts/change_password.html',
        {
            'error': error
        }
    )