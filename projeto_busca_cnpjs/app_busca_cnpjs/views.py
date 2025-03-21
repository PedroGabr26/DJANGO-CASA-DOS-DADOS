from django.shortcuts import render
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.contrib import messages
from .models import BuscaAvancada
from .forms import CreateUsuarioForm,AuthenticateUsuarioForm,CreateFormCnpj,CreateFormBuscaAvancada
import requests
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from .utils import verificar_whatsapp
from django.contrib.auth.models import User
from .serializers import UserSerializer
from rest_framework import generics,status
from django.shortcuts import get_object_or_404
from app_busca_cnpjs.utils import generate_link,email_reset_password
from rest_framework.response import Response
# Create your views here.

def authenticate_user(request):
    if request.method == "POST":
        form = AuthenticateUsuarioForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('/home/')
            else:
                form.add_error(None, 'Usuário ou senha incorretos!')
        print(form.errors)
    else:
        form = AuthenticateUsuarioForm()
    return render(request, 'login.html', {'form': form})



def create_user(request):
    if request.method == "POST":
        form = CreateUsuarioForm(request.POST)
        email = form.cleaned_data['email']
        if form.is_valid():
            form.save()
            messages.success(request,'Usuário criado com sucesso!')
            return redirect('/')
    else:
        form = CreateUsuarioForm()
        print(form.errors)
    return render(request,'cadastro.html', {'form':form})


# def redefinir_senha(request):
#     return render(request,'check_email.html')


@login_required
def home(request):
    return render(request,'home.html')


@login_required
def busca_cnpj(request):
    if request.method == "POST":
        form = CreateFormCnpj(request.POST)
        if form.is_valid():
            cnpj = form.cleaned_data.get('cnpj')
            api_key = form.cleaned_data.get('api_key')
            url = f"https://api.casadosdados.com.br/v4/cnpj/{cnpj}"
            headers = {
                "api-key": f"{api_key}"
            }
            try:
                response = requests.get(url,headers=headers)
                if response.status_code == 200:
                    dados_cnpj = response.json()
                    return render(request, 'busca_cnpj.html', {'form': form, 'dados_cnpj': dados_cnpj})
                else:
                    messages.error(request,f"Erro: {response.status_code}\nRequisição sem sucesso")
                    return render(request,'busca_cnpj.html',{'form':form})
            except requests.exceptions.RequestException as e:
                messages.error(request,{"mensagem": f"Erro ao conectar à API: {str(e)}"}) # vai exibir essa mensagem no busca_cnpj.html 
                return render(request,'busca_cnpj.html',{'form':form})
    else:
        form = CreateFormCnpj() # o que essa linha quer dizer
    return render(request,'busca_cnpj.html',{'form':form}) # o que é esse 3 parametro



