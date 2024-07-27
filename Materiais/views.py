from django.shortcuts import render,redirect
from django.shortcuts import render, get_object_or_404, redirect
from .models import *
from django.http import HttpResponse, JsonResponse,HttpResponseRedirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import auth
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import Group
from django.contrib import messages
from django.core.paginator import Paginator
from .models import *
from .forms import *
from django.db.models import Q  # Import Q
from django.core.mail import send_mail
from django.conf import settings



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

@login_required
def logoutUser(request):
    logout(request)
    return redirect('login')

@login_required
@user_passes_test(is_admin,login_url='/cadastro?status=99')
def cadastrar_novo_usuario(request):
    if request.method == 'POST':
        form = CadastroUsuario(request.POST)
        if form.is_valid():
            user = form.save()
            group = Group.objects.get(name='user')
            user.groups.add(group)

            return redirect('home')
    else:
        form = CadastroUsuario()
    return render(request, 'cadastrar_usuario.html', {'form': form})

# view das funcionalidades do sistema


@login_required
@user_passes_test(is_user,login_url='/?status=99')
def cadastrar_material(request):
    context = {}
    if request.method == 'POST':
        form = CadstroMaterial(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect("/cadastro?status=1")
    else:
        form = CadstroMaterial()
          
    context['form'] = form
    return render(request, "cadastro_material.html", context)


@login_required
@user_passes_test(is_user,login_url='/?status=99')
def listar_materiais(request):
    query = request.GET.get('q')
    if query:
        materiais_list = Material.objects.filter(
            Q(nome__icontains=query) |
            Q(localizacao__gerencia__icontains=query) |
            Q(localizacao__cidade__icontains=query) |
            Q(localizacao__superintendencia__icontains=query) |
            Q(RGP__icontains=query) &
            Q(ativo=1)
        )
    else:
        materiais_list = Material.objects.all()

    paginator = Paginator(materiais_list, 5)  # 5 itens por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'listar_materiais.html', {'page_obj': page_obj, 'query': query})


@login_required
@user_passes_test(is_user,login_url='/cadastro?status=99')
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

@login_required
@user_passes_test(is_admin,login_url='/cadastro?status=99')
def cadastrar_localizacao(request):
    context = {}
    if request.method == 'POST':
        form = CadastroLocalizacao(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect("/cadastro?status=1")
    else:
        form = CadastroLocalizacao()
          
    context['form'] = form
    return render(request, "cadastro_localizacao.html", context)

@login_required
@user_passes_test(is_user,login_url='/?status=99')
def listar_localizacao(request):
    locais = Localizacao.objects.all()   
    return render(request, 'listar_localizacao.html', {'page_obj': locais})

@login_required
@user_passes_test(is_admin,login_url='/?status=99')
def apagar_localizacao(request, id):
    local = get_object_or_404(Localizacao, id=id)
    if request.method == 'POST':
        local.ativo=0
        local.save()
        return redirect('listar_localizacao')
    return render(request, 'confirmar_apagar_local.html', {'local': local})

@login_required
@user_passes_test(is_user,login_url='/cadastro?status=99')
def editar_localizacao(request, id):
    local = get_object_or_404(Localizacao, id=id)
    if request.method == 'POST':
        form = CadastroLocalizacao(request.POST, request.FILES, instance=local)
        if form.is_valid():
            form.save()
            return redirect('listar_localizacao')
    else:
        form = CadastroLocalizacao(instance=local)
    return render(request, 'editar_localizacao.html', {'form': form, 'local': local})