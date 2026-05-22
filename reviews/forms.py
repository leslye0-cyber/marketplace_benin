# reviews/forms.py

from django import forms
from .models import Review


class ReviewForm(forms.ModelForm):
    note = forms.ChoiceField(
        choices=[(i, f'{i} étoile{"s" if i > 1 else ""}') for i in range(1, 6)],
        widget=forms.RadioSelect(attrs={'class': 'star-radio'}),
        label='Note'
    )

    class Meta:
        model = Review
        fields = ['note', 'commentaire']
        widgets = {
            'commentaire': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Partagez votre expérience avec ce produit...'
            }),
        }
        labels = {
            'commentaire': 'Votre commentaire',
        }