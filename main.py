from modulos.trocar_temptoken import trocar_temp_token, testar_api_com_chaves, criar_link_autorizacao
from dotenv import load_dotenv
from modulos.teste import testar_check_publish_permission
from modulos.consulta_produtos import listar_sku_codes
from modulos.puxar_dimensoes import processar
from modulos.consulta_spu_info import processar_spus
from modulos.limpa_historico import excluir_planilha, excluir_json
from modulos.copiar_planilha_master import copiar_planilha
import os

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
    # print(f"APP_ID: {APP_ID}")
    # print(f"APP_SECRET: {'*' * (len(APP_SECRET) - 4)}{APP_SECRET[-4:]}")

    # Excluir uma planilha na raiz
    excluir_planilha("detalhes_shein.xlsx")
    excluir_planilha("detalhes_spu.xlsx")

    # Excluir um JSON dentro da pasta modulos/produtos
    excluir_json("modulos/produtos", "skus_shein.json")
    excluir_json("Tabela Master", "Tabela de Preco Master.xlsx")
    
    while True:
        print("\n=== MENU ===")
        print("1. Gerar link de autorização")
        print("2. Trocar tempToken por chaves")
        print("3. Testar API com chaves existentes")
        print("4. Consultar SKUs")
        print("5. Puxar dimensões")
        print("6. Consultar Preço e Preço Normal")
        print("7. Sair")
        
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
            testar_check_publish_permission()
                
        elif opcao == "4":
            listar_sku_codes()
        elif opcao == "5":
            processar()
        elif opcao == "6":
            # listar_sku_codes()
            # processar_spus()
            copiar_planilha(
                r"\\192.168.1.89\Site\Produtos\Preço\Tabelas Compilada\Comparador\Tabelas Master",
                "Tabela de Preco Master.xlsx",
                "Tabela Master"
            )
        elif opcao == "7":
            print("\nSaindo...")
            break
        else:
            print("\n[ERRO] Opção inválida")

if __name__ == "__main__":
    main()
