from django.apps import apps
from django.conf import settings
from django.contrib.auth.hashers import check_password, make_password
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, get_user_model, login as auth_login
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.urls import NoReverseMatch, reverse
from django.core.mail import send_mail
from django.utils.dateparse import parse_datetime
from django.utils import timezone as dj_timezone
from datetime import timedelta
import secrets
import re

from .forms import (
    FarmerRegistrationForm,
    DoctorRegistrationForm,
    ConsultantRegistrationForm,
    CommonLoginForm,
    DoctorProfileForm,
    ConsultantProfileForm,
    AdminRegistrationForm,
    OTPVerificationForm,
)
from .models import (
    Farmer,
    Doctor,
    Consultant,
    Role,
    IdentityChangeRequest,
    RegistrationOTP,
    AdminProfile,
)

from consultation.models import ConsultationRequest
from machinery.models import TractorBooking
from services.models import ServiceRequest
from farmer_support.models import CropProblem
from .forms import EditProfileForm
from agritech.utils import doctor_required, consultant_required


User = get_user_model()

_ROLE_MODEL_EXCLUDES = {
    'SiteSettings',
    'WhyChooseUs',
    'FooterSettings',
    'RolePageSettings',
}


def _registration_roles():

    Role.objects.get_or_create(
        slug='admin',
        defaults={
            'name': 'Admin',
            'description': 'Create and manage platform administrators.',
            'icon': '🛡️',
            'register_url': 'admin_register',
            'dashboard_url': 'admin_dashboard',
            'is_active': True,
        }
    )

    roles = list(Role.objects.filter(is_active=True))

    for role in roles:

        register_url = role.register_url

        if not register_url.startswith(('/', 'http://', 'https://')):
            try:
                register_url = reverse(register_url)
            except NoReverseMatch:
                pass

        role.resolved_register_url = register_url

    return roles


def _account_password_matches(stored_password, raw_password):

    if not stored_password:
        return False

    if stored_password == raw_password:
        return True

    try:
        return check_password(raw_password, stored_password)
    except Exception:
        return False


def _generate_otp():

    return f'{secrets.randbelow(1000000):06d}'


def _send_otp_email(email_address, role_label, email_otp, phone_otp):

    send_mail(
        subject=f'{role_label} registration OTP',
        message=(
            f'Your {role_label} email OTP is {email_otp}. '\
            f'Your mobile OTP is {phone_otp}. '\
            'These codes expire in 5 minutes.'
        ),
        from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', None),
        recipient_list=[email_address],
        fail_silently=True,
    )


def _clean_registration_payload(cleaned_data):

    payload = dict(cleaned_data)
    payload.pop('confirm_password', None)
    payload.pop('admin_code', None)
    payload.pop('profile_photo', None)
    payload.pop('identity_photo_upload', None)
    return payload


def _registration_redirect(role):

    route_map = {
        'farmer': 'register',
        'doctor': 'doctor_register',
        'consultant': 'consultant_register',
        'admin': 'admin_register',
    }

    return route_map.get(role, 'choose_role')


def _admin_profile_verified(user):

    profile = getattr(user, 'agritech_profile', None)

    if profile is None:
        return True

    return profile.email_verified and profile.phone_verified


def choose_role(request):
    return render(
        request,
        'accounts/choose_role.html',
        {
            'flow_type': 'register',
            'roles': _registration_roles(),
        }
    )


def _set_farmer_session(request, farmer):

    request.session['user_role'] = 'farmer'
    request.session['farmer_id'] = farmer.id
    request.session['farmer_name'] = farmer.name
    request.session['profile_picture'] = (
        farmer.profile_picture.url if farmer.profile_picture else ''
    )


