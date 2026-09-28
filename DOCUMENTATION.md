# 🚀 Documentação Técnica: Sistema de Gestão Full-Stack & ETL

## 📌 Visão Geral do Projeto
Este repositório contém uma aplicação **Full-Stack** desenvolvida para fins de engenharia de software, unindo um back-end robusto em API, persistência relacional em banco de dados, automação de dados em tempo real (ETL) e uma interface web moderna baseada em componentes assíncronos.

---

## 🏗️ Arquitetura e Componentes

### 1. Back-end (FastAPI)
* **Framework:** FastAPI (Python)
* **Funcionalidade:** Responsável por expor rotas RESTful para comunicação HTTP de alta performance.
* **Segurança e Comunicação:** Configuração de `CORSMiddleware` para permitir integração livre entre a interface e o servidor, além de validação de carga de dados com **Pydantic** (`BaseModel`).

### 2. Banco de Dados (SQLite)
* **Tecnologia:** SQLite3 nativo do Python (`banco.db`).
* **Estrutura de Tabelas:**
  * `itens`: Gerencia o inventário (ID autoincrementável, nome do produto e quantidade).
  * `logs_automacao`: Armazena o histórico de coletas de dados de mercado (moedas e cotações).

### 3. Pipeline de Automação (ETL - Extract, Transform, Load)
* **Mecanismo:** Script independente (`etl.py`).
* **Extração:** Consome APIs públicas de economia em tempo real via biblioteca `requests`.
* **Transformação e Carga:** Trata exceções com blocos `try/except` para garantir resiliência e grava os dados coletados de forma persistente no banco de dados SQLite.

### 4. Front-end Integrado
* **Tecnologia:** HTML5, CSS3 estruturado em painel responsivo e JavaScript assíncrono (`async/await` com `fetch`).
* **Operações (CRUD Completo):**
  * **Create (POST):** Cadastro assíncrono de novos itens no estoque.
  * **Read (GET):** Listagem em tempo real dos itens e logs de automação.
  * **Update (PUT):** Manipulação e edição dinâmica de registros utilizando formulários inteligentes.
  * **Delete (DELETE):** Remoção instantânea de registros do banco.

---

## 🔄 Como Executar o Projeto Localmente

1. Clone o repositório:
   ```bash
   git clone [https://github.com/jefersonbrs1993-ops/sistema-gestao-fullstack.git](https://github.com/jefersonbrs1993-ops/sistema-gestao-fullstack.git)
   cd sistema-gestao-fullstack