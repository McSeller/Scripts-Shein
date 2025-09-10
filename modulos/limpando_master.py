import pandas as pd

def filter_amazon_rows(input_file: str, output_file: str):
    """
    Lê uma planilha, mantém apenas as linhas onde o campo 'player' é 'Amazon',
    e salva o resultado em um novo arquivo.
    
    Args:
        input_file (str): Caminho do arquivo de entrada (.xlsx ou .csv).
        output_file (str): Caminho do arquivo de saída (.xlsx ou .csv).
    """
    # Detecta o tipo do arquivo
    if input_file.endswith('.xlsx'):
        df = pd.read_excel(input_file)
    elif input_file.endswith('.csv'):
        df = pd.read_csv(input_file)
    else:
        raise ValueError("Arquivo de entrada deve ser .xlsx ou .csv")
    
    # Filtra apenas linhas onde player == 'Shein'
    df_shein = df[df['player'] == 'SHEIN'].reset_index(drop=True)
    
    # Salva o resultado
    if output_file.endswith('.xlsx'):
        df_shein.to_excel(output_file, index=False)
    elif output_file.endswith('.csv'):
        df_shein.to_csv(output_file, index=False)
    else:
        raise ValueError("Arquivo de saída deve ser .xlsx ou .csv")

def main():
    # Exemplo de uso
    input_file = 'planilha_original.xlsx'
    output_file = 'planilha_amazon.xlsx'
    filter_amazon_rows(input_file, output_file)

if __name__ == "__main__":
    main()