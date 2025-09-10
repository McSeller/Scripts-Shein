import requests
import xlwings as xw
import time
import base64
import hmac
import hashlib
import string
import secrets
import json
from dotenv import dotenv_values
from datetime import datetime

# ==== CONFIGURAÇÕES ====
ARQUIVO_DETALHES = "detalhes_spu.xlsx"
NOME_LOG = f"log_envio_precos_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.txt"
API_HOST = "https://openapi.sheincorp.com"
PATH = "/open-api/openapi-business-backend/product/price/save"

# PEGUE OS DADOS DAS SUAS CHAVES
keys = dotenv_values('.env.keys')
OPEN_KEY = keys["SHEIN_OPEN_KEY"]
SECRET_KEY = keys["SHEIN_SECRET_KEY"]

SITE = "shein-br"        # ajuste conforme necessário
CURRENCY = "BRL"         # ajuste conforme necessário
RISE_REASON = "3"  # ajuste conforme necessário

def gerar_random_key(n=5):
    return ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(n))

def gerar_assinatura(open_key_id, secret_key, path, timestamp, random_key):
    value = f"{open_key_id}&{timestamp}&{path}"
    key = f"{secret_key}{random_key}".encode("utf-8")
    hmac_obj = hmac.new(key, value.encode("utf-8"), hashlib.sha256)
    hmac_hex = hmac_obj.hexdigest()
    hmac_base64 = base64.b64encode(hmac_hex.encode("utf-8")).decode("utf-8")
    return random_key + hmac_base64

def ler_planilha_detalhes():
    app = xw.App(visible=False)
    wb = app.books.open(ARQUIVO_DETALHES)
    sht = wb.sheets[0]
    ultima_linha = sht.range("A" + str(sht.cells.last_cell.row)).end("up").row
    dados = []
    for linha in range(2, ultima_linha+1):
        sku = sht.range(f"C{linha}").value
        preco = sht.range(f"D{linha}").value
        promo = sht.range(f"E{linha}").value
        if not sku or preco is None:
            continue
        try:
            preco = float(preco)
        except:
            continue
        # promo pode ser None ou vazio
        try:
            promo = float(promo)
        except:
            promo = None
        dados.append({
            "sku": str(sku).strip(),
            "preco": preco,
            "promo": promo
        })
    wb.close()
    app.quit()
    return dados

def enviar_precos(lista_precos):
    log = []
    for i in range(0, len(lista_precos), 100):
        lote = lista_precos[i:i+100]
        productPriceList = []
        for item in lote:
            payload = {
                "currencyCode": CURRENCY,
                "productCode": item["sku"],
                "site": SITE,
                "shopPrice": item["preco"],
                "riseReason": RISE_REASON,
            }
            if item["promo"] is not None:
                payload["specialPrice"] = item["promo"]
            productPriceList.append(payload)

        # Gera assinatura e headers
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
        body = {"productPriceList": productPriceList}
        try:
            resp = requests.post(url, headers=headers, json=body, timeout=30)
            resp.raise_for_status()
            data = resp.json()
            log.append(f"Lote {i//100+1}: {len(productPriceList)} produtos enviados")
            log.append(">> Enviado:\n" + json.dumps(body, ensure_ascii=False, indent=2))
            log.append(">> Resposta:\n" + json.dumps(data, ensure_ascii=False, indent=2))
        except Exception as e:
            log.append(f"Erro no envio do lote {i//100+1}: {str(e)}\nEnviado: {body}")

        time.sleep(1)  # segura um pouco entre os lotes
    return log

if __name__ == "__main__":
    lista = ler_planilha_detalhes()
    log = enviar_precos(lista)
    with open(NOME_LOG, "w", encoding="utf-8") as f:
        f.write("\n\n".join(log))
    print(f"Log salvo em {NOME_LOG}")
