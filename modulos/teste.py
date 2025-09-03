import os
import time
import hmac
import hashlib
import base64
import string
import secrets
import requests
from dotenv import load_dotenv, dotenv_values

# load_dotenv()
keys = dotenv_values('.env.keys')

# Carrega as chaves
OPEN_KEY = keys["SHEIN_OPEN_KEY"]          # openKeyId descriptografado (.env.keys)
SECRET_KEY = keys["SHEIN_SECRET_KEY"]      # secretKey descriptografado (.env.keys)

API_HOST = "https://openapi.sheincorp.com"
PATH = "/open-api/goods/product/check-publish-permission"

def gerar_random_key(n=5):
    return ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(n))

def gerar_assinatura(open_key_id, secret_key, path, timestamp, random_key):
    # String a ser assinada: openKeyId&timestamp&path
    value = f"{open_key_id}&{timestamp}&{path}"
    key = f"{secret_key}{random_key}".encode("utf-8")
    hmac_obj = hmac.new(key, value.encode("utf-8"), hashlib.sha256)
    hmac_hex = hmac_obj.hexdigest()
    hmac_base64 = base64.b64encode(hmac_hex.encode("utf-8")).decode("utf-8")
    signature = random_key + hmac_base64
    return signature

def testar_check_publish_permission():
    timestamp = str(int(time.time() * 1000))
    random_key = gerar_random_key()
    assinatura = gerar_assinatura(OPEN_KEY, SECRET_KEY, PATH, timestamp, random_key)
    url = f"{API_HOST}{PATH}"
    headers = {
        "x-lt-openKeyId": OPEN_KEY,
        "x-lt-timestamp": timestamp,
        "x-lt-signature": assinatura,
        "language": "PT",  # ou "EN", se quiser em inglês
        "Content-Type": "application/json"
    }
    print("HEADERS:", headers)
    print("URL:", url)
    response = requests.get(url, headers=headers)
    print("Status:", response.status_code)
    print("Response:", response.text)

if __name__ == "__main__":
    testar_check_publish_permission()
