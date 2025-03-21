from django.urls import path
from .views import CheckEmailUser

urlpatterns = [
    path('',CheckEmailUser.as_view(), name='check_email')
]
