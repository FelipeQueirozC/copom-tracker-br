import pandas as pd
import json
import requests
from io import BytesIO

def update_holidays():
    url = "https://www.anbima.com.br/feriados/arqs/feriados_nacionais.xls"
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status() # Garante que o download funcionou

        # O segredo: usamos read_excel com o engine 'xlrd' 
        # para ler o arquivo binário da ANBIMA
        df = pd.read_excel(BytesIO(response.content), engine='xlrd')

        # O arquivo da ANBIMA geralmente tem as datas na primeira coluna
        # e começa com algumas linhas vazias ou de título. 
        # Vamos converter a coluna 'Data' e remover o que não for data.
        df.columns = ['Data', 'Dia da Semana', 'Feriado']
        df['Data'] = pd.to_datetime(df['Data'], errors='coerce')
        df = df.dropna(subset=['Data'])
        
        holidays_list = df['Data'].dt.strftime('%Y-%m-%d').tolist()
        
        output = {
            "last_update": pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S'),
            "holidays": holidays_list
        }
        
        with open('feriados_anbima.json', 'w') as f:
            json.dump(output, f, indent=4)
            
        print(f"Sucesso! {len(holidays_list)} feriados salvos em feriados_anbima.json")
        
    except Exception as e:
        print(f"Erro ao processar: {e}")

if __name__ == "__main__":
    update_holidays()
