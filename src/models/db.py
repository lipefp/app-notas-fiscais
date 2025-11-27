import sqlite3
import os

# --- CONFIGURAÇÃO DO CAMINHO DO BANCO ---
# Pega o caminho absoluto da pasta onde o projeto está rodando
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Define a pasta 'data' dentro do projeto
DATA_DIR = os.path.join(BASE_DIR, "data")
# Define o nome do arquivo final
DB_NAME = os.path.join(DATA_DIR, "banco.db")

def conectar():
    """Conecta ao banco de dados, criando a pasta 'data' se necessário."""
    # Se a pasta 'data' não existir, cria ela agora
    if not os.path.exists(DATA_DIR):
        try:
            os.makedirs(DATA_DIR)
        except OSError as e:
            print(f"Erro ao criar pasta data: {e}")
            # Fallback: se falhar criar pasta, salva na raiz mesmo
            return sqlite3.connect("banco.db")
            
    return sqlite3.connect(DB_NAME)

def criar_tabelas():
    """Cria as tabelas se não existirem."""
    conn = conectar()
    cursor = conn.cursor()
    
    # Tabela Clientes
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT, telefone TEXT, endereco TEXT,
            carro TEXT, placa TEXT, ano TEXT, km TEXT, observacoes TEXT,
            status TEXT DEFAULT 'Aberto'
        )
    """)
    
    # Tabela Histórico
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS historico_servicos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_cliente INTEGER,
            data_servico TEXT,
            itens_json TEXT,
            valor_total REAL,
            arquivo_path TEXT,
            FOREIGN KEY(id_cliente) REFERENCES clientes(id)
        )
    """)
    conn.commit()
    conn.close()

# --- Funções de Clientes ---
def salvar_cliente(nome, telefone, endereco, carro, placa, ano, km, observacoes):
    conn = conectar()
    conn.cursor().execute("""
        INSERT INTO clientes (nome, telefone, endereco, carro, placa, ano, km, observacoes, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'Aberto')
    """, (nome, telefone, endereco, carro, placa, ano, km, observacoes))
    conn.commit()
    conn.close()

def listar_clientes():
    conn = conectar()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, status, nome, telefone, endereco, carro, placa, ano, km, observacoes FROM clientes")
        dados = cursor.fetchall()
    except:
        dados = []
    conn.close()
    return dados

def atualizar_status(id_cliente, novo_status):
    conn = conectar()
    conn.cursor().execute("UPDATE clientes SET status = ? WHERE id = ?", (novo_status, id_cliente))
    conn.commit()
    conn.close()

def deletar_cliente(id_cliente):
    conn = conectar()
    conn.cursor().execute("DELETE FROM clientes WHERE id = ?", (id_cliente,))
    conn.commit()
    conn.close()

# --- Funções de Histórico e Financeiro ---
def salvar_historico(id_cliente, data, itens_json, total, arquivo):
    conn = conectar()
    conn.cursor().execute("""
        INSERT INTO historico_servicos (id_cliente, data_servico, itens_json, valor_total, arquivo_path)
        VALUES (?, ?, ?, ?, ?)
    """, (id_cliente, data, itens_json, total, arquivo))
    conn.commit()
    conn.close()

def listar_historico(id_cliente):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT data_servico, itens_json, valor_total FROM historico_servicos WHERE id_cliente = ? ORDER BY id DESC", (id_cliente,))
    dados = cursor.fetchall()
    conn.close()
    return dados

def obter_total_financeiro():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT SUM(valor_total) FROM historico_servicos")
    res = cursor.fetchone()[0]
    conn.close()
    return res if res else 0.0

# --- AUTO-INICIALIZAÇÃO ---
# Executa a criação das tabelas automaticamente quando este arquivo é importado.
# Isso evita o erro "no such table" mesmo se o main.py esquecer de chamar.
criar_tabelas()