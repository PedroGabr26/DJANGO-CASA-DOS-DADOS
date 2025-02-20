from django.shortcuts import render
from django.contrib.auth import authenticate, login
from django.shortcuts import redirect
from django.contrib import messages
from .forms import CreateUsuarioForm,AuthenticateUsuarioForm,CreateFormCnpj,CreateFormBuscaAvancada
import requests
import json
from django.views.generic import ListView
from django.http import JsonResponse 
from django.core.paginator import Paginator
from django.http import QueryDict
from .utils import verificar_whatsapp
# Create your views here.

def authenticate_user(request):
    form = AuthenticateUsuarioForm(data=request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('/home/')
            else:
                form.add_error(request, 'Usuário ou senha incorreto!')
    return render(request,'login.html',{'form':form})    




def create_user(request):
    if request.method == "POST":
        form = CreateUsuarioForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request,'Usuário criado com sucesso!')
            return redirect('/')
    else:
        form = CreateUsuarioForm()
    return render(request,'cadastro.html', {'form':form})




def home(request):
    return render(request,'home.html')




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



class BuscaAvancadaView(ListView):
    template_name = "busca_avancada.html"
    context_object_name = "dados" 
    paginate_by = 10


    def get(self,request,*agrs,**kwargs):
        form = CreateFormBuscaAvancada(request.GET)  # Mudamos para GET
        page_list = request.GET.getlist("page")
        page = int(page_list[-1]) if page_list else 1  # Pega o último valor ou usa 1 se estiver vazio

        if form.is_valid():  
            url = "https://api.casadosdados.com.br/v5/cnpj/pesquisa?tipo_resultado=completo"
            headers = {
                "api-key": "485a4129e6a8763fe42c87b03996ab87b93092727623ddf2763da480588d8ed8f36f7b092cfc5af5ec1b5062b9eac8cd8e2ed9298c95f6f25d2908dd8287012c"
            }
            resultados_por_pagina = 20
            body = {
                "cnpj": [form.cleaned_data.get("cnpj")] if form.cleaned_data.get("cnpj") else [],
                "nome_empresa": [form.cleaned_data.get("nome_fantasia")] if form.cleaned_data.get("nome_fantasia") else [],
                "codigo_atividade_principal": [form.cleaned_data.get("cnae")] if form.cleaned_data.get("cnae") else [],
                "situacao_cadastral": [form.cleaned_data.get("situacao_cadastral")] if form.cleaned_data.get("situacao_cadastral") else [],
                "cep": [form.cleaned_data.get("cep")] if form.cleaned_data.get("cep") else [],
                "estado": [form.cleaned_data.get("estado")] if form.cleaned_data.get("estado") else [],
                "ddd": [form.cleaned_data.get("ddd")] if form.cleaned_data.get("ddd") else [],
                "municipio": [form.cleaned_data.get("municipio")] if form.cleaned_data.get("municipio") else [],
                "bairro": [form.cleaned_data.get("bairro")] if form.cleaned_data.get("bairro") else [],
                "capital_social": {
                    "minimo": form.cleaned_data.get("capital_minimo") if form.cleaned_data.get("capital_minimo") else None,
                    "maximo": form.cleaned_data.get("capital_maximo") if form.cleaned_data.get("capital_maximo") else None
                },
                "mais_filtros": {"com_email": True, "somente_celular": True},
                "pagina": page,
                "limite": resultados_por_pagina
            }

            # Remover campos vazios
            body = {k: v for k, v in body.items() if v not in ([], None, {})}
            
            if "capital_social" in body and not any(body["capital_social"].values()):
                del body["capital_social"]
            
            #print(body)
            total_dados = 0  # Inicialização antes do bloco try
            dados_paginados = []
            try:
                response = requests.post(url, headers=headers, json=body)
                #print("Resposta da API:", response.text)
                if response.status_code == 200:
                    #print("Total de Registros:", total_dados)
                    #print("Dados Paginados:", dados_paginados)
                    dados = response.json()

                    total_dados = dados.get("total", 0)  
                    dados_paginados = dados.get("cnpjs", []) 
                    #passar por cada empresa em dados
                    for empresa in dados_paginados:
                        contatos = empresa.get("contato_telefonico") # pega a chave contato_telefonico referente a todos os resultados
                        empresa['whatsapp'] = []
                        for contato in contatos: # passa por cada um
                            telefone = contato.get("completo") # pega cada telefone
                            if telefone:
                                empresa['whatsapp'].append({
                                    "telefone":telefone,
                                    "whatsapp":verificar_whatsapp(telefone)
                                })
                    total_paginas = (total_dados // resultados_por_pagina) + (1 if total_dados % resultados_por_pagina else 0)
                        
                    if page > total_paginas:
                        page = total_paginas
                    # Paginação manual, se necessário
                    context = {
                        "form":form,
                        "total_registros": total_dados,
                        "pagina_atual": page,
                        "total_paginas": total_paginas,
                        "limite_por_pagina": resultados_por_pagina,
                        "dados": dados_paginados,  # Passando os dados para o template
                        "is_paginated": total_paginas > 1,  # Indica se há paginação
                        "page_obj": {
                            "has_previous": page > 1,
                            "previous_page_number": page - 1 if page > 1 else None,
                            "number": page,
                            "has_next": page < total_paginas,
                            "next_page_number": page + 1 if page < total_paginas else None,
                        },
                        "paginator": {"num_pages": total_paginas},
                    }
                    return render(request,self.template_name,context)
                else:
                    return render(request, self.template_name, {f"{response.status_code}":f"{response.text}"})               
            except requests.exceptions.RequestException as e:
                print("Erro na requisição:", response.text)
                return []
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CreateFormBuscaAvancada(self.request.GET)
        return context
#falta incluir paginacao dinamica
#salvar os resultados na sessão pra paginação dinamica continuar e sempre manter os filtros