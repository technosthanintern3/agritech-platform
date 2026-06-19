from django.contrib.auth import get_user_model

from .models import Farmer, SiteSettings, Doctor, Consultant, RolePageSettings, FooterSettings


User = get_user_model()


def _name_for_object(user_object):

    if not user_object:
        return ''

    for field_name in ('full_name', 'name', 'username', 'email'):

        value = getattr(user_object, field_name, None)

        if value:
            return value

    return str(user_object)


def current_account(request):

    current_role = None
    current_user_object = None

    farmer_id = request.session.get('farmer_id')
    doctor_id = request.session.get('doctor_id')
    consultant_id = request.session.get('consultant_id')
    admin_id = request.session.get('admin_id')

    if farmer_id:
        current_role = 'farmer'
        current_user_object = Farmer.objects.filter(id=farmer_id).first()

    elif doctor_id:
        current_role = 'doctor'
        current_user_object = Doctor.objects.filter(id=doctor_id).first()

    elif consultant_id:
        current_role = 'consultant'
        current_user_object = Consultant.objects.filter(id=consultant_id).first()

    elif admin_id or (
        request.user.is_authenticated
        and (request.user.is_staff or request.user.is_superuser)
    ):
        current_role = 'admin'
        current_user_object = request.user

        if admin_id and not request.user.is_authenticated:
            current_user_object = User.objects.filter(id=admin_id).first()

    return {
        'current_role': current_role,
        'current_user_name': _name_for_object(current_user_object),
        'current_user_object': current_user_object,
        'current_user_photo': _photo_for_object(current_user_object),
    }


def _photo_for_object(user_object):

    if not user_object:
        return ''

    for field_name in ('profile_photo', 'profile_picture', 'photo', 'image'):
        image_field = getattr(user_object, field_name, None)
        if image_field:
            try:
                return image_field.url
            except ValueError:
                return ''

    return ''


def logged_in_farmer(request):

    farmer = None

    farmer_id = request.session.get('farmer_id')

    if farmer_id:
        try:
            farmer = Farmer.objects.get(id=farmer_id)
        except Farmer.DoesNotExist:
            pass

    return {
        'logged_in_farmer': farmer
    }


def logged_in_doctor(request):

    doctor = None

    doctor_id = request.session.get('doctor_id')

    if doctor_id:
        try:
            doctor = Doctor.objects.get(id=doctor_id)
        except Doctor.DoesNotExist:
            pass

    return {
        'logged_in_doctor': doctor
    }


def logged_in_consultant(request):

    consultant = None

    consultant_id = request.session.get('consultant_id')

    if consultant_id:
        try:
            consultant = Consultant.objects.get(id=consultant_id)
        except Consultant.DoesNotExist:
            pass

    return {
        'logged_in_consultant': consultant
    }


def site_settings(request):

    return {
        'site_settings': SiteSettings.objects.first()
    }


def footer_settings(request):

    return {
        'footer_settings': FooterSettings.objects.first()
    }


def role_page_settings(request):

    settings_obj = RolePageSettings.objects.order_by('role_name').first()

    return {
        'role_settings': settings_obj
    }
