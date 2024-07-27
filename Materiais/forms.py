from django import forms
from .models import *
from django.forms import ModelForm, ImageField
from djmoney.forms.fields import MoneyField
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
import re
import string
import random
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
        fields = ["RGP", "nome", "localizacao", "localizacao","foto1","estado","obs","valor"]
        widgets = {
            'foto1': forms.FileInput(attrs={'accept': 'image/*;capture=camera'})
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

class CadastroUsuario(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True, label='Nome')
    last_name = forms.CharField(max_length=30, required=True, label='Sobrenome')
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')
    
    def clean(self):
        super().clean()
        password=str(funcoes_basicas.generate_random_password())
        self.cleaned_data["password1"]=password
        self.cleaned_data["password2"]=self.cleaned_data["password1"]
        return self.cleaned_data

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Remover os campos de senha
        self.fields.pop('password1')
        self.fields.pop('password2')
        
    def save(self, commit=True):
        
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.username = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.set_password=self.cleaned_data["password1"]
        funcoes_basicas.enviar_email(
                'Senha do Sistema de Inventario do MTE',
                f'Sua senha provisória é: {self.cleaned_data["password1"]}',
                settings.EMAIL_HOST_USER,
                [user.email,settings.EMAIL_HOST_USER],
                settings.EMAIL_HOST_PASSWORD_APP
            )
        if commit:
            user.save()
        return user