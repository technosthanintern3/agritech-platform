from django.shortcuts import render, redirect

from .forms import FarmerRegistrationForm
from .login_forms import LoginForm
from .models import Farmer

from consultation.models import ConsultationRequest
from machinery.models import TractorBooking
from services.models import ServiceRequest
from farmer_support.models import CropProblem
from .forms import EditProfileForm


def register(request):

    success = False

    if request.method == 'POST':

        form = FarmerRegistrationForm(
            request.POST
        )

        if form.is_valid():

            form.save()

            success = True

            form = FarmerRegistrationForm()

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


def login_view(request):

    error = None

    if request.method == 'POST':

        form = LoginForm(request.POST)

        if form.is_valid():

            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            try:

                farmer = Farmer.objects.get(
                    email=email,
                    password=password
                )

                request.session['farmer_id'] = farmer.id
                request.session['farmer_name'] = farmer.name
                if farmer.profile_picture:
                    request.session['profile_picture'] = farmer.profile_picture.url
                else:
                    request.session['profile_picture'] = ''

                return redirect(
                    'dashboard'
                )

            except Farmer.DoesNotExist:

                error = "Invalid Email or Password"

    else:

        form = LoginForm()

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
  
    
def edit_profile(request):

    farmer_id = request.session.get('farmer_id')

    if not farmer_id:
        return redirect('login')

    farmer = Farmer.objects.get(id=farmer_id)

    if request.method == 'POST':

        form = EditProfileForm(
            request.POST,
            request.FILES,
            instance=farmer
        )

        if form.is_valid():

            farmer = form.save()

            # Update session data
            request.session['farmer_name'] = farmer.name

            if farmer.profile_picture:
                request.session['profile_picture'] = farmer.profile_picture.url
            else:
                request.session['profile_picture'] = ''

            return redirect('dashboard')

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