# dashboard/forms.py

from company.models import SiteSettings

class SiteSettingsForm(forms.ModelForm):

    class Meta:

        model = SiteSettings

        fields = "__all__"