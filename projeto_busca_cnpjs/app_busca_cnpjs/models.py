from django.db import models
from django import forms
from django.contrib.auth.models import User
from validate_docbr import CNPJ
from django.core.exceptions import ValidationError
# Create your models here.

#       Models definimos o modelo base que sera utilizado pra criar o nosso formulario e como os dados serão passados, o tipo deles

#OBS: não criei o modelo Usuario porque estou usando o modelo User do django


def validate_cnpj(value):
    cnpj = CNPJ()
    if not cnpj.validate(value):
        raise ValidationError("Cnpj Inválido")


class PesquisaCnpj(models.Model):
    usuario = models.ForeignKey(User,on_delete=models.CASCADE)
    cnpj = models.CharField(max_length=14,validators=[validate_cnpj])
    api_key = models.CharField(max_length=270)

    def __str__(self):
        return f"{self.cnpj} - {self.usuario.username}"
    





SITUACAO_CADASTRAL_CHOICES = [
    ('',''),
    ("ATIVA", "Ativa"),
    ("INATIVA", "Inativa"),
    ("BAIXADA", "Baixada"),
]

class BuscaAvancada(models.Model):
    usuario = models.ForeignKey(User,on_delete=models.CASCADE)
    cnpj = models.CharField(max_length=14,blank=True,null=True,validators=[validate_cnpj])
    nome_fantasia = models.CharField(blank=True,null=True)
    situacao_cadastral = models.CharField(choices=SITUACAO_CADASTRAL_CHOICES,blank=True,null=True)
    cnae = models.CharField(blank=True,null=True)
    ddd = models.CharField(max_length=2,blank=True,null=True)
    cep = models.PositiveIntegerField(blank=True,null=True)
    uf = models.CharField(blank=True,null=True)
    bairro = models.CharField(blank=True,null=True)
    municipio = models.CharField(blank=True,null=True) 
    capital_minimo = models.DecimalField(max_digits=15,decimal_places=2,blank=True,null=True)
    capital_maximo = models.DecimalField(max_digits=15,decimal_places=2,blank=True,null=True)