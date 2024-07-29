from django.shortcuts import render
from django.http import HttpResponse
from .models import Usuario,Tipo
from django.shortcuts import redirect 
from hashlib import sha256
from usuarios.forms import *
from inventario import settings
import re
import string
import random
from django.http import Http404
from funcoes_basicas import *

def vazio(request):
    return redirect('/auth/login/') 
def login(request):
    # cria a view do login do usuário
    status=str(request.GET.get('status'))
    return render(request, "login.html", {'status':status})

@is_admin
def cadastrar(request):
    status=str(request.GET.get('status'))
    return render(request, "cadastro.html", {'status':status})

@is_user
def editar(request):

    if not request.session.get('usuario'):
        return redirect('/auth/login/?status=2')
    usuario = Usuario.objects.get(id=request.session.get('usuario')) 

    if request.method=="GET":

        return render(request, "editar.html",{'usuario':usuario})

    senha_antiga=request.POST.get("senha_antiga")
    nova_senha=request.POST.get("senha_nova")
    nova_senha2=request.POST.get("senha_nova2")

    nome=request.POST.get("nome")
    email=request.POST.get("email")

    if nova_senha!= nova_senha2:
        return render(request, "editar.html",{'usuario':usuario,'status':5})
    senha_antiga=sha256(senha_antiga.encode()).hexdigest()
    
    if senha_antiga==usuario.senha:
        #regex = "^(?=.*[0-9])(?=.*[a-z])(?=.*[A-Z])(?=.*[!@#$%<^&*?()])[a-zA-Z0-9!@#$%<^&*?()]{6,}" # verifica se tem ao menos uma letra, um numero, um simbolo e no minimo 6 caracteres 
        if  True :#(re.search(regex, nova_senha)):
            nova_senha=sha256(nova_senha.encode()).hexdigest()
            usuario.nome=nome
            usuario.senha=nova_senha
            usuario.email=email
            usuario.primeiro_acesso=False
            usuario.save()
            return redirect("/cadastro")
        else:
            return render(request, "editar.html",{'usuario':usuario,'status':3})
    return render(request, "editar.html",{'usuario':usuario,'status':1})
    
def valida_cadastro(request):
    # validar cadastro, falta implementar verificação de e-mail
    nome=request.POST.get('nome')
    email=request.POST.get('email')
    senha=gera_senha(12)
    tipo=Tipo.objects.get(tipo="user")
    primeiro_acesso=True
    ativo=True
    print(nome,email,senha,tipo,primeiro_acesso,ativo)
    padrao = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    if not re.fullmatch(padrao, email):
        return redirect('/auth/cadastrar/?status=4') # email invalido
    try:    
        senhacod= sha256(senha.encode()).hexdigest() # recuperando senha e codificando num hash sha256
        usuario=Usuario(nome=nome, senha=senhacod, email=email, tipo=tipo, primeiro_acesso=primeiro_acesso,ativo=ativo) # cria um objeto usuário com as informações recebidas do fomulario
        try:
            conteudo_html = f"""<html>
                                <head></head>
                                <body>
                                    <h2>Olá {nome}!</h2>
                                    <p>Seu login foi criado no sistema de inventário do MTE.</p>
                                    <p>Os dados para login são:</p>
                                    <p>Seu nome de usuário: {email}</p>
                                    <p>Sua senha provisória: {senha}</p>
                                    <p>O link para acesso ao sistema é: <a href="192.168.0.197"> 192.168.0.197 </a></p>
                                    <p>Obrigado!</p>
                                    <p> Administrado do Sistema</p>
                                </body>
                                </html>"""
            conteudo_plain=f"A sua senha provisória é {senha}"
            enviar_email("Envio de senha provisória",conteudo_html,[email]) 
        except:
            raise Http404("Impossivel enviar o e-mail com a senha, favor contactar o Administrador")
        usuario.save() # salva o objeto usuário no banco de dados
        return redirect('/auth/login/?status=0') # retorna sem erro e sem usuario

    except Exception as e:
        print(e)
        return redirect('/auth/cadastrar/?status=99') # retorna erro geral de gravação no banco de dados
  
    return HttpResponse("Erro na pagina de cadastro - View")

def validar_login(request):
    # validar o login feito na pagina de login
    email=request.POST.get('email')
    senha=request.POST.get('senha')
    #primeiro_acesso=False
    senha=sha256(senha.encode()).hexdigest()
    usuario=Usuario.objects.filter(email=email).filter(senha=senha).filter(ativo=True)
    
    if len(usuario)==0:
        return redirect('/auth/login/?status=1')
    else:
        request.session['usuario']= usuario[0].id
        
        if usuario[0].primeiro_acesso==True:
            return redirect('/auth/editar/?status=1')
        return redirect("/cadastro")

def esqueci_senha(request):
    
    if request.method=="GET":
        status=request.GET.get('status')
        return render(request, "esqueci_senha.html", {'status':status})
    else:
        email= request.POST.get('email')
        usuario=Usuario.objects.filter(email=email,ativo=True)
        if len(usuario)==0:
            return redirect('/auth/esqueci_senha/?status=1') # Usuario não cadastrado
        novasenha=gera_senha(12)
        usuario[0].senha=sha256(novasenha.encode()).hexdigest()   
        usuario[0].primeiro_acesso=True
        try:
            
            enviar_email(subject='Recuperação de Senha Sistema de gestão de ativos',message=f"A sua nova senha é {novasenha}",
            from_email="gestaodeativos@outlook.com.br",recipient_list=[usuario[0].email,'gestaodeativos@outlook.com.br'])  
        except:
            return redirect('/auth/esqueci_senha/?status=2') # Falha no envio
        
        usuario[0].save()
        
        return redirect('/auth/login/?status=51') # nova senha enviada por email com sucesso

