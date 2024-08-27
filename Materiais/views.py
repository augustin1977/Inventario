from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from .models import *
from django.core.paginator import Paginator
from .forms import *
from django.db.models import Q  # Import Q
from django.conf import settings
from usuarios.models import *
from funcoes_basicas import *
from django.contrib import messages
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.units import cm
import os
import io
import pandas as pd
from PIL import Image as PILImage
from django.http import JsonResponse
@is_user
def home(request):
    status = str(request.GET.get("status"))
    return render(request,"home.html",{'status':status})


@is_user
def cadastrar_material(request):
    context = {}
    if request.method == 'POST':
        form = CadstroMaterial(request.POST, request.FILES)
        if form.is_valid():
            material = form.save(commit=False)
            if 'foto1' in request.FILES:
                original_image = request.FILES['foto1']
                resized_image = resize_image(original_image)
                material.foto1 = resized_image
            material.save()
            return redirect("/cadastro?status=1")
    else:
        form = CadstroMaterial()
          
    context['form'] = form
    return render(request, "cadastro_material.html", context)

@is_admin
def cadastrar_material_lote(request):
    if request.method == 'POST':
        file = request.FILES.get("file")

        if not file:
            messages.error(request, "Nenhum arquivo foi selecionado.")
            return render(request, "cadastro_material_lote.html")

        try:
            # Ler todas as planilhas do arquivo Excel
            xls = pd.ExcelFile(file)
        except Exception as e:
            messages.error(request, f"Erro ao ler o arquivo: {str(e)}")
            return render(request, "cadastro_material_lote.html")

        # Iterar sobre todas as planilhas do arquivo Excel
        i=0
        for sheet_name in xls.sheet_names:
            df = pd.read_excel(xls, sheet_name=sheet_name) 

            # Iterar sobre as linhas da planilha
           
            for index, row in df.iterrows():
                rgp = NAN(str(row['RGP 8 dígitos']),"")  # Garantir que o RGP tenha 8 dígitos, preenchendo com zeros à esquerda
                if rgp=="":
                    rgp="NC"
                else:
                    rgp=rgp.zfill(8)
                i+=1
                if i%1000==0:
                    messages.success(request, f"{i} arquivos processados.")
                # Verificar se o material já existe
                if Material.objects.filter(RGP=rgp).exists():
                    print(f"Item {rgp} ja existe!")
                    continue  # Pula para o próximo item
                codigo=NAN(row['CÓDIGO MATERIAL'],"")
                codigo_conta= NAN(row(["CÓDIGO DA CONTA"]))
                nome = NAN(row['DESCRIÇÃO RESUMIDA'],"")
                modelo = NAN(row['MARCA/MODELO'],"")
                valor = numero(NAN(row['VALOR REAVALIAÇÃO'],0),float)
                # Processar a localização
                localizacao_nome = NAN(row['LOCALIZAÇÃO'],"")
                localizacao, created = Localizacao.objects.get_or_create(
                    gerencia=localizacao_nome,
                    defaults={
                        'superintendencia': 'SP',  # ou outro valor padrão
                        'gerencia': localizacao_nome,
                        'endereco': '',
                        'obs': '',
                        'ativo': True
                    }
                )

                # Processar o estado
                estado_nome = NAN(row['ESTADO DE CONSERVAÇÃO'],"").capitalize()
                if Estado_bem.objects.filter(estado=estado_nome).exists():
                    estado=Estado_bem.objects.get(estado=estado_nome)
                else:
                    estado=Estado_bem.objects.get(estado="NA")
                # Definir os valores de uso, ativo e servível com base na coluna Condição
                if NAN(row['Condição'],0) == 0:
                    uso = True
                    ativo = True
                    servivel = True
                else:
                    uso = False
                    ativo = True
                    servivel = False

                # Criar o material
                material = Material(
                    RGP=rgp,
                    codigo=codigo,
                    nome=nome,
                    modelo=modelo,
                    valor=valor,
                    localizacao=localizacao,
                    estado=estado,
                    uso=uso,
                    ativo=ativo,
                    servivel=servivel,
                    codigo_conta=codigo_conta,
                    obs=''  # Ajustar conforme necessário
                )
                material.save()

        messages.success(request, "Materiais cadastrados com sucesso!")
        return redirect("/cadastro?status=1")

    return render(request, "cadastro_material_lote.html")

    

@is_user
def listar_materiais(request):
    query = request.GET.get('q')
    gerencia = request.GET.get('gerencia')
    gerencias=Localizacao.objects.all()
    
    if gerencia and not query:
        busca=gerencia.split('_')
        local=Localizacao.objects.get(superintendencia=busca[0].strip(),
                                         cidade=busca[2].strip(),
                                         gerencia=busca[1].strip())
        materiais_list = Material.objects.filter(localizacao=local).order_by('RGP')
        #materiais_list = Material.objects.all()
    elif query and not gerencia:
        
        materiais_list = Material.objects.filter(
            Q(nome__icontains=query) |
            Q(localizacao__gerencia__icontains=query) |
            Q(localizacao__cidade__icontains=query) |
            Q(localizacao__superintendencia__icontains=query) |
            Q(RGP__icontains=query) &
            Q(ativo=1)
        ).order_by('RGP')
    elif query and gerencia:
        busca=gerencia.split('_')
        local=Localizacao.objects.filter(superintendencia=busca[0].strip(),
                                         cidade=busca[2].strip(),
                                         gerencia__icontains=busca[1].strip())
        materiais_list = Material.objects.filter(
            Q(nome__icontains=query) |
            Q(localizacao__cidade__icontains=query) |
            Q(localizacao__superintendencia__icontains=query) |
            Q(RGP__icontains=query) & Q(localizacao=local[0])&
            Q(ativo=1)
        ).order_by('RGP')
    else:
        materiais_list = Material.objects.all().order_by('RGP')

    # Exportar PDF
    if 'export' in request.GET and request.GET['export'] == 'pdf':
        return exportar_pdf(materiais_list)

    # Exportar XLSX
    if 'export' in request.GET and request.GET['export'] == 'xlsx':
        return exportar_xlsx(materiais_list)

    paginator = Paginator(materiais_list, 20)  # 20 itens por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'listar_materiais.html', {'page_obj': page_obj, 'query': query,'selected_gerencia':gerencia ,'gerencias':gerencias})


