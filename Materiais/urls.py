from django.urls import path
from . import views

urlpatterns = [
    path("",views.home, name="home"),
    path("cadastrar_item/",views.cadastrar_material, name="cadastrar_item"),
    path("cadastrar_item_lote/",views.cadastrar_material_lote, name="cadastrar_item_lote"),
    path("cadastrar_localizacao/",views.cadastrar_localizacao, name="cadastrar_localizacao"),
    path('listar_materiais/', views.listar_materiais, name='listar_materiais'),
    path('listar_localizacao/', views.listar_localizacao, name='listar_localizacao'),
    path('itens/editar/<int:id>/', views.editar_item, name='editar_item'),
    path('itens/apagar/<int:id>/', views.apagar_item, name='apagar_item'),
    path('localizacao/editar/<int:id>/', views.editar_localizacao, name='editar_local'),
    path('localiacao/apagar/<int:id>/', views.apagar_localizacao, name='apagar_local'),
    path('disponibilizar/<int:id>/', views.disponibilizar_item, name='disponibilizar_item'),
    
]