import sqlite3
import os
from datetime import datetime

# --- CONFIGURAÇÃO DO CAMINHO DO BANCO ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
DB_NAME = os.path.join(DATA_DIR, "banco.db")

def conectar():
    if not os.path.exists(DATA_DIR):
        try: os.makedirs(DATA_DIR)
        except: return sqlite3.connect("banco.db")
    return sqlite3.connect(DB_NAME)

def criar_tabelas():
    conn = conectar()
    c = conn.cursor()
    
    # Tabela Clientes
    c.execute("""
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT, telefone TEXT, endereco TEXT,
            carro TEXT, placa TEXT, ano TEXT, km TEXT, observacoes TEXT,
            status TEXT DEFAULT 'Aberto'
        )
    """)
    
    # Tabela Histórico
    c.execute("""
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
    
    # Tabela Fechamentos (ESSENCIAL PARA O ERRO QUE VOCÊ TEVE)
    c.execute("""
        CREATE TABLE IF NOT EXISTS fechamentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tipo TEXT,          -- 'Diário' ou 'Mensal'
            periodo TEXT,       -- Ex: '27/11/2025'
            valor REAL,
            data_registro TEXT
        )
    """)
    conn.commit()
    conn.close()

# --- CLIENTES ---
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
        c = conn.cursor()
        c.execute("SELECT id, status, nome, telefone, endereco, carro, placa, ano, km, observacoes FROM clientes")
        dados = c.fetchall()
    except: dados = []
    conn.close()
    return dados

def atualizar_status(id_cliente, novo_status):
    conn = conectar()
    conn.cursor().execute("UPDATE clientes SET status=? WHERE id=?", (novo_status, id_cliente))
    conn.commit()
    conn.close()

def deletar_cliente(id_cliente):
    conn = conectar()
    conn.cursor().execute("DELETE FROM clientes WHERE id=?", (id_cliente,))
    conn.commit()
    conn.close()

# --- HISTÓRICO ---
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
    c = conn.cursor()
    c.execute("SELECT data_servico, itens_json, valor_total FROM historico_servicos WHERE id_cliente=? ORDER BY id DESC", (id_cliente,))
    dados = c.fetchall()
    conn.close()
    return dados

# --- FINANCEIRO (AS FUNÇÕES QUE ESTÃO FALTANDO) ---

def calcular_total_dia(data_str):
    """Soma notas emitidas na data exata."""
    conn = conectar()
    c = conn.cursor()
    c.execute("SELECT SUM(valor_total) FROM historico_servicos WHERE data_servico = ?", (data_str,))
    res = c.fetchone()[0]
    conn.close()
    return res if res else 0.0

def calcular_total_mes(mes, ano):
    """Soma notas emitidas no mês."""
    conn = conectar()
    c = conn.cursor()
    termo = f"%/{mes}/{ano}"
    c.execute("SELECT SUM(valor_total) FROM historico_servicos WHERE data_servico LIKE ?", (termo,))
    res = c.fetchone()[0]
    conn.close()
    return res if res else 0.0

def registrar_fechamento(tipo, periodo, valor):
    conn = conectar()
    agora = datetime.now().strftime("%d/%m/%Y %H:%M")
    conn.cursor().execute("INSERT INTO fechamentos (tipo, periodo, valor, data_registro) VALUES (?, ?, ?, ?)", (tipo, periodo, valor, agora))
    conn.commit()
    conn.close()

def listar_fechamentos():
    conn = conectar()
    c = conn.cursor()
    c.execute("SELECT tipo, periodo, valor, data_registro FROM fechamentos ORDER BY id DESC")
    dados = c.fetchall()
    conn.close()
    return dados

# Garante criação ao importar
criar_tabelas()