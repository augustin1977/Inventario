from django import forms
from .models import *
from django.forms import ModelForm, ImageField
 
 
# creating a form
class CadstroMaterial(forms.ModelForm):
   
    # create meta class
    class Meta:
        # specify model to be used
        model = Material
        # specify fields to be used
        fields = ["RGP", "nome", "localizacao", "localizacao","foto1","estado","obs","valor"]
        widgets = {'foto1':  forms.FileInput(attrs={'accept': "image/*;capture=camera"})}