def _set_doctor_session(request, doctor):

    doctor.is_active_status = True
    doctor.is_online = True
    doctor.last_seen = timezone.now()
    doctor.last_login_time = timezone.now()
    doctor.save(update_fields=[
        'is_active_status', 'is_online', 'last_seen', 'last_login_time'
    ])

    request.session['user_role'] = 'doctor'
    request.session['doctor_id'] = doctor.id
    request.session['doctor_name'] = doctor.full_name
    request.session['doctor_photo'] = (
        doctor.profile_photo.url if doctor.profile_photo else ''
    )


def _set_consultant_session(request, consultant):

    consultant.is_active_status = True
    consultant.is_online = True
    consultant.last_seen = timezone.now()
    consultant.last_login_time = timezone.now()
    consultant.save(update_fields=[
        'is_active_status', 'is_online', 'last_seen', 'last_login_time'
    ])

    request.session['user_role'] = 'consultant'
    request.session['consultant_id'] = consultant.id
    request.session['consultant_name'] = consultant.full_name
    request.session['consultant_photo'] = (
        consultant.profile_photo.url if consultant.profile_photo else ''
    )


def _set_admin_session(request, user):

    request.session['user_role'] = 'admin'
    request.session['account_role'] = 'admin'
    request.session['admin_id'] = user.id
    request.session['admin_name'] = user.get_full_name() or user.username


def _mark_role_online(account):

    now = timezone.now()

    account.is_online = True
    account.last_seen = now

    update_fields = ['is_online', 'last_seen']

    if hasattr(account, 'is_active_status'):

        account.is_active_status = True
        update_fields.append('is_active_status')

    if hasattr(account, 'last_login_time'):

        account.last_login_time = now
        update_fields.append('last_login_time')

    account.save(update_fields=update_fields)


def _mark_role_offline(account):

    now = timezone.now()

    account.is_online = False
    account.last_seen = now

    update_fields = ['is_online', 'last_seen']

    if hasattr(account, 'is_active_status'):

        account.is_active_status = False
        update_fields.append('is_active_status')

    account.save(update_fields=update_fields)


def _display_name_for_account(account):

    for field_name in ('full_name', 'name', 'username', 'email'):

        value = getattr(account, field_name, None)

        if value:
            return value

    return str(account)


def _account_photo_url(account):

    for field_name in (
        'profile_photo',
        'profile_picture',
        'photo',
        'image',
    ):

        image_field = getattr(account, field_name, None)

        if image_field:

            try:
                return image_field.url
            except ValueError:
                return ''

    return ''


def _set_account_session(request, role_slug, account):

    display_name = _display_name_for_account(account)
    photo_url = _account_photo_url(account)

    if role_slug in {'doctor', 'consultant'}:

        _mark_role_online(account)

    request.session['user_role'] = role_slug
    request.session['account_role'] = role_slug
    request.session['account_id'] = account.id
    request.session['account_name'] = display_name
    request.session['account_photo'] = photo_url

    role_prefix = f'{role_slug}_'
    request.session[f'{role_prefix}id'] = account.id
    request.session[f'{role_prefix}name'] = display_name

    if role_slug in {'doctor', 'consultant'}:
        now = timezone.now()
        account.is_online = True
        account.last_seen = now
        account.last_login_time = now
        account.save(update_fields=['is_online', 'last_seen', 'last_login_time'])

    if photo_url:
        request.session[f'{role_prefix}photo'] = photo_url

    if role_slug == 'farmer':

        request.session['farmer_name'] = display_name
        request.session['profile_picture'] = photo_url

    elif role_slug == 'doctor':

        request.session['doctor_name'] = display_name
        request.session['doctor_photo'] = photo_url

    elif role_slug == 'consultant':

        request.session['consultant_name'] = display_name
        request.session['consultant_photo'] = photo_url


def _account_models_for_login():

    for model in apps.get_app_config('accounts').get_models():

        if model.__name__ in _ROLE_MODEL_EXCLUDES:
            continue

        field_names = {field.name for field in model._meta.fields}

        if {'email', 'password'}.issubset(field_names):
            yield model


