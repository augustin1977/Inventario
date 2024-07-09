from django.shortcuts import render,redirect
from django.shortcuts import render, get_object_or_404, redirect
from .models import *
from django.http import HttpResponse, JsonResponse,HttpResponseRedirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import auth
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.core.paginator import Paginator
from .models import *
from .forms import *


# views de definição de acesso 
def is_admin(user):
    return user.groups.filter(name='admin').exists() 

def is_user(user):
    return user.groups.filter(name='user').exists() or user.groups.filter(name='admin').exists() 
def custom_redirect(view_name, status_code):
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            if view_func(request.user):
                return view_func(request, *args, **kwargs)
            else:
                return redirect(f'/{view_name}?status={status_code}')
        return _wrapped_view
    return decorator

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
@user_passes_test(is_user,login_url='/?status=99')
def listar_materiais(request):
    materiais = Material.objects.filter(ativo=1)
    paginator = Paginator(materiais, 5)  # 5 itens por página

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'listar_materiais.html', {'page_obj': page_obj})


@login_required

@user_passes_test(is_admin,login_url='/cadastro?status=99')
def editar_item(request, id):
    item = get_object_or_404(Material, id=id)
    if request.method == 'POST':
        form = CadstroMaterial(request.POST, request.FILES, instance=item)
        if form.is_valid():
            form.save()
            return redirect('listar_materiais')
    else:
        form = CadstroMaterial(instance=item)
    return render(request, 'editar_item.html', {'form': form, 'item': item})


@login_required
@user_passes_test(is_user,login_url='/?status=99')
def apagar_item(request, id):
    item = get_object_or_404(Material, id=id)
    if request.method == 'POST':
        item.ativo=0
        item.save()
        return redirect('listar_materiais')
    return render(request, 'confirmar_apagar.html', {'item': item})