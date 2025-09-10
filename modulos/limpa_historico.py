import os
import glob

def excluir_planilha(nome_arquivo):
    """Exclui um arquivo Excel na pasta raiz do projeto."""
    caminho = os.path.join(os.getcwd(), nome_arquivo)
    if os.path.exists(caminho):
        os.remove(caminho)
        print(f"Planilha '{nome_arquivo}' excluída com sucesso.")
    else:
        print(f"Planilha '{nome_arquivo}' não encontrada na pasta raiz.")

def excluir_json(pasta, nome_arquivo):
    """Exclui um arquivo JSON dentro de uma pasta específica."""
    caminho = os.path.join(os.getcwd(), pasta, nome_arquivo)
    if os.path.exists(caminho):
        os.remove(caminho)
        print(f"JSON '{nome_arquivo}' excluído da pasta '{pasta}' com sucesso.")
    else:
        print(f"JSON '{nome_arquivo}' não encontrado na pasta '{pasta}'.")

def excluir_txt(padrao):
    arquivos = glob.glob(padrao)
    for arq in arquivos:
        try:
            os.remove(arq)
            print(f"Arquivo excluído: {arq}")
        except Exception as e:
            print(f"Erro ao excluir {arq}: {e}")
