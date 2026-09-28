import requests
import sqlite3

def coletar_dados_externos():
    url = "https://economia.awesomeapi.com.br/json/last/USD-BRL,EUR-BRL"
    
    try:
        resposta = requests.get(url, timeout=5)
        if resposta.status_code == 200:
            dados = resposta.json()
            dolar = float(dados.get('USDBRL', {}).get('bid', 5.00))
            euro = float(dados.get('EURBRL', {}).get('bid', 5.50))
        else:
            # Fallback de segurança caso a API pública falhe
            dolar, euro = 5.00, 5.50
            
        conn = sqlite3.connect("banco.db")
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS logs_automacao (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                moeda TEXT,
                valor REAL,
                data_coleta TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("INSERT INTO logs_automacao (moeda, valor) VALUES (?, ?)", ("Dólar (USD)", dolar))
        cursor.execute("INSERT INTO logs_automacao (moeda, valor) VALUES (?, ?)", ("Euro (EUR)", euro))
        
        conn.commit()
        conn.close()
        print("✔️ Pipeline ETL executado com sucesso: Dados salvos no banco!")
    except Exception as e:
        print(f"❌ Erro crítico no pipeline de dados: {e}")

if __name__ == "__main__":
    coletar_dados_externos()