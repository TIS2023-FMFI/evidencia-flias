from django import forms
from .models import SpravaPlynov

class SpravaPlynovForm(forms.ModelForm):
    class Meta:
        model = SpravaPlynov
        fields = ['nazov_plynu', 'mnozstvo', 'datum_dodania', 'poznamky']
