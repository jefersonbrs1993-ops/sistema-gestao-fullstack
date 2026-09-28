from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sqlite3

app = FastAPI(title="Sistema de Gestão Full-Stack - CRUD Completo")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def init_db():
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

init_db()

class Item(BaseModel):
    nome: str
    quantidade: int

@app.get("/api/itens")
def listar_itens():
    conn = sqlite3.connect("banco.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, nome, quantidade FROM itens")
    rows = cursor.fetchall()
    conn.close()
    return {"status": "Sucesso", "dados": [{"id": r[0], "nome": r[1], "quantidade": r[2]} for r in rows]}

@app.post("/api/itens")
def criar_item(item: Item):
    conn = sqlite3.connect("banco.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO itens (nome, quantidade) VALUES (?, ?)", (item.nome, item.quantidade))
    conn.commit()
    conn.close()
    return {"mensagem": "Item cadastrado com sucesso!"}

@app.put("/api/itens/{item_id}")
def atualizar_item(item_id: int, item: Item):
    conn = sqlite3.connect("banco.db")
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE itens SET nome = ?, quantidade = ? WHERE id = ?",
        (item.nome, item.quantidade, item_id)
    )
    conn.commit()
    conn.close()
    return {"mensagem": f"Item {item_id} atualizado com sucesso!"}

@app.delete("/api/itens/{item_id}")
def deletar_item(item_id: int):
    conn = sqlite3.connect("banco.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM itens WHERE id = ?", (item_id,))
    conn.commit()
    conn.close()
    return {"mensagem": "Removido com sucesso!"}

@app.get("/api/logs")
def listar_logs():
    conn = sqlite3.connect("banco.db")
    cursor = conn.cursor()
    cursor.execute("SELECT moeda, valor, data_coleta FROM logs_automacao ORDER BY id DESC LIMIT 5")
    rows = cursor.fetchall()
    conn.close()
    return {"dados": [{"moeda": r[0], "valor": r[1], "data": r[2]} for r in rows]}

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Painel Full-Stack - CRUD com Edição</title>
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
            padding: 30px;
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
        .lista-container {
            text-align: left;
            max-height: 140px;
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
        <h1>Dashboard & Estoque</h1>
        
        <h3 id="tituloForm">Cadastrar Novo Item</h3>
        <input type="hidden" id="editandoId" value="">
        <input type="text" id="nomeItem" placeholder="Nome do Produto">
        <input type="number" id="qtdItem" placeholder="Quantidade">
        <button class="btn-salvar" id="btnSalvar" onclick="salvarItem()">Salvar no Banco</button>
        <button class="btn-cancelar" id="btnCancelar" onclick="limparFormulario()">Cancelar Edição</button>

        <div class="lista-container" id="listaItens">Carregando estoque...</div>

        <h3>Monitoramento de Dados (ETL)</h3>
        <div class="lista-container" id="listaLogs">Carregando logs...</div>
    </div>

    <script>
        async function carregarTudo() {
            try {
                const resEstoque = await fetch('/api/itens');
                const jsonEstoque = await resEstoque.json();
                const containerEstoque = document.getElementById('listaItens');
                
                if (jsonEstoque.dados.length === 0) {
                    containerEstoque.innerHTML = "<p style='color: #666; text-align: center; margin: 5px;'>Nenhum item.</p>";
                } else {
                    containerEstoque.innerHTML = "";
                    jsonEstoque.dados.forEach(item => {
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

        async function salvarItem() {
            const id = document.getElementById('editandoId').value;
            const nome = document.getElementById('nomeItem').value;
            const quantidade = document.getElementById('qtdItem').value;

            if (!nome || !quantidade) return alert("Preencha todos os campos!");

            if (id === "") {
                await fetch('/api/itens', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ nome, quantidade: parseInt(quantidade) })
                });
            } else {
                await fetch(`/api/itens/${id}`, {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ nome, quantidade: parseInt(quantidade) })
                });
            }

            limparFormulario();
            carregarTudo();
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