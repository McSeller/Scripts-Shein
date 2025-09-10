# modulos/consulta_spu_info.py

import os
import time
import hmac
import hashlib
import base64
import string
import secrets
import requests
import json
import pandas as pd
from dotenv import dotenv_values

# ==== CONFIGURAÇÃO DE CHAVES ====
keys = dotenv_values('.env.keys')
OPEN_KEY = keys["SHEIN_OPEN_KEY"]
SECRET_KEY = keys["SHEIN_SECRET_KEY"]

API_HOST = "https://openapi.sheincorp.com"
PATH = "/open-api/goods/spu-info"
ARQUIVO_EXCEL = "detalhes_spu.xlsx"
ARQUIVO_JSON = "C:\\Users\\Windows\\3D Objects\\Shein\\modulos\\produtos\\skus_shein.json"

# ==== FUNÇÕES AUXILIARES ====
def gerar_random_key(n=5):
    return ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(n))

def gerar_assinatura(open_key_id, secret_key, path, timestamp, random_key):
    value = f"{open_key_id}&{timestamp}&{path}"
    key = f"{secret_key}{random_key}".encode("utf-8")
    hmac_obj = hmac.new(key, value.encode("utf-8"), hashlib.sha256)
    hmac_hex = hmac_obj.hexdigest()
    hmac_base64 = base64.b64encode(hmac_hex.encode("utf-8")).decode("utf-8")
    return random_key + hmac_base64

def ler_spus_arquivo(arquivo_json):
    with open(arquivo_json, encoding="utf-8") as f:
        dados = json.load(f)
    return sorted({x["spuName"] for x in dados if "spuName" in x})

def consultar_spu(spu_name, idiomas=["pt-br"]):
    timestamp = str(int(time.time() * 1000))
    random_key = gerar_random_key()
    assinatura = gerar_assinatura(OPEN_KEY, SECRET_KEY, PATH, timestamp, random_key)
    url = f"{API_HOST}{PATH}"
    headers = {
        "x-lt-openKeyId": OPEN_KEY,
        "x-lt-timestamp": timestamp,
        "x-lt-signature": assinatura,
        "Content-Type": "application/json;charset=UTF-8",
    }
    body = {
        "languageList": idiomas,
        "spuName": spu_name
    }

    resp = requests.post(url, headers=headers, json=body, timeout=30)
    if resp.status_code != 200:
        print(f"[ERRO HTTP] {resp.status_code}: {resp.text}")
        return None

    data = resp.json()
    if data.get("code") != "0":
        print(f"[ERRO API] {data.get('msg')}")
        return None

    return data.get("info", {})

def processar_spus():
    lista_spus = ler_spus_arquivo(ARQUIVO_JSON)
    print(f"Total de SPUs encontrados: {len(lista_spus)}")
    resultados = []
    for spu in lista_spus:
        print(f"Consultando SPU {spu} ...")
        info = consultar_spu(spu)
        if not info:
            continue

        # pegar título multilíngue (primeiro idioma solicitado)
        titulo = ""
        if "productMultiNameList" in info and info["productMultiNameList"]:
            titulo = info["productMultiNameList"][0].get("productName", "")

        skc_list = info.get("skcInfoList", [])
        for skc in skc_list:
            for sku in skc.get("skuInfoList", []):
                skuCode = sku.get("skuCode", "")
                preco_normal = ""
                preco_promocional = ""
                if "priceInfoList" in sku and sku["priceInfoList"]:
                    preco_obj = sku["priceInfoList"][0]
                    preco_normal = preco_obj.get("basePrice", "")
                    preco_promocional = preco_obj.get("specialPrice", "")
                resultados.append({
                    "spuName": spu,
                    "titulo": titulo,
                    "skuCode": skuCode,
                    "basePrice": preco_normal,
                    "specialPrice": preco_promocional
                })
        time.sleep(0.5)

    df = pd.DataFrame(resultados)
    df.to_excel(ARQUIVO_EXCEL, index=False)
    print(f"Arquivo gerado: {ARQUIVO_EXCEL} ({len(df)} linhas)")

# ==== EXECUÇÃO ====
if __name__ == "__main__":
    processar_spus()
