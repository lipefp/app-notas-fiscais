import sqlite3

def conectar():
    return sqlite3.connect("data/banco.db")

def criar_tabela_cliente():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            telefone TEXT,
            endereco TEXT
        )
    """)
    conn.commit()
    conn.close()
pass


def salvar_cliente(nome, telefone, endereco):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO clientes (nome, telefone, endereco) VALUES (?, ?, ?)",
                   (nome, telefone, endereco))
    conn.commit()
    conn.close()
pass