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
class Material(models.Model):
    RGP = models.CharField(max_length=255,unique=True)
    data_cadastro=models.DateTimeField(auto_now_add=True)
    data_atualizacao=models.DateTimeField(auto_now=True)
    nome = models.CharField(max_length=255)
    localizacao=models.ForeignKey(Localizacao, on_delete=models.CASCADE)
    foto=models.FileField()
    obs=models.TextField(null=True,blank=True)
    ativo=models.BooleanField(default=True)
    valor=MoneyField(max_digits=19, decimal_places=4, null=True, default_currency="BRL") # type: ignore

    def __str__(self):
        return f"{self.RGP} - {self.nome} - {self.localizacao}"