@is_user
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

@is_user
def disponibilizar_item(request, id):
    if request.method == 'POST':
        item = get_object_or_404(Material, id=id)
        item.ativo = False
        item.descartado = True
        item.save()
        return JsonResponse({'status': 'success', 'ativo': item.ativo, 'descartado': item.descartado})
    return JsonResponse({'status': 'fail'})

@is_admin
def apagar_item(request, id):
    item = get_object_or_404(Material, id=id)
    if request.method == 'POST':
        item.delete()  # Deleta o item do banco de dados
        return redirect('listar_materiais')
    return render(request, 'confirmar_apagar.html', {'item': item})

@is_admin
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

@is_user
def listar_localizacao(request):
    locais = Localizacao.objects.all().order_by("-cidade","gerencia")   
    return render(request, 'listar_localizacao.html', {'page_obj': locais})

@is_admin
def apagar_localizacao(request, id):
    local = get_object_or_404(Localizacao, id=id)
    if request.method == 'POST':
        local.ativo=0
        local.save()
        return redirect('listar_localizacao')
    return render(request, 'confirmar_apagar_local.html', {'local': local})

@is_admin
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


def exportar_pdf(materiais_list):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=20, leftMargin=20, topMargin=28.35, bottomMargin=28.35)  # 1 cm = 28.35 points

    styles = getSampleStyleSheet()
    style_title = styles['Title']
    style_title.alignment = TA_CENTER

    title = Paragraph("Relatório de Materiais", style_title)

    # Estilo para as células da tabela
    style_cell = ParagraphStyle(name='Normal', alignment=TA_LEFT, fontSize=10)

    # Dados da tabela
    data = [["RGP", "Nome", "Localização","Estado","Foto", "Valor","Servivel","em Uso?","Ativo"]]
    for material in materiais_list:
        ativo="Não"
        uso="Não"
        servivel="Não"
        if material.ativo:
            ativo="Sim"
        if material.uso:
            uso="Sim"
        if material.servivel:
            servivel="Sim"
        foto_path = os.path.join(settings.MEDIA_ROOT, material.foto1.name) if material.foto1 else None
        
        # Verificar se a foto existe e adicionar ao PDF
        if foto_path and os.path.exists(foto_path):
            
            compressed_image = compress_image(foto_path)
            img = Image(compressed_image, width=2*cm, height=2*cm)
            img.drawWidth = 2 * cm
            img.drawHeight = 2 * cm * img.imageHeight/ img.imageWidth  
              # Mantém a proporção da imagem
            
        else:
            img = Paragraph("Sem foto", style_cell)
        data.append([
            Paragraph(str(material.RGP), style_cell),
            Paragraph(str(material.nome), style_cell),
            Paragraph(str(material.localizacao.local()), style_cell),
            Paragraph(str(material.estado), style_cell),
            img,
            Paragraph(str(material.valor), style_cell),
            Paragraph(servivel, style_cell),
            Paragraph(uso, style_cell),
            Paragraph(ativo, style_cell)
        ])

    # Criar a tabela
    table = Table(data, colWidths=[50, 100, 100, 50, 70,70,50,50,50])
    
    # Estilo da tabela
    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('VALIGN', (0, 0), (-1, -1), 'TOP')
    ])
    table.setStyle(style)

    # Construir o documento
    elements = [title, Spacer(1, 12), table]
    doc.build(elements)

    buffer.seek(0)

    response= HttpResponse(buffer,  content_type="application/pdf")
    response["Content-Disposition"] = f"attachment; filename=relatorio_materiais.pdf"
    return response


def exportar_xlsx(materiais_list):
    sim_nao=lambda x: "Sim" if x else "Não"

    data = [{
        'RGP': material.RGP,
        'codigo': material.codigo,
        'codigo_conta':material.codigo_conta,
        'Nome': material.nome,
        'Modelo':material.modelo,
        'Localização': material.localizacao,
        'Estado': material.estado,
        'Valor': material.valor,
        'servivel': sim_nao(material.servivel),
        'Em Uso?': sim_nao(material.uso),
        'Ativo':sim_nao(material.ativo)
        
    } for material in materiais_list]

    df = pd.DataFrame(data)
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Materiais')

    buffer.seek(0)

    response= HttpResponse(buffer,  content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response["Content-Disposition"] = f"attachment; filename=relatorio_materiais.xlsx"
    return response


def compress_image(image_path, max_width=120, max_height=120):
    img = PILImage.open(image_path)
    img.thumbnail((max_width, max_height))
    output = io.BytesIO()
    img.save(output, format='JPEG', quality=75)  # Ajustar a qualidade conforme necessário
    output.seek(0)
    return output