from django.urls import path
from . import views
urlpatterns = [
    path("",views.home, name="home"),
    path("cadastrar_item/",views.cadastrar, name="cadastrar_item"),
]