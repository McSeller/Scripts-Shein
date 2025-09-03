import os
import time
import hmac
import hashlib
import base64
import requests
from dotenv import load_dotenv

load_dotenv()

APP_ID = os.getenv("SHEIN_APP_ID")
APP_SECRET = os.getenv("SHEIN_APP_SECRET")
REDIRECT_URL = os.getenv("SHEIN_REDIRECT_URL")
STATE = os.getenv("SHEIN_STATE", "AUTH-SHEIN")

if not APP_ID or not APP_SECRET:
    raise ValueError("⚠️ APP_ID e APP_SECRET precisam estar definidos no .env")

# hosts produção
AUTH_HOST = "https://openapi-sem.sheincorp.com/#/empower"
API_HOST = "https://openapi.sheincorp.com"


def gerar_link_autorizacao():
    """
    Monta o link para o lojista autorizar.
    """
    redirect_b64 = base64.b64encode(REDIRECT_URL.encode("utf-8")).decode("utf-8")
    url = f"{AUTH_HOST}?appid={APP_ID}&redirectUrl={redirect_b64}&state={STATE}"
    return url


def gerar_assinatura(appid: str, secret: str, timestamp: str) -> str:
    """
    Gera assinatura HMAC-SHA256 + Base64
    """
    msg = f"{appid}{timestamp}".encode("utf-8")
    key = secret.encode("utf-8")
    raw = hmac.new(key, msg, hashlib.sha256).digest()
    assinatura = base64.b64encode(raw).decode("utf-8")

    # DEBUG
    print("DEBUG assinatura:")
    print("String assinada:", f"{appid}{timestamp}")
    print("Timestamp:", timestamp)
    print("Assinatura:", assinatura)

    return assinatura
