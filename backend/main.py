from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Sistema de Gestão Full-Stack")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Página HTML integrada direto no Back-end
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sistema de Gestão</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f4f7f6;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
        }
        .painel {
            background-color: white;
            padding: 40px;
            border-radius: 10px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            text-align: center;
        }
        h1 { color: #333; }
        .status {
            margin-top: 20px;
            padding: 15px;
            background-color: #e0f7fa;
            color: #006064;
            border-radius: 5px;
            font-weight: bold;
        }
    </style>
</head>
<body>
    <div class="painel">
        <h1>Meu Primeiro Sistema Full-Stack</h1>
        <p>Abaixo está a resposta em tempo real do nosso servidor:</p>
        <div class="status" id="resultado-api">Conectando ao servidor...</div>
    </div>

    <script>
        async function carregarDados() {
            const painelStatus = document.getElementById('resultado-api');
            try {
                const resposta = await fetch('/api/status');
                const dados = await resposta.json();
                painelStatus.innerHTML = `✔️ <strong>Status:</strong> ${dados.status} <br><br> ⚙️ <strong>Ambiente:</strong> ${dados.ambiente}`;
                painelStatus.style.backgroundColor = '#d4edda';
                painelStatus.style.color = '#155724';
            } catch (erro) {
                painelStatus.innerHTML = "❌ Erro ao conectar com a API.";
                painelStatus.style.backgroundColor = '#f8d7da';
                painelStatus.style.color = '#721c24';
            }
        }
        carregarDados();
    </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
def home():
    return HTML_TEMPLATE

@app.get("/api/status")
def api_status():
    return {"status": "A API está no ar e conectada com sucesso!", "ambiente": "Desenvolvimento"}