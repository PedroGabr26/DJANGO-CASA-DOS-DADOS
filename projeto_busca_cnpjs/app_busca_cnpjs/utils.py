import requests
import re


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