class BuscaAvancadaView(LoginRequiredMixin,ListView):
    template_name = "busca_avancada.html"
    context_object_name = "dados" 
    paginate_by = None
    login_url = '/'
    queryset = None

    def fetch_api_data(self,request,page,form_data=None):  
        url = "https://api.casadosdados.com.br/v5/cnpj/pesquisa?tipo_resultado=completo"
        headers = {
            "api-key": "485a4129e6a8763fe42c87b03996ab87b93092727623ddf2763da480588d8ed8f36f7b092cfc5af5ec1b5062b9eac8cd8e2ed9298c95f6f25d2908dd8287012c"
        }
        resultados_por_pagina = 20

        if form_data is None:
            form = CreateFormBuscaAvancada(request.GET)
            form_data = form.is_valid() and form.cleaned_data or {}
        body = {
            "cnpj": [form_data.get("cnpj")] if form_data.get("cnpj") else [],
            "nome_empresa": [form_data.get("nome_fantasia")] if form_data.get("nome_fantasia") else [],
            "codigo_atividade_principal": [form_data.get("cnae")] if form_data.get("cnae") else [],
            "situacao_cadastral": [form_data.get("situacao_cadastral")] if form_data.get("situacao_cadastral") else [],
            "cep": [form_data.get("cep")] if form_data.get("cep") else [],
            "estado": [form_data.get("estado")] if form_data.get("estado") else [],
            "ddd": [form_data.get("ddd")] if form_data.get("ddd") else [],
            "municipio": [form_data.get("municipio")] if form_data.get("municipio") else [],
            "bairro": [form_data.get("bairro")] if form_data.get("bairro") else [],
            "capital_social": {
                "minimo": form_data.get("capital_minimo") if form_data.get("capital_minimo") else None,
                "maximo": form_data.get("capital_maximo") if form_data.get("capital_maximo") else None
            },
            "mais_filtros": {"com_email": True, "somente_celular": True},
            "pagina": page,
            "limite": resultados_por_pagina
        }
            # Remover campos vazios
        body = {k: v for k, v in body.items() if v != [] and v is not None and v != {}}
        if "capital_social" in body and not any(body["capital_social"].values()):
            del body["capital_social"]
        try:
            response = requests.post(url, headers=headers, json=body)#print("Resposta da API:", response.text)
            if response.status_code == 200:
                dados = response.json()
                total_dados = dados.get("total", 0)  
                dados_paginados = dados.get("cnpjs", []) 
                #passar por cada empresa em dados
                for empresa in dados_paginados:
                    contatos = empresa.get("contato_telefonico", [])
                    empresa['whatsapp'] = []  # Lista para armazenar telefones e status do WhatsApp
                    for contato in contatos:
                        telefone = contato.get("completo")
                        if telefone:
                            empresa['whatsapp'].append({
                                "telefone": telefone,
                                "whatsapp": verificar_whatsapp(telefone)
                            })
                total_paginas = (total_dados // resultados_por_pagina) + (1 if total_dados % resultados_por_pagina else 0)
                if page > total_paginas:
                    page = total_paginas
                    # Paginação manual, se necessário
                return {
                    "total_registros": total_dados,
                    "pagina_atual": page,
                    "total_paginas": total_paginas,
                    "limite_por_pagina": resultados_por_pagina,
                    "dados": dados_paginados,
                    "is_paginated": total_paginas > 1,
                    "page_obj": {
                        "has_previous": page > 1,
                        "previous_page_number": page - 1 if page > 1 else None,
                        "number": page,
                        "has_next": page < total_paginas,
                        "next_page_number": page + 1 if page < total_paginas else None,
                    },
                    "paginator": {"num_pages": total_paginas},
                }
            else:
                return {
                    "error": f"{response.status_code} : {response.text}"}               
        except requests.exceptions.RequestException as e:
            return { "error": f"Erro na requisição:{str(e)}"}
    

    def post(self,request):
        form = CreateFormBuscaAvancada(request.POST)
        page = int(request.GET.get("page",1))
        if form.is_valid():
            context = self.fetch_api_data(request,page,form.cleaned_data)
            if "error" not in context:
                context["form"] = form
                return render(request, self.template_name, context)
            else:
                return render(request, self.template_name, {"form": form, "error": context["error"]})
        return render(request,self.template_name,{"form":form})


    def get(self,request,*args,**kwargs):
        page = int(request.GET.get("page",1))
        context = self.fetch_api_data(request, page)
        context["form"] = CreateFormBuscaAvancada(request.GET)
        return render(request,self.template_name,context)
    


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CreateFormBuscaAvancada(self.request.GET)
        return context
        # context['form'] = CreateFormBuscaAvancada(self.request.GET)
        # return context


# já tem que renderizar a página ao acessar ela
class CheckEmailUser(generics.RetrieveAPIView):
    def get(self,request,*args,**kwargs):
        if request.method == "GET":
            email = request.GET.get('email')
            if email:
                if User.objects.filter(email=email).first(): # Não dava pra tirar o email e fazer a busca só pelo filtro ?
                    to_email = email
                    user = get_object_or_404(User,email=email)
                    link = generate_link(user)
                    if to_email and link:
                        email_reset_password(to_email,link)
                        # mudar a messagem de email enviado pro usuario
                        return Response({'messagem-enviada':True},status=status.HTTP_200_OK)
                else:
                    return Response({'exists':False},status=status.HTTP_404_NOT_FOUND)
            return render(request,'check_email.html')
        else:
            return redirect('check_email')
                



#falta incluir paginacao dinamica
#salvar os resultados na sessão pra paginação dinamica continuar e sempre manter os filtros 