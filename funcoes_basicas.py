import smtplib
from email.mime.text import MIMEText
from django.conf import settings
from usuarios.models import *
from Materiais.models import *
from django.shortcuts import render,redirect
from PIL import Image
import io
import pandas as pd
from django.core.files.uploadedfile import InMemoryUploadedFile
def numero(valor,tipo):
    corrigindo=True
    i=0
    if type(valor)==tipo:
        return valor
    valor=str(valor)
    if tipo==float:
        while (corrigindo and i<len(valor)):
            try:
                valor=float(valor[i:])
                corrigindo=False
            except:
                corrigindo=True
                i+=1
        if type(valor)!=tipo:
            if(i>=len(valor)):
                    valor=0
                
    elif tipo==int:
        while (corrigindo and i<len(valor)):
            try:
                valor=int(valor[i:])
                corrigindo=False
            except:
                corrigindo=True
                i+=1
        if type(valor)!=tipo:
            if(i>=len(valor)):
                    valor=0
    return valor
def NAN(valor,opcao):
    if pd.isna(valor) or valor=="NaN":
        return opcao
    else:
        return valor
def resize_image(image_file, max_width=1080, max_height=720):
    # Abrir a imagem usando Pillow
    image = Image.open(image_file)
    
    # Redimensionar a imagem
    image.thumbnail((max_width, max_height))
    
    # Salvar a imagem em memória
    output = io.BytesIO()
    image.save(output, format='JPEG', quality=80)  # Ajuste a qualidade conforme necessário
    output.seek(0)
    
    # Criar um novo arquivo para Django
    resized_image_file = InMemoryUploadedFile(
        output, 
        'ImageField', 
        image_file.name, 
        'image/jpeg', 
        output.tell(), 
        None
    )
    
    return resized_image_file   
def enviar_email(subject,body,recipients):
        html_message = MIMEText(body, 'html')
        html_message['Subject'] = subject
        html_message['From'] = settings.EMAIL_HOST_USER
        html_message['To'] = ', '.join(recipients)
        with smtplib.SMTP_SSL(settings.EMAIL_HOST, settings.EMAIL_PORT) as server:
            server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD_APP)
            server.sendmail(settings.EMAIL_HOST_USER, recipients, html_message.as_string())   
            
            

def is_user(view_func):
    def wrapper(request, *args, **kwargs):
        try:
            usuario = request.session.get('usuario')
        except:
            usuario=False
        if usuario:
            user= Usuario.objects.get(id=usuario)
            tipouser=Tipo.objects.get(tipo="user")
            tipoadmin=Tipo.objects.get(tipo="admin")
            if user.ativo==1 and (user.tipo==tipouser or user.tipo==tipoadmin):
                return view_func(request, *args, **kwargs)
            else:
                return redirect('login')
        else:
            return redirect('login')  # Redireciona para uma página de login ou qualquer outra página apropriada
    return wrapper
def is_admin(view_func):
    def wrapper(request, *args, **kwargs):
        try:
            usuario = request.session.get('usuario')
        except:
            usuario=False
        if usuario:
            user= Usuario.objects.get(id=usuario)
            tipo=Tipo.objects.get(tipo="admin")
            if user.ativo and user.tipo==tipo:
                return view_func(request, *args, **kwargs)
            else: 
                return redirect("/cadastro?status=99")
        else:
            return redirect("/cadastro?status=99")  # Redireciona para uma página de login ou qualquer outra página apropriada
    return wrapper
           
