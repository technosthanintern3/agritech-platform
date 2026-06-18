from .models import Farmer, SiteSettings


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


def site_settings(request):

    return {
        'site_settings': SiteSettings.objects.first()
    }