def _dashboard_url_for_account(role_slug, account):

    dashboard_url_name = getattr(
        account,
        'dashboard_url_name',
        None
    )

    if dashboard_url_name:

        try:
            return reverse(dashboard_url_name)
        except NoReverseMatch:
            pass

    candidate_names = []

    if role_slug == 'farmer':
        candidate_names.extend(['dashboard', 'farmer_dashboard'])
    else:
        candidate_names.extend([
            f'{role_slug}_dashboard',
            f'{account.__class__.__name__.lower()}_dashboard',
        ])

    for url_name in candidate_names:

        try:
            return reverse(url_name)
        except NoReverseMatch:
            continue

    return None


def _try_common_login(email, password):

    for model in _account_models_for_login():

        field_names = {field.name for field in model._meta.fields}
        filters = {'email': email}

        if 'is_approved' in field_names:
            filters['is_approved'] = True

        if 'is_active_status' in field_names:
            filters['is_active_status'] = True

        if 'email_verified' in field_names:
            filters['email_verified'] = True

        if 'phone_verified' in field_names:
            filters['phone_verified'] = True

        account = model.objects.filter(**filters).first()

        if account and not _account_password_matches(account.password, password):
            account = None

        if account:

            role_slug = getattr(
                account,
                'role_slug',
                account.__class__.__name__.lower()
            )

            return role_slug, account

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
        if not _admin_profile_verified(admin_user):
            return None, None
        return 'admin', admin_user

    return None, None


def register(request, role=None):

    if role is None:
        return render(
            request,
            'accounts/choose_role.html',
            {
                'flow_type': 'register',
                'roles': _registration_roles(),
            }
        )
    return _start_role_registration(
        request,
        FarmerRegistrationForm,
        'accounts/register.html',
        'farmer',
    )


def doctor_register(request):
    return _start_role_registration(
        request,
        DoctorRegistrationForm,
        'accounts/doctor_register.html',
        'doctor',
    )


def consultant_register(request):
    return _start_role_registration(
        request,
        ConsultantRegistrationForm,
        'accounts/consultant_register.html',
        'consultant',
    )


def admin_register(request):

    if request.method == 'POST':

        form = AdminRegistrationForm(request.POST)

        if form.is_valid():

            admin_code = form.cleaned_data.get('admin_code')
            configured_code = getattr(settings, 'ADMIN_SECRET_CODE', 'AGROSTHAN2026')

            if admin_code != configured_code:
                form.add_error('admin_code', 'Invalid Admin Code')
            else:
                payload = _clean_registration_payload(form.cleaned_data)
                otp_token = _create_registration_token(
                    'admin',
                    payload['email'],
                    payload['phone_number'],
                    payload,
                )
                return redirect('registration_verify', token=otp_token.token)

    else:

        form = AdminRegistrationForm()

    return render(
        request,
        'accounts/admin_register.html',
        {
            'form': form,
            'success': False,
        }
    )


def _start_role_registration(request, form_class, template_name, role_slug):

    if request.method == 'POST':

        form = form_class(request.POST, request.FILES)

        if form.is_valid():

            payload = _clean_registration_payload(form.cleaned_data)
            profile_photo = form.cleaned_data.get('profile_photo')
            identity_photo = form.cleaned_data.get('identity_photo_upload')

            otp_token = _create_registration_token(
                role_slug,
                payload['email'],
                payload['phone'],
                payload,
                profile_photo=profile_photo,
                identity_photo=identity_photo,
            )
            return redirect('registration_verify', token=otp_token.token)

    else:

        form = form_class()

    return render(
        request,
        template_name,
        {
            'form': form,
            'success': False,
        }
    )


def _create_registration_token(role, email, phone_number, payload, profile_photo=None, identity_photo=None):

    email_otp = _generate_otp()
    phone_otp = _generate_otp()

    token = RegistrationOTP.objects.create(
        role=role,
        email=email,
        phone_number=phone_number,
        payload=payload,
        profile_photo=profile_photo,
        identity_photo_upload=identity_photo,
        email_otp_hash=make_password(email_otp),
        phone_otp_hash=make_password(phone_otp),
        expires_at=timezone.now() + timedelta(minutes=5),
    )

    _send_otp_email(email, role.title(), email_otp, phone_otp)
    return token


