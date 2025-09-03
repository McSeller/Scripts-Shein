import os
import time
import hmac
import hashlib
import base64
import string
import secrets
import requests
from dotenv import load_dotenv
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
from descriptografar import decrypt_KEY

load_dotenv()

# Configurações do ambiente
APP_ID = os.getenv("SHEIN_APP_ID")
APP_SECRET = os.getenv("SHEIN_APP_SECRET")

# URLs dos ambientes
TEST_API_HOST = "https://openapi-test01.sheincorp.cn"
TEST_AUTH_HOST = "openapi-sem-test01.dotfashion.cn"
PROD_API_HOST = "https://openapi.sheincorp.com"
PROD_AUTH_HOST = "openapi-sem.sheincorp.com"

# Escolha o ambiente (TEST ou PROD)
ENVIRONMENT = "PROD"  # Mude para "PROD" quando for para produção

if ENVIRONMENT == "TEST":
    API_HOST = TEST_API_HOST
    AUTH_HOST = TEST_AUTH_HOST
else:
    API_HOST = PROD_API_HOST
    AUTH_HOST = PROD_AUTH_HOST

def gerar_random_key(n=5):
    """Gera uma chave aleatória de n caracteres"""
    return ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(n))

def gerar_assinatura(appid, secret, timestamp, path):
    """
    Gera a assinatura x-lt-signature conforme documentação SHEIN
    Formato: randomKey + base64(hmac-sha256-hex)
    """
    random_key = gerar_random_key()
    
    # String a ser assinada: appid&timestamp&path
    value = f"{appid}&{timestamp}&{path}"
    
    # Chave: secret + randomKey
    key = (secret + random_key).encode("utf-8")
    
    # HMAC-SHA256
    hmac_obj = hmac.new(key, value.encode("utf-8"), hashlib.sha256)
    
    # Converter para hexadecimal
    hmac_hex = hmac_obj.hexdigest()
    
    # Codificar hexadecimal em base64
    hmac_base64 = base64.b64encode(hmac_hex.encode("utf-8")).decode("utf-8")
    
    # Assinatura final: randomKey + base64
    signature = random_key + hmac_base64
    
    print(f"[DEBUG] Random Key: {random_key}")
    print(f"[DEBUG] Value to sign: {value}")
    print(f"[DEBUG] HMAC Hex: {hmac_hex}")
    print(f"[DEBUG] Final Signature: {signature}")
    
    return signature

def criar_link_autorizacao(redirect_url, state="default"):
    """
    Cria o link de autorização para o comerciante
    """
    # Codificar a URL de redirecionamento em base64
    redirect_url_base64 = base64.b64encode(redirect_url.encode("utf-8")).decode("utf-8")
    
    # Montar o link
    auth_link = f"https://{AUTH_HOST}/#/empower?appid={APP_ID}&redirectUrl={redirect_url_base64}&state={state}"
    
    print("\n=== LINK DE AUTORIZAÇÃO ===")
    print(f"Link gerado: {auth_link}")
    print(f"Ambiente: {ENVIRONMENT}")
    print(f"Host de autorização: {AUTH_HOST}")
    print("\nInstruções:")
    print("1. Acesse o link acima no navegador")
    print("2. Faça login e autorize o aplicativo")
    print("3. Após autorizar, você será redirecionado para sua URL com o tempToken")
    print("4. O tempToken estará no final da URL após 'tempToken='")
    print("5. Copie o tempToken e use na função trocar_temp_token()")
    
    return auth_link

