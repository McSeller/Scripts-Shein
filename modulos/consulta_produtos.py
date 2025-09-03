import os
import time
import hmac
import hashlib
import base64
import string
import secrets
import requests
import json
from dotenv import load_dotenv, dotenv_values

# load_dotenv()
keys = dotenv_values('.env.keys')

# Carrega as chaves
OPEN_KEY = keys["SHEIN_OPEN_KEY"]          # openKeyId DESCRIPTOGRAFADO (.env.keys)
SECRET_KEY = keys["SHEIN_SECRET_KEY"]      # secretKey DESCRIPTOGRAFADO (.env.keys)

API_HOST = "https://openapi.sheincorp.com"
PATH = "/open-api/openapi-business-backend/product/query"

def gerar_random_key(n=5):
    return ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(n))

def gerar_assinatura(open_key_id, secret_key, path, timestamp, random_key):
    value = f"{open_key_id}&{timestamp}&{path}"
    key = f"{secret_key}{random_key}".encode("utf-8")
    hmac_obj = hmac.new(key, value.encode("utf-8"), hashlib.sha256)
    hmac_hex = hmac_obj.hexdigest()
    hmac_base64 = base64.b64encode(hmac_hex.encode("utf-8")).decode("utf-8")
    return random_key + hmac_base64

def listar_sku_codes():
    page_num = 1
    page_size = 50  # Máx permitido na Shein
    todos_skus = []

    while True:
        timestamp = str(int(time.time() * 1000))
        random_key = gerar_random_key()
        assinatura = gerar_assinatura(OPEN_KEY, SECRET_KEY, PATH, timestamp, random_key)
        url = f"{API_HOST}{PATH}"
        headers = {
            "x-lt-openKeyId": OPEN_KEY,
            "x-lt-timestamp": timestamp,
            "x-lt-signature": assinatura,
            "language": "PT",
            "Content-Type": "application/json"
        }
        body = {
            "pageNum": page_num,
            "pageSize": page_size
        }

        print(f"Buscando página {page_num} ...")
        resp = requests.post(url, headers=headers, json=body, timeout=30)
        if resp.status_code != 200:
            print("Erro HTTP:", resp.status_code, resp.text)
            break
        data = resp.json()
        if data.get("code") != "0":
            print("Erro na API:", data.get("msg"), data)
            break

        info = data.get("info", {})
        produtos = info.get("data", [])
        if not produtos:
            print("Fim da lista.")
            break

        for produto in produtos:
            for sku in produto.get("skuCodeList", []):
                todos_skus.append({
                    "skcName": produto.get("skcName"),
                    "spuName": produto.get("spuName"),
                    "skuCode": sku
                })

        if len(produtos) < page_size:
            print("Todas as páginas processadas.")
            break
        page_num += 1
        time.sleep(0.5)  # evitar flood

    # Salva no arquivo JSON
    os.makedirs("modulos/produtos", exist_ok=True)
    with open("modulos/produtos/skus_shein.json", "w", encoding="utf-8") as f:
        json.dump(todos_skus, f, indent=2, ensure_ascii=False)
    print(f"Salvo {len(todos_skus)} SKUs em skus_shein.json.")

if __name__ == "__main__":
    listar_sku_codes()