def _registration_form_context(token_obj):

    return {
        'token': token_obj,
        'role_label': token_obj.get_role_display(),
    }


def _finalize_registration(token_obj):

    payload = token_obj.payload

    if token_obj.role == 'farmer':
        farmer = Farmer.objects.create(
            name=payload['name'],
            email=payload['email'],
            phone=payload['phone'],
            address=payload['address'],
            password=make_password(payload['password']),
            email_verified=True,
            phone_verified=True,
        )
        return 'farmer', farmer

    if token_obj.role == 'doctor':
        doctor = Doctor.objects.create(
            full_name=payload['full_name'],
            email=payload['email'],
            phone=payload['phone'],
            aadhaar_number=payload['aadhaar_number'],
            pan_number=payload['pan_number'],
            identity_photo_upload=token_obj.identity_photo_upload,
            profile_photo=token_obj.profile_photo,
            password=make_password(payload['password']),
            is_approved=True,
            is_active_status=True,
            email_verified=True,
            phone_verified=True,
        )
        return 'doctor', doctor

    if token_obj.role == 'consultant':
        consultant = Consultant.objects.create(
            full_name=payload['full_name'],
            email=payload['email'],
            phone=payload['phone'],
            aadhaar_number=payload['aadhaar_number'],
            pan_number=payload['pan_number'],
            identity_photo_upload=token_obj.identity_photo_upload,
            profile_photo=token_obj.profile_photo,
            password=make_password(payload['password']),
            is_approved=True,
            is_active_status=True,
            email_verified=True,
            phone_verified=True,
        )
        return 'consultant', consultant

    if token_obj.role == 'admin':
        username = payload['email']
        user = User.objects.create_user(
            username=username,
            email=payload['email'],
            password=payload['password'],
            first_name=payload['full_name'],
            is_staff=True,
            is_active=True,
        )
        AdminProfile.objects.create(
            user=user,
            full_name=payload['full_name'],
            phone_number=payload['phone_number'],
            email_verified=True,
            phone_verified=True,
        )
        return 'admin', user

    return None, None


def registration_verify(request, token):

    token_obj = get_object_or_404(RegistrationOTP, token=token)

    if token_obj.is_consumed:
        messages.info(request, 'This verification link has already been used.')
        return redirect('login')

    expired = timezone.now() > token_obj.expires_at
    form = OTPVerificationForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():

        email_otp = form.cleaned_data['email_otp']
        phone_otp = form.cleaned_data['phone_otp']

        if expired:
            form.add_error(None, 'OTP expired. Please resend the OTP.')
        elif not check_password(email_otp, token_obj.email_otp_hash):
            form.add_error('email_otp', 'Invalid Email OTP')
        elif not check_password(phone_otp, token_obj.phone_otp_hash):
            form.add_error('phone_otp', 'Invalid Mobile OTP')
        else:
            role_slug, account = _finalize_registration(token_obj)
            token_obj.is_consumed = True
            token_obj.save(update_fields=['is_consumed', 'updated_at'])

            if role_slug == 'admin':
                auth_login(request, account)
                _set_admin_session(request, account)
                messages.success(request, 'Admin registration completed successfully.')
                return redirect('admin_dashboard')

            messages.success(request, f'{token_obj.get_role_display()} registration completed successfully.')
            return redirect('login')

    return render(
        request,
        'accounts/verify_registration_otp.html',
        {
            'form': form,
            'token': token_obj,
            'expired': expired,
        }
    )


