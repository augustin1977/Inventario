from django import forms
from .models import *
from django.forms import ModelForm, ImageField
from djmoney.forms.fields import MoneyField
 
 
# creating a form
class CadstroMaterial(forms.ModelForm):
    valor = MoneyField(
    max_digits=19, 
    decimal_places=4, 
    default_currency='BRL', )
   
    # create meta class
    class Meta:
        # specify model to be used
        model = Material
        # specify fields to be used
        fields = ["RGP", "nome", "localizacao", "localizacao","foto1","estado","obs","valor"]
        widgets = {
            'foto1': forms.FileInput(attrs={'accept': 'image/*;capture=camera'})
        }
