from django import forms
from .models import Review


class ReviewForm(forms.ModelForm):

    class Meta:

        model = Review

        fields = [
            'name',
            'rating',
            'review_text'
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

            'review_text': forms.Textarea(
                attrs={
                    'rows': 4
                }
            )

        }