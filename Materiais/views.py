from django.shortcuts import render

# Create your views here.
from .models import *
from .forms import *
 
 
def cadastro(request):
    context ={}
    # add the dictionary during initialization
    form = CadstroMaterial(request.POST or None)
    if form.is_valid():
        form.save()
        print("Salvou")
         
    context['form']= form
    return render(request, "cadastro_material.html", context)