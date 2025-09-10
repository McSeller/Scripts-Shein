# modulos/copiar_planilha.py

import os
import shutil

def copiar_planilha(origem_dir, nome_planilha, destino_dir):
    """
    Copia uma planilha de um diretório para outro.

    :param origem_dir: Caminho da pasta onde está a planilha original.
    :param nome_planilha: Nome exato do arquivo da planilha (ex: "detalhes_spu.xlsx").
    :param destino_dir: Caminho da pasta de destino.
    """
    origem_caminho = os.path.join(origem_dir, nome_planilha)
    destino_caminho = os.path.join(destino_dir, nome_planilha)

    if not os.path.exists(origem_caminho):
        print(f"⚠️ Arquivo '{nome_planilha}' não encontrado em '{origem_dir}'.")
        return

    os.makedirs(destino_dir, exist_ok=True)

    shutil.copy2(origem_caminho, destino_caminho)
    print(f"✅ Planilha '{nome_planilha}' copiada para '{destino_dir}'.")
