from django.shortcuts import render
from django.contrib.auth import authenticate, login
from django.shortcuts import redirect
from django.contrib import messages
from .forms import UsuarioForm
# Create your views here.

def login_user(request):
    if request.method == "POST":
        username = request.POST.get('username').strip()
        password = request.POST.get('password').strip()
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Usuário ou senha Inválidos!')
    return render(request,'login.html')    



def create_user(request):
    if request.method == "POST":
        form = UsuarioForm(request.POST)
        if form.is_valid():
            form.save()
            messages.sucess('Usuário criado com sucesso')
        else:
            form = UsuarioForm()
    return render(request,'cadastro.html', {'form':form})