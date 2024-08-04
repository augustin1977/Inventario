from django import forms
from .models import *
from django.forms import ModelForm, ImageField
from djmoney.forms.fields import MoneyField
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
import re
from django.core.mail import send_mail
from django.conf import settings
import funcoes_basicas
 
 
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
        fields = ["RGP", "nome", "localizacao", "localizacao","foto1","estado","obs","valor","ativo",'descartado']
        widgets = {'foto1': forms.FileInput(attrs={'accept':"'image/*'"})
        }
class CadastroLocalizacao(forms.ModelForm):

    # create meta class
    class Meta:
        # specify model to be used
        model = Localizacao
        # specify fields to be used
        fields = "__all__"
        
    def clean_superintendencia(self):
        superintendencia = self.cleaned_data.get('superintendencia')
        if not re.match(r'^[A-Z]{2}$', superintendencia):
            raise forms.ValidationError("O campo Superintendência deve conter a sigla do Estado da Superintendência.")
        return superintendencia

