# Generated by Django 5.1.5 on 2025-02-11 16:45

import app_busca_cnpjs.models
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_busca_cnpjs', '0004_alter_pesquisacnpj_cnpj'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='BuscaAvancada',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cnpj', models.CharField(blank=True, max_length=14, null=True, validators=[app_busca_cnpjs.models.validate_cnpj])),
                ('nome_fantasia', models.CharField(blank=True, null=True)),
                ('situacao_cadastral', models.CharField(blank=True, choices=[('', ''), ('ATIVA', 'Ativa'), ('INATIVA', 'Inativa'), ('BAIXADA', 'Baixada')], null=True)),
                ('cnae', models.CharField(blank=True, null=True)),
                ('ddd', models.CharField(blank=True, max_length=2, null=True)),
                ('cep', models.PositiveIntegerField(blank=True, null=True)),
                ('estado', models.CharField(blank=True, null=True)),
                ('bairro', models.CharField(blank=True, null=True)),
                ('municipio', models.CharField(blank=True, null=True)),
                ('capital_minimo', models.DecimalField(blank=True, decimal_places=2, max_digits=15, null=True)),
                ('capital_maximo', models.DecimalField(blank=True, decimal_places=2, max_digits=15, null=True)),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
