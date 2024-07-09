from django.shortcuts import render,redirect
from django.shortcuts import render, get_object_or_404, redirect
from .models import *
from django.http import HttpResponse, JsonResponse,HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib import auth
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages

# Create your views here.
from .models import *
from .forms import *
# Views adiminstrativas do sistema 
def home(request):
    status = str(request.GET.get("status"))
    return render(request,"home.html",{'status':status})

def logoutUser(request):
    logout(request)
    return redirect('login')
# view das funcionalidades do sistema

@login_required
def cadastrar(request):
    context = {}
    if request.method == 'POST':
        form = CadstroMaterial(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect("/?status=1")
    else:
        form = CadstroMaterial()
          
    context['form'] = form
    return render(request, "cadastro_material.html", context)

@login_required
def listar_materiais(request):
    materiais = Material.objects.filter(ativo=1)
    context = {
        'materiais': materiais
    }
    return render(request, 'listar_materiais.html', context) 