@require_POST
def resend_registration_otp(request, token):

    token_obj = get_object_or_404(RegistrationOTP, token=token)

    if token_obj.is_consumed:
        messages.error(request, 'This verification link has already been used.')
        return redirect('login')

    if token_obj.resend_count >= 3:
        messages.error(request, 'Maximum resend attempts reached.')
        return redirect('registration_verify', token=token)

    email_otp = _generate_otp()
    phone_otp = _generate_otp()

    token_obj.email_otp_hash = make_password(email_otp)
    token_obj.phone_otp_hash = make_password(phone_otp)
    token_obj.resend_count += 1
    token_obj.verify_attempts = 0
    token_obj.expires_at = timezone.now() + timedelta(minutes=5)
    token_obj.save(update_fields=['email_otp_hash', 'phone_otp_hash', 'resend_count', 'verify_attempts', 'expires_at', 'updated_at'])

    _send_otp_email(token_obj.email, token_obj.get_role_display(), email_otp, phone_otp)
    messages.success(request, 'OTP resent successfully.')
    return redirect('registration_verify', token=token)


def login_view(request, role=None):

    error = None

    if request.method == 'POST':

        form = CommonLoginForm(request.POST)

        if form.is_valid():

            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            matched_role, user = _try_common_login(email, password)

            if matched_role == 'farmer':
                _set_account_session(request, 'farmer', user)
                return redirect(
                    _dashboard_url_for_account('farmer', user) or 'dashboard'
                )

            if matched_role == 'doctor':
                _set_account_session(request, 'doctor', user)
                return redirect(
                    _dashboard_url_for_account('doctor', user) or 'doctor_dashboard'
                )

            if matched_role == 'consultant':
                _set_account_session(request, 'consultant', user)
                return redirect(
                    _dashboard_url_for_account('consultant', user)
                    or 'consultant_dashboard'
                )

            if matched_role == 'admin':
                auth_login(request, user)
                _set_admin_session(request, user)
                return redirect('admin_dashboard')

            if matched_role:
                _set_account_session(request, matched_role, user)

                dashboard_url = _dashboard_url_for_account(matched_role, user)

                if dashboard_url:
                    return redirect(dashboard_url)

            error = "Invalid Email or Password"

    else:

        form = CommonLoginForm()

    return render(
        request,
        'accounts/login.html',
        {
            'form': form,
            'error': error,
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
    now = timezone.now()
    doctor_id = request.session.get('doctor_id')
    consultant_id = request.session.get('consultant_id')

    if doctor_id:
        Doctor.objects.filter(id=doctor_id).update(
            is_online=False,
            last_seen=now,
        )
    if consultant_id:
        Consultant.objects.filter(id=consultant_id).update(
            is_online=False,
            last_seen=now,
        )
    role = request.session.get('user_role')

    if role == 'doctor':

        doctor_id = request.session.get('doctor_id')

        if doctor_id:

            doctor = Doctor.objects.filter(id=doctor_id).first()

            if doctor:

                _mark_role_offline(doctor)

    elif role == 'consultant':

        consultant_id = request.session.get('consultant_id')

        if consultant_id:

            consultant = Consultant.objects.filter(id=consultant_id).first()

            if consultant:

                _mark_role_offline(consultant)

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

    current_role = request.session.get('user_role')

    if current_role == 'doctor':
        return redirect('doctor_profile')

    if current_role == 'consultant':
        return redirect('consultant_profile')

    if current_role == 'admin':
        return redirect('admin_dashboard')

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

            if not _account_password_matches(farmer.password, current_password):

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

            farmer.password = make_password(new_password)
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

        if not _account_password_matches(farmer.password, current_password):

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

            farmer.password = make_password(new_password)
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


def _prepare_role_identity_fields(form, unlocked):

    for field_name in ('aadhaar_number', 'pan_number', 'identity_photo_upload'):
        if field_name in form.fields:
            form.fields[field_name].disabled = not unlocked
            if not unlocked:
                form.fields[field_name].help_text = 'Locked by Admin'


def _handle_role_profile_update(request, account, form_class, dashboard_url_name, role_slug):

    form = form_class(request.POST or None, request.FILES or None, instance=account)
    _prepare_role_identity_fields(form, account.identity_edit_allowed)

    if request.method == 'POST' and form.is_valid():
        updated_account = form.save(commit=False)
        new_password = form.cleaned_data.get('password')
        new_profile_photo = form.cleaned_data.get('profile_photo')
        new_identity_photo = form.cleaned_data.get('identity_photo_upload')

        if new_password:
            updated_account.password = make_password(new_password)

        if not new_profile_photo:
            updated_account.profile_photo = account.profile_photo

        if not account.identity_edit_allowed:
            updated_account.aadhaar_number = account.aadhaar_number
            updated_account.pan_number = account.pan_number
            updated_account.identity_photo_upload = account.identity_photo_upload
        else:
            updated_account.identity_edit_allowed = False
            if not new_identity_photo:
                updated_account.identity_photo_upload = account.identity_photo_upload

        updated_account.save()

        session_name_key = f'{role_slug}_name'
        session_photo_key = f'{role_slug}_photo'
        request.session[session_name_key] = updated_account.full_name
        request.session[session_photo_key] = updated_account.profile_photo.url if updated_account.profile_photo else ''

        messages.success(request, f'{role_slug.title()} profile updated successfully.')
        return redirect(dashboard_url_name)

    return form


@doctor_required
def doctor_profile(request):

    doctor = Doctor.objects.filter(id=request.session.get('doctor_id')).first()

    if not doctor:
        return redirect('login')

    form = _handle_role_profile_update(request, doctor, DoctorProfileForm, 'doctor_dashboard', 'doctor')

    pending_request = IdentityChangeRequest.objects.filter(
        role=IdentityChangeRequest.ROLE_DOCTOR,
        account_id=doctor.id,
        status=IdentityChangeRequest.STATUS_PENDING,
    ).first()

    return render(
        request,
        'accounts/doctor_profile.html',
        {
            'doctor': doctor,
            'form': form,
            'pending_request': pending_request,
        }
    )


@consultant_required
def consultant_profile(request):

    consultant = Consultant.objects.filter(id=request.session.get('consultant_id')).first()

    if not consultant:
        return redirect('login')

    form = _handle_role_profile_update(request, consultant, ConsultantProfileForm, 'consultant_dashboard', 'consultant')

    pending_request = IdentityChangeRequest.objects.filter(
        role=IdentityChangeRequest.ROLE_CONSULTANT,
        account_id=consultant.id,
        status=IdentityChangeRequest.STATUS_PENDING,
    ).first()

    return render(
        request,
        'accounts/consultant_profile.html',
        {
            'consultant': consultant,
            'form': form,
            'pending_request': pending_request,
        }
    )


@doctor_required
@require_POST
def request_doctor_identity_change(request):

    doctor = Doctor.objects.filter(id=request.session.get('doctor_id')).first()

    if not doctor:
        return redirect('doctor_dashboard')

    IdentityChangeRequest.objects.get_or_create(
        role=IdentityChangeRequest.ROLE_DOCTOR,
        account_id=doctor.id,
        status=IdentityChangeRequest.STATUS_PENDING,
        defaults={
            'account_name': doctor.full_name,
            'email': doctor.email,
            'reason': request.POST.get('reason', '').strip(),
        }
    )

    messages.success(request, 'Identity change request sent to admin.')
    return redirect('doctor_profile')


@consultant_required
@require_POST
def request_consultant_identity_change(request):

    consultant = Consultant.objects.filter(id=request.session.get('consultant_id')).first()

    if not consultant:
        return redirect('consultant_dashboard')

    IdentityChangeRequest.objects.get_or_create(
        role=IdentityChangeRequest.ROLE_CONSULTANT,
        account_id=consultant.id,
        status=IdentityChangeRequest.STATUS_PENDING,
        defaults={
            'account_name': consultant.full_name,
            'email': consultant.email,
            'reason': request.POST.get('reason', '').strip(),
        }
    )

    messages.success(request, 'Identity change request sent to admin.')
    return redirect('consultant_profile')
