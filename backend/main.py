from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import sqlite3
import logging
import time

# --- CONFIGURAÇÃO DE LOGS CORPORATIVOS ---
logging.basicConfig(
    filename="sistema.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    encoding="utf-8"
)

app = FastAPI(title="Sistema de Gestão Full-Stack - Logs Corporativos")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware para registrar automaticamente todas as requisições HTTP
@app.middleware("http")
async def log_requisicoes(request: Request, call_next):
    inicio = time.time()
    resposta = await call_next(request)
    duracao = time.time() - inicio
    logging.info(f"Rota: {request.url.path} | Metodo: {request.method} | Status: {resposta.status_code} | Tempo: {duracao:.4f}s")
    return resposta

def init_db():
    try:
        conn = sqlite3.connect("banco.db")
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS itens (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                quantidade INTEGER NOT NULL
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS logs_automacao (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                moeda TEXT,
                valor REAL,
                data_coleta TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        conn.close()
        logging.info("Banco de dados inicializado com sucesso.")
    except Exception as e:
        logging.error(f"Erro ao inicializar o banco de dados: {e}")

init_db()

class Item(BaseModel):
    nome: str = Field(..., min_length=2, description="O nome deve ter pelo menos 2 caracteres")
    quantidade: int = Field(..., gt=0, description="A quantidade deve ser maior que zero")

@app.get("/api/itens")
def listar_itens():
    try:
        conn = sqlite3.connect("banco.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, nome, quantidade FROM itens")
        rows = cursor.fetchall()
        conn.close()
        return {"status": "Sucesso", "dados": [{"id": r[0], "nome": r[1], "quantidade": r[2]} for r in rows]}
    except Exception as e:
        logging.error(f"Erro ao listar itens: {e}")
        raise HTTPException(status_code=500, detail="Erro interno no servidor.")

@app.post("/api/itens")
def criar_item(item: Item):
    try:
        conn = sqlite3.connect("banco.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO itens (nome, quantidade) VALUES (?, ?)", (item.nome, item.quantidade))
        conn.commit()
        conn.close()
        logging.info(f"Item criado com sucesso: {item.nome} (Qtd: {item.quantidade})")
        return {"mensagem": "Item cadastrado com sucesso!"}
    except Exception as e:
        logging.error(f"Erro ao criar item: {e}")
        raise HTTPException(status_code=500, detail="Erro ao salvar no banco.")

@app.put("/api/itens/{item_id}")
def atualizar_item(item_id: int, item: Item):
    try:
        conn = sqlite3.connect("banco.db")
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE itens SET nome = ?, quantidade = ? WHERE id = ?",
            (item.nome, item.quantidade, item_id)
        )
        conn.commit()
        conn.close()
        logging.info(f"Item {item_id} atualizado com sucesso.")
        return {"mensagem": f"Item {item_id} atualizado com sucesso!"}
    except Exception as e:
        logging.error(f"Erro ao atualizar item {item_id}: {e}")
        raise HTTPException(status_code=500, detail="Erro ao atualizar item.")

@app.delete("/api/itens/{item_id}")
def deletar_item(item_id: int):
    try:
        conn = sqlite3.connect("banco.db")
        cursor = conn.cursor()
        cursor.execute("DELETE FROM itens WHERE id = ?", (item_id,))
        conn.commit()
        conn.close()
        logging.warning(f"Item {item_id} deletado do sistema.")
        return {"mensagem": "Removido com sucesso!"}
    except Exception as e:
        logging.error(f"Erro ao deletar item {item_id}: {e}")
        raise HTTPException(status_code=500, detail="Erro ao excluir item.")

@app.get("/api/logs")
def listar_logs():
    try:
        conn = sqlite3.connect("banco.db")
        cursor = conn.cursor()
        cursor.execute("SELECT moeda, valor, data_coleta FROM logs_automacao ORDER BY id DESC LIMIT 5")
        rows = cursor.fetchall()
        conn.close()
        return {"dados": [{"moeda": r[0], "valor": r[1], "data": r[2]} for r in rows]}
    except Exception as e:
        logging.error(f"Erro ao buscar logs de automação: {e}")
        return {"dados": []}

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Painel Full-Stack - Corporativo</title>
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
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            width: 480px;
            text-align: center;
        }
        h1 { color: #333; font-size: 20px; }
        h3 { color: #0056b3; font-size: 15px; margin-top: 15px; text-align: left; border-bottom: 2px solid #0056b3; padding-bottom: 4px; }
        input, button {
            width: 100%;
            padding: 8px;
            margin-top: 8px;
            border: 1px solid #ccc;
            border-radius: 5px;
            box-sizing: border-box;
        }
        .btn-salvar { background-color: #28a745; color: white; border: none; font-weight: bold; cursor: pointer; }
        .btn-salvar:hover { background-color: #218838; }
        .btn-cancelar { background-color: #6c757d; color: white; border: none; font-weight: bold; cursor: pointer; display: none; margin-top: 5px;}
        .alerta {
            padding: 8px;
            margin-bottom: 10px;
            border-radius: 4px;
            font-size: 12px;
            display: none;
        }
        .alerta-sucesso { background-color: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
        .alerta-erro { background-color: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
        .lista-container {
            text-align: left;
            max-height: 110px;
            overflow-y: auto;
            border: 1px solid #eee;
            background: #f9f9f9;
            padding: 6px;
            border-radius: 4px;
            margin-top: 5px;
            font-size: 13px;
        }
        .item-row {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 4px;
            border-bottom: 1px solid #e5e5e5;
            padding-bottom: 4px;
        }
        .botoes-acao { display: flex; gap: 4px; }
        .btn-editar { background-color: #ffc107; color: black; border: none; padding: 3px 6px; border-radius: 3px; cursor: pointer; font-size: 11px; }
        .btn-excluir { background-color: #dc3545; color: white; border: none; padding: 3px 6px; border-radius: 3px; cursor: pointer; font-size: 11px; }
    </style>
</head>
<body>
    <div class="painel">
        <h1>Dashboard Corporativo</h1>
        
        <div id="mensagemAlerta" class="alerta"></div>

        <h3 id="tituloForm">Cadastrar Novo Item</h3>
        <input type="hidden" id="editandoId" value="">
        <input type="text" id="nomeItem" placeholder="Nome do Produto (Mín. 2 letras)">
        <input type="number" id="qtdItem" placeholder="Quantidade (Maior que 0)">
        <button class="btn-salvar" id="btnSalvar" onclick="salvarItem()">Salvar no Banco</button>
        <button class="btn-cancelar" id="btnCancelar" onclick="limparFormulario()">Cancelar Edição</button>

        <h3>Lista de Estoque</h3>
        <input type="text" id="filtroBusca" placeholder="🔍 Pesquisar produto no estoque..." onkeyup="filtrarEstoque()">
        <div class="lista-container" id="listaItens">Carregando estoque...</div>

        <h3>Monitoramento de Dados (ETL)</h3>
        <div class="lista-container" id="listaLogs">Carregando logs...</div>
    </div>

    <script>
        let listaGlobalItens = [];

        function mostrarAlerta(texto, tipo) {
            const alerta = document.getElementById('mensagemAlerta');
            alerta.innerText = texto;
            alerta.className = "alerta " + (tipo === 'sucesso' ? 'alerta-sucesso' : 'alerta-erro');
            alerta.style.display = "block";
            setTimeout(() => { alerta.style.display = "none"; }, 4000);
        }

        async function carregarTudo() {
            try {
                const resEstoque = await fetch('/api/itens');
                const jsonEstoque = await resEstoque.json();
                listaGlobalItens = jsonEstoque.dados;
                renderizarItens(listaGlobalItens);

                const resLogs = await fetch('/api/logs');
                const jsonLogs = await resLogs.json();
                const containerLogs = document.getElementById('listaLogs');
                
                if (jsonLogs.dados.length === 0) {
                    containerLogs.innerHTML = "<p style='color: #666; text-align: center; margin: 5px;'>Nenhum log.</p>";
                } else {
                    containerLogs.innerHTML = "";
                    jsonLogs.dados.forEach(log => {
                        containerLogs.innerHTML += `<div>📈 <strong>${log.moeda}</strong>: R$ ${log.valor}</div>`;
                    });
                }
            } catch (erro) {
                console.error("Erro:", erro);
            }
        }

        function renderizarItens(itens) {
            const containerEstoque = document.getElementById('listaItens');
            if (itens.length === 0) {
                containerEstoque.innerHTML = "<p style='color: #666; text-align: center; margin: 5px;'>Nenhum item encontrado.</p>";
                return;
            }
            containerEstoque.innerHTML = "";
            itens.forEach(item => {
                containerEstoque.innerHTML += `
                    <div class="item-row">
                        <span>📦 <strong>${item.nome}</strong> (${item.quantidade})</span>
                        <div class="botoes-acao">
                            <button class="btn-editar" onclick="prepararEdicao(${item.id}, '${item.nome}', ${item.quantidade})">Editar</button>
                            <button class="btn-excluir" onclick="excluirItem(${item.id})">Excluir</button>
                        </div>
                    </div>
                `;
            });
        }

        function filtrarEstoque() {
            const termo = document.getElementById('filtroBusca').value.toLowerCase();
            const filtrados = listaGlobalItens.filter(i => i.nome.toLowerCase().includes(termo));
            renderizarItens(filtrados);
        }

        async function salvarItem() {
            const id = document.getElementById('editandoId').value;
            const nome = document.getElementById('nomeItem').value;
            const quantidade = document.getElementById('qtdItem').value;

            if (!nome || !quantidade) {
                mostrarAlerta("Preencha todos os campos!", "erro");
                return;
            }

            if (parseInt(quantidade) <= 0) {
                mostrarAlerta("A quantidade deve ser maior que zero!", "erro");
                return;
            }

            try {
                let resposta;
                if (id === "") {
                    resposta = await fetch('/api/itens', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ nome, quantidade: parseInt(quantidade) })
                    });
                } else {
                    resposta = await fetch(`/api/itens/${id}`, {
                        method: 'PUT',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ nome, quantidade: parseInt(quantidade) })
                    });
                }

                if (resposta.ok) {
                    mostrarAlerta(id === "" ? "Item cadastrado com sucesso!" : "Item atualizado com sucesso!", "sucesso");
                    limparFormulario();
                    carregarTudo();
                } else {
                    mostrarAlerta("Erro de validação nos dados enviados.", "erro");
                }
            } catch (e) {
                mostrarAlerta("Erro de conexão com o servidor.", "erro");
            }
        }

        function prepararEdicao(id, nome, quantidade) {
            document.getElementById('editandoId').value = id;
            document.getElementById('nomeItem').value = nome;
            document.getElementById('qtdItem').value = quantidade;
            document.getElementById('tituloForm').innerText = "Editando Item #" + id;
            document.getElementById('btnSalvar').innerText = "Atualizar Item";
            document.getElementById('btnCancelar').style.display = "block";
        }

        function limparFormulario() {
            document.getElementById('editandoId').value = "";
            document.getElementById('nomeItem').value = "";
            document.getElementById('qtdItem').value = "";
            document.getElementById('tituloForm').innerText = "Cadastrar Novo Item";
            document.getElementById('btnSalvar').innerText = "Salvar no Banco";
            document.getElementById('btnCancelar').style.display = "none";
        }

        async function excluirItem(id) {
            await fetch(`/api/itens/${id}`, { method: 'DELETE' });
            mostrarAlerta("Item removido com sucesso!", "sucesso");
            carregarTudo();
        }

        carregarTudo();
    </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
def home():
    return HTML_TEMPLATE