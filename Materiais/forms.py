from django import forms
from .models import *
 
 
# creating a form
class CadstroMaterial(forms.ModelForm):
 
    # create meta class
    class Meta:
        # specify model to be used
        model = Material
 
        # specify fields to be used
        fields = fields = ["RGP", "nome", "localizacao", "localizacao","foto1","estado","obs","valor"]
