import requests
import re
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from projeto_busca_cnpjs.settings import EMAIL_HOST_USER
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator




def verificar_whatsapp(numero):
        numero_limpo = re.sub(r'\D', '', numero)
        url = "https://evo2-gcp8.blubots.com/chat/whatsappNumbers/testegabriel"

        payload = {"numbers": [f"55{numero_limpo}"]}
        headers = {
            "apikey": "bb5wil41ltf76p59klk1ko",
            "Content-Type": "application/json"
        }
        response = requests.request("POST", url, json=payload, headers=headers)

        if response.status_code == 200:
            data = response.json()
            return data
            print( "-" * 20)
        else:
            print(f"Erro:{response.status_code}")


def generate_link(user):
    """Função usada pra gerar links personalizados que o usuário recebe no email psra trocar de senha"""
    uid = urlsafe_base64_encode(force_bytes(user.pk)) # gera o uid que vai no link 
    token = default_token_generator.make_token(user) # gera o token que vai no link
    link = f"http://127.0.0.1:8000/accounts/reset/{uid}/{token}/"
    return link 



User = get_user_model()
def email_reset_password(request, to_email):
    """Função que estabele o envio de email já pré-montado pra não ter que ficar criando"""
    User = get_user_model()
    user = User.objects.get(email=to_email)
    link = generate_link(user)

    message = f"Hello\nPlease click the following link: {link}\n\nBest regards, \nYour Team"
    to_email = user.email
    send_mail(
        "Redefinir Senha",
        message,
        EMAIL_HOST_USER,
        [to_email],
        fail_silently=True
    )