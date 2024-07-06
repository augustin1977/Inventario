from django.db import models
from djmoney.models.fields import *


class Localizacao(models.Model):
    superintendencia=models.CharField(max_length=255,default="SP")
    cidade=models.CharField(max_length=255)
    gerencia=models.CharField(max_length=255)
    endereco=models.TextField(null=True,blank=True)
    obs=models.TextField(null=True,blank=True)
    ativo=models.BooleanField(default=True)

    def __str__(self):
        return f"{self.superintendencia} - {self.gerencia} - {self.cidade} - {self.endereco}"

class Estado_bem(models.Model):
    estado=models.CharField(max_length=255,default="Bom")
    def __str__(self):
        return f"{self.estado}"

class Material(models.Model):
    RGP = models.CharField(verbose_name="Numero RGP",max_length=255,unique=True)
    data_cadastro=models.DateTimeField(auto_now_add=True)
    data_atualizacao=models.DateTimeField(auto_now=True)
    nome = models.CharField(max_length=255)
    localizacao=models.ForeignKey(Localizacao, on_delete=models.CASCADE)
    foto1=models.ImageField(verbose_name="Foto do Item")
    estado=models.ForeignKey(Estado_bem,on_delete=models.CASCADE)
    obs=models.TextField(verbose_name="Observação",null=True,blank=True)
    ativo=models.BooleanField(verbose_name="Item em uso?",default=True)
    valor=MoneyField(max_digits=19, decimal_places=4, null=True, default_currency="BRL") # type: ignore

    def __str__(self):
        return f"{self.RGP} - {self.nome} - {self.localizacao}"
