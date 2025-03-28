"""
URL configuration for projeto_busca_cnpjs project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from app_busca_cnpjs import views
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('',views.authenticate_user,name='login'),
    path('create/', views.create_user,name='create_user'),
    path('home/',views.home,name='home'),
    path('cnpj/',views.busca_cnpj,name='cnpj'),
    path('busca_avancada/',views.BuscaAvancadaView.as_view(),name='busca_avancada'),
    path('',include('app_busca_cnpjs.urls')),
    path('check-email/',views.CheckEmailUser.as_view(),name='check_email'),
    path('reset/<uidb64>/<token>/',auth_views.PasswordResetConfirmView.as_view(template_name='registration/password_reset_confirm.html'),name='password_reset_confirm'), # funcionando
    path('reset-complete-password/',auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'),name='password_reset_complete')
]