def sair(request):
    if not request.session.get('usuario'):
        return redirect('/auth/login/?status=2')
    usuario=Usuario.objects.get(id=request.session.get('usuario'))
    #log=Log(transacao='us',movimento='lf',usuario=usuario,alteracao=f'{usuario} saiu do sistema')
    #log.save()
    request.session.flush() # sair do usuário
    return redirect('/auth/login')

def gera_senha(tamanho):
    caracteres = string.ascii_letters + string.digits + string.punctuation + string.ascii_letters
    senha = ''.join(random.choice(caracteres) for i in range(tamanho-1))
    senha=random.choice(string.ascii_uppercase)+senha
    return senha
@is_admin
def listarUsuarios(request):
    usuarios=Usuario.objects.filter(ativo=True).order_by('nome')
    return render(request, "listaUsuarios.html", {'usuarios':usuarios})
    
@is_admin
def exibirUsuario(request):
    if not request.session.get("usuario"):
        return redirect("/auth/login/?status=2")
    usuario=Usuario.objects.get(id=request.session.get('usuario'))
    tipo=Tipo.objects.get(tipo="admin")
    user=Usuario.objects.get(id=request.GET.get('usuario'))
    ##print(usuario.nome,usuario.tipo,usuario.id)
    if not usuario:
        return redirect('/auth/login/?status=1')
    elif(usuario.tipo==tipo):
        return render(request, "exibirUsuario.html", {'usuario':user})
    else:
        return redirect("/cadastro")
@is_admin
def editarUsuario(request):
    usuario=Usuario.objects.get(id=request.session.get('usuario'))
    tipo=Tipo.objects.get(tipo="admin")
    if(usuario.tipo==tipo):
        if request.method=="GET":
            user=Usuario.objects.get(id=request.GET.get('usuario'))
            ##print(user)
            form=EditaUsuarioForm(instance=user)
            return render(request, "editarUsuario.html", {'form':form})
        elif request.method=="POST":
            details = EditaUsuarioForm(request.POST)
            if details.is_valid():
                user=Usuario.objects.get(id=details.cleaned_data['id'])
                listaCampos=['nome','chapa','email','tipo','primeiro_acesso']
                alteracao=False
                for campo in listaCampos:
                    setattr(user,campo,details.cleaned_data[campo])
                user.save() 
            usuarios=Usuario.objects.filter(ativo=True).order_by('nome')
            return render(request, "listaUsuarios.html", {'usuarios':usuarios})
        else:
            return redirect("/cadastro?status=1")
    else:
        return redirect("/cadastro")
@is_admin    
def excluirUsuario(request):
    

    if not request.session.get('usuario'):
        return redirect('/auth/login/?status=1')
    usuario=Usuario.objects.get(id=request.session.get('usuario'))
    tipo=Tipo.objects.get(tipo="admin")
    if(usuario.tipo==tipo):
        if request.method=="GET":
            user=Usuario.objects.get(id=request.GET.get("usuario"))
            return render(request, "excluirUsuario.html", {'usuario':user})
        elif request.method=="POST":
            user=Usuario.objects.get(id=request.POST.get('id'))
            user.ativo=False
            user.save()           
            return redirect('/listarUsuarios/')
    return  redirect(f'/equipamentos/?status=50')
# Implementado e não testado
@is_admin
def trocasenha(request):
    if not request.session.get("usuario"):
        return redirect("/auth/login/?status=2")
    usuario_adm=Usuario.objects.get(id=request.session.get('usuario')) 
    tipo=Tipo.objects.get(tipo="admin")
    if(usuario_adm.tipo==tipo):
        usuarios=Usuario.objects.filter(ativo=True).order_by('nome')
        if request.method=="GET":
            id=request.GET.get('idUsuario')
            try:
                usuario_troca_senha=Usuario.objects.get(id=id,ativo=True)
            except:
                return render(request, "listaUsuarios.html", {'status':'1','usuarios':usuarios})# Usuario não cadastrado / Erro Geral
            
            novasenha=gera_senha(12)
            usuario_troca_senha.senha=sha256(novasenha.encode()).hexdigest()   
            usuario_troca_senha.primeiro_acesso=True
            
            try:
                conteudo_html = f"""<html>
                                <head></head>
                                <body>
                                    <h2>Olá {usuario_troca_senha}!</h2>
                                    <p>Foi solicitada uma nova senha para seu usuário pelo usuario administrador do sistema.</p>
                                    <p>Os dados para login são:</p>
                                    <p>Seu nome de usuário: {usuario_troca_senha.email}</p>
                                    <p>Sua nova senha provisória: {novasenha}</p>
                                    <p>O link do sistema é: <a href="192.168.0.197"> 192.168.0.197 </a> </p>
                                    <p>Obrigado!</p>
                                </body>
                                </html>"""
                              
                enviar_email("Envio de senha provisória",conteudo_html,[usuario_troca_senha.email]) 

                usuario_troca_senha.save()
                return render(request, "listaUsuarios.html", {'status':'51','usuarios':usuarios}) # troca de senha efetuada com sucesso  
            except:
                return render(request, "listaUsuarios.html", {'status':'2','usuarios':usuarios}) # Erro no envio do email
        
    return redirect('/auth/login/?status=0')
        
