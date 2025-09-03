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
from dotenv import load_dotenv, dotenv_values

# Caminho do arquivo de SKUs gerado antes
SKUS_JSON = "modulos/produtos/skus_shein.json"
ARQUIVO_EXCEL = "detalhes_shein.xlsx"

load_dotenv()

keys = dotenv_values('.env.keys')

OPEN_KEY = keys["SHEIN_OPEN_KEY"]
SECRET_KEY = keys["SHEIN_SECRET_KEY"]

API_HOST = "https://openapi.sheincorp.com"
PATH = "/open-api/openapi-business-backend/product/full-detail"

def gerar_random_key(n=5):
    return ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(n))

def gerar_assinatura(open_key_id, secret_key, path, timestamp, random_key):
    value = f"{open_key_id}&{timestamp}&{path}"
    key = f"{secret_key}{random_key}".encode("utf-8")
    hmac_obj = hmac.new(key, value.encode("utf-8"), hashlib.sha256)
    hmac_hex = hmac_obj.hexdigest()
    hmac_base64 = base64.b64encode(hmac_hex.encode("utf-8")).decode("utf-8")
    return random_key + hmac_base64

def ler_skus_arquivo(arquivo_json):
    with open(arquivo_json, encoding="utf-8") as f:
        dados = json.load(f)
    # Garante lista única de SKU codes
    return list({x["skuCode"] for x in dados})

def consultar_detalhes_sku(sku_codes):
    timestamp = str(int(time.time() * 1000))
    random_key = gerar_random_key()
    assinatura = gerar_assinatura(OPEN_KEY, SECRET_KEY, PATH, timestamp, random_key)
    url = f"{API_HOST}{PATH}"
    headers = {
        "x-lt-openKeyId": OPEN_KEY,
        "x-lt-timestamp": timestamp,
        "x-lt-signature": assinatura,
        "Content-Type": "application/json;charset=UTF-8",
        "language": "pt-br"
    }
    body = {
        "skuCodes": sku_codes,
        "language": "pt-br"
    }
    resp = requests.post(url, headers=headers, json=body, timeout=30)
    if resp.status_code != 200:
        print(f"Erro HTTP: {resp.status_code} - {resp.text}")
        return []
    data = resp.json()
    if data.get("code") != "0":
        print("Erro na API:", data.get("msg"), data)
        return []
    return data.get("info", [])

def processar():
    print("Lendo SKUs do arquivo...")
    sku_list = ler_skus_arquivo(SKUS_JSON)
    print(f"Total de SKU codes encontrados: {len(sku_list)}")
    resultados = []
    # Consulta lotes de 100 SKUs
    for i in range(0, len(sku_list), 100):
        lote = sku_list[i:i+100]
        print(f"Consultando lote SKUs {i+1} até {i+len(lote)}...")
        detalhes = consultar_detalhes_sku(lote)
        for item in detalhes:
            # Extrai campos, faz tratamento se faltar algum
            skuCode = item.get("skuCode", "")
            productName = ""
            try:
                # Pode ser dict ou string, depende do idioma do retorno
                if isinstance(item.get("productName"), dict):
                    productName = item["productName"].get("productName", "")
                else:
                    productName = item.get("productName", "")
            except:
                productName = ""
            shopPrice = ""
            specialPrice = ""
            if "currentPrices" in item and item["currentPrices"]:
                price_obj = item["currentPrices"][0]
                shopPrice = price_obj.get("shopPrice", "")
                specialPrice = price_obj.get("specialPrice", "")
            skuDim = item.get("skuDimensionsInfo", {})
            length = skuDim.get("length", "")
            width = skuDim.get("width", "")
            height = skuDim.get("height", "")
            weight = skuDim.get("weight", "")
            resultados.append({
                "skuCode": skuCode,
                "productName": productName,
                "shopPrice": shopPrice,
                "specialPrice": specialPrice,
                "length": length,
                "width": width,
                "height": height,
                "weight": weight
            })
        time.sleep(0.5)  # evitar flood
    
    # Salva no Excel
    df = pd.DataFrame(resultados)
    df.to_excel(ARQUIVO_EXCEL, index=False)
    print(f"Arquivo gerado: {ARQUIVO_EXCEL} ({len(df)} linhas)")

if __name__ == "__main__":
    processar()