def trocar_temp_token(temp_token):
    """
    Troca o tempToken temporário pelas chaves de autorização permanentes
    """
    path = "/open-api/auth/get-by-token"
    timestamp = str(int(time.time() * 1000))

    # Gerar assinatura
    assinatura = gerar_assinatura(APP_ID, APP_SECRET, timestamp, path)

    url = f"{API_HOST}{path}"
    headers = {
        "x-lt-appid": APP_ID,
        "x-lt-timestamp": timestamp,
        "x-lt-signature": assinatura,
        "Content-Type": "application/json; charset=UTF-8",
        "language": "en"
    }

    body = {
        "tempToken": temp_token
    }

    print("\n=== TROCANDO TEMP TOKEN ===")
    print(f"URL: {url}")
    print(f"Headers: {headers}")
    print(f"Body: {body}")

    try:
        response = requests.post(url, headers=headers, json=body, timeout=30)
        print(f"\nStatus Code: {response.status_code}")
        print(f"Response: {response.text}")

        if response.status_code == 200:
            data = response.json()
            if data.get("code") == "0":
                result = data.get("info", {})
                encrypted_key = result.get("secretKey", "")
                open_key = result.get("openKeyId", "")

                print("\n=== CHAVES OBTIDAS COM SUCESSO ===")
                print(f"OpenKey ID: {open_key}")
                print(f"SecretKey (criptografada): {encrypted_key}")

                if encrypted_key:
                    secret_key = decrypt_KEY(APP_SECRET, encrypted_key)
                    print(f"SecretKey (descriptografada): {secret_key}")
                else:
                    secret_key = ""
                    print("[ERRO] secretKey não veio na resposta.")

                # Salvar as chaves
                salvar_chaves(open_key, encrypted_key, secret_key)

                return result
            else:
                print(f"\n[ERRO] Falha na API: {data.get('msg', 'Erro desconhecido')}")
        else:
            print(f"\n[ERRO] HTTP {response.status_code}: {response.text}")

    except requests.exceptions.RequestException as e:
        print(f"\n[ERRO] Erro na requisição: {str(e)}")

    return None

def salvar_chaves(open_key, encrypted_key, secret_key):
    """
    Salva as chaves em um arquivo .env.keys
    """
    with open(".env.keys", "w") as f:
        f.write(f"SHEIN_OPEN_KEY={open_key}\n")
        f.write(f"SHEIN_SECRET_KEY={secret_key}\n")
    
    print("\n✅ Chaves salvas em .env.keys")

def testar_api_com_chaves(open_key):
    """
    Testa uma chamada de API usando as chaves obtidas
    """
    path = "/open-api/order/list"
    timestamp = str(int(time.time() * 1000))
    
    # Gerar assinatura com a nova chave
    assinatura = gerar_assinatura(open_key, timestamp, path)
    
    url = f"{API_HOST}{path}"
    headers = {
        "x-lt-appid": open_key,
        "x-lt-timestamp": timestamp,
        "x-lt-signature": assinatura,
        "Content-Type": "application/json; charset=UTF-8",
        "language": "en"
    }
    
    body = {
        "pageNo": 1,
        "pageSize": 10
    }
    
    print("\n=== TESTANDO API COM NOVAS CHAVES ===")
    response = requests.post(url, headers=headers, json=body, timeout=30)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text[:200]}...")  # Primeiros 200 caracteres

def main():
    """
    Fluxo principal do processo de autorização
    """
    print("=" * 50)
    print("CLIENTE API SHEIN - PROCESSO DE AUTORIZAÇÃO")
    print("=" * 50)
    
    if not APP_ID or not APP_SECRET:
        print("\n[ERRO] Configure SHEIN_APP_ID e SHEIN_APP_SECRET no arquivo .env")
        return
    
    print(f"\nAmbiente: {ENVIRONMENT}")
    print(f"APP_ID: {APP_ID}")
    print(f"APP_SECRET: {'*' * (len(APP_SECRET) - 4)}{APP_SECRET[-4:]}")
    
    while True:
        print("\n=== MENU ===")
        print("1. Gerar link de autorização")
        print("2. Trocar tempToken por chaves")
        print("3. Testar API com chaves existentes")
        print("4. Sair")
        
        opcao = input("\nEscolha uma opção: ").strip()
        
        if opcao == "1":
            redirect_url = "https://www.casametais.com.br"
            state = input("Digite o state (opcional, pressione Enter para 'default'): ").strip() or "default"
            criar_link_autorizacao(redirect_url, state)
            
        elif opcao == "2":
            print("\n⚠️  IMPORTANTE: O tempToken expira em 10 minutos!")
            temp_token = input("Cole o tempToken aqui: ").strip()
            if temp_token:
                trocar_temp_token(temp_token)
            else:
                print("[ERRO] tempToken não pode estar vazio")
                
        elif opcao == "3":
            # Tentar carregar chaves salvas
            try:
                from dotenv import dotenv_values
                keys = dotenv_values(".env.keys")
                open_key = keys.get("SHEIN_OPEN_KEY")
                secret_key = keys.get("SHEIN_SECRET_KEY")
                
                if open_key and secret_key:
                    testar_api_com_chaves(open_key, secret_key)
                else:
                    print("[ERRO] Chaves não encontradas em .env.keys")
            except Exception as e:
                print(f"[ERRO] {str(e)}")
                
        elif opcao == "4":
            print("\nSaindo...")
            break
        else:
            print("\n[ERRO] Opção inválida")

if __name__ == "__main__":
    main()