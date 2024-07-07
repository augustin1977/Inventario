from django.contrib import admin
from .models import *
from django.utils.html import format_html
# Register your models here.
# admin.site.register(Material)
admin.site.register(Localizacao)
admin.site.register(Estado_bem)

@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ('RGP', 'nome', 'display_foto', 'localizacao', 'data_cadastro', 'ativo')
    readonly_fields = ('data_cadastro', 'data_atualizacao')  # Campos que são apenas leitura
    search_fields = ['RGP', 'nome', 'localizacao__superintendencia', 'localizacao__cidade', 'localizacao__gerencia']
    list_per_page = 10  # Define o número de registros por página
    def display_foto(self, obj):
        return format_html('<img src="{}" height="150 width=100" />', obj.foto1.url)

    display_foto.short_description = 'Foto'  # Nome da coluna na listagem