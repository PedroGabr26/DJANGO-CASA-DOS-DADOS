from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import PesquisaCnpj,BuscaAvancada

#       Forms a gente define que vamos usar o formulario baseado em um modelo ou no modelo do Django e como o formulario e o campo é visto no site, tanto 

#formulario de criação de usuario 
class CreateUsuarioForm(UserCreationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Usuario'})
    )
    email = forms.CharField(
        widget=forms.EmailInput(attrs={'class':'form-control','placeholder':'Email'})
    )
    password1 = forms.CharField( 
        widget=forms.PasswordInput(attrs={'class':'form-control','placeholder':'Senha'})
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class':'form-control','placeholder':'Repita a senha'})
    )

    def __init__(self, *args, **kwargs):
        super(CreateUsuarioForm, self).__init__(*args, **kwargs)
        self.fields['username'].label = ''
        self.fields['email'].label = ''
        self.fields['password1'].label = ''
        self.fields['password2'].label = ''

    class Meta:
        model = User
        fields = ['username','email','password1','password2']
    
    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Senhas não coincidem !")
        return password2



#formulario de autentitcação de usuario
class AuthenticateUsuarioForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Usuario'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class':'form-control', 'placeholder':'Senha'})
    )

#formulario de consultar um cnpj por vez
class CreateFormCnpj(forms.ModelForm):
    class Meta:
        model = PesquisaCnpj
        exclude = ['usuario']
        fields = ['cnpj','api_key']

        widgets={
        'cnpj':forms.TextInput(attrs={'class':'form-control','placeholder':'Digite o cnpj'}),
        'api_key':forms.TextInput(attrs={'class':'form-control','placeholder':'Digite a chave da api'}),
        }




#formulario de busca avançada
#Definimos as opções que podem ser os valores que o usuario escolher do campo "situacao_cadastral/"
class CreateFormBuscaAvancada(forms.ModelForm):
    cnpj = forms.CharField(max_length=14,label="Cnpj(somente os números)",required=False)
    nome_fantasia = forms.CharField(label="Empresa",required=False)
    situacao_cadastral = forms.ChoiceField(
        label="Situação Cadastral",
        choices = [('','--------')] + BuscaAvancada._meta.get_field('situacao_cadastral').choices,
        required=False)
    cnae = forms.CharField(label="Cnae(somente números)",required=False)
    ddd = forms.CharField(max_length=2,label="DDD",required=False)
    cep = forms.CharField(label="Cep",required=False)
    uf = forms.CharField(label="Sigla do estado",required=False)
    bairro = forms.CharField(label="Bairro",required=False)
    municipio = forms.CharField(label="Municipio",required=False) 
    capital_minimo = forms.IntegerField(min_value=0,label="Capital Mínimo", required=False)
    capital_maximo = forms.IntegerField(min_value=0,label="Capital Máximo", required=False)


    class Meta:
        model = BuscaAvancada
        exclude = ['usuario']
        fields = ['cnpj','nome_fantasia','situacao_cadastral','cnae','ddd','cep','uf','bairro','municipio','capital_minimo','capital_maximo']
        

    def __init__(self,*args, **kwargs):
        super(CreateFormBuscaAvancada,self).__init__(*args, **kwargs)
        if not self.data.get('uf'):
            self.fields['municipio'].required = False # faz com que o campo não seja obrigatório
            self.fields['municipio'].widget = forms.HiddenInput()# esconde o campo do formulario 

