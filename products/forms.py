from django import forms
from .models import Review


class ReviewForm(forms.ModelForm):

    class Meta:

        model = Review

        fields = [
            'name',
            'rating',
            'comment'
        ]

        widgets = {

            'rating': forms.Select(
                choices=[
                    (1, '⭐'),
                    (2, '⭐⭐'),
                    (3, '⭐⭐⭐'),
                    (4, '⭐⭐⭐⭐'),
                    (5, '⭐⭐⭐⭐⭐')
                ]
            ),

            'comment': forms.Textarea(
                attrs={
                    'rows': 4
                }
            )

        }