from django.db import models
from django import forms
from django.contrib.auth.models import User
# Create your models here.
    
class PesquisaCnpj(models.Model):
    usuario = models.ForeignKey(User,on_delete=models.CASCADE)
    cnpj = models.PositiveIntegerField()

