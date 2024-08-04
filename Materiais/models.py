from django.db import models
from djmoney.models.fields import *
from django.db.models.signals import pre_delete
from django.dispatch import receiver
   

class Localizacao(models.Model):
    superintendencia=models.CharField(verbose_name="Superintendência",max_length=255,default="SP")
    cidade=models.CharField(max_length=255)
    gerencia=models.CharField(verbose_name="Gerência",max_length=255)
    endereco=models.TextField(verbose_name="Endereço Completo",null=True,blank=True)
    obs=models.TextField(verbose_name="Observação",null=True,blank=True)
    ativo=models.BooleanField(verbose_name="Em uso",default=True)

    def __str__(self):
        return f"{self.superintendencia} _ {self.gerencia} _ {self.cidade} _ {self.endereco}"
    def local(self):
        return f"{self.superintendencia} _ {self.gerencia} _ {self.cidade}" 

class Estado_bem(models.Model):
    estado=models.CharField(max_length=255,default="Bom")
    def __str__(self):
        return f"{self.estado}"

class Material(models.Model):
    RGP = models.CharField(verbose_name="Numero RGP",max_length=255,unique=False)
    data_cadastro=models.DateTimeField(auto_now_add=True)
    data_atualizacao=models.DateTimeField(auto_now=True)
    nome = models.CharField(max_length=255)
    localizacao=models.ForeignKey(Localizacao,verbose_name="Unidade/Setor" ,on_delete=models.CASCADE)
    foto1=models.ImageField(verbose_name="Foto do Item",null=True,blank=True)
    estado=models.ForeignKey(Estado_bem,on_delete=models.CASCADE)
    obs=models.TextField(verbose_name="Observação",null=True,blank=True)
    ativo=models.BooleanField(verbose_name="Item em uso?",default=True)
    descartado =models.BooleanField(verbose_name="Recolhimento?",default=False) 
    valor=MoneyField(max_digits=19, decimal_places=4, null=True, default_currency="BRL")

    def __str__(self):
        return f"{self.RGP} - {self.nome} - {self.localizacao}"
    
@receiver(pre_delete, sender=Material)
def delete_foto1_file(sender, instance, **kwargs):
    if instance.foto1:
        instance.foto1.delete(False)
    
       
