from modulos.auth_shein import gerar_link_autorizacao

def main():
    print("=== SHEIN AUTH FLUXO ===")
    print("\n1) Link de autorização (abra no navegador, lojista precisa aceitar):")
    print(gerar_link_autorizacao())

    print("\n2) Após autorização, copie o tempToken da sua redirectUrl e cole aqui.")

if __name__ == "__main__":
    main()
