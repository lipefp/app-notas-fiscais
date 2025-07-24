import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QLabel, QVBoxLayout, QWidget, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QHBoxLayout
)
import models.db

from models.db import criar_tabela_cliente, salvar_cliente

class CadastroCliente(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("""
    QWidget {
        background-color: #f7f7f7;
        font-family: "Segoe UI", "Helvetica Neue", sans-serif;
        font-size: 14px;
        color: #333;
    }

    QLabel {
        font-weight: 500;
        margin-top: 4px;
    }

    QLineEdit {
        background-color: #ffffff;
        border: 1px solid #ccc;
        border-radius: 6px;
        padding: 6px;
        margin-bottom: 6px;
    }

    QLineEdit:focus {
        border: 1px solid #5c9ded;
        outline: none;
    }

    QPushButton {
        background-color: #ffffff;
        border: 1px solid #ccc;
        border-radius: 6px;
        padding: 6px 14px;
        min-width: 100px;
    }

    QPushButton:hover {
        background-color: #eaeaea;
    }

    QTableWidget {
        background-color: #ffffff;
        border: 1px solid #dcdcdc;
        border-radius: 8px;
        padding: 6px;
        gridline-color: #eee;
    }

    QHeaderView::section {
        background-color: #f0f0f0;
        padding: 6px;
        border: none;
        font-weight: 600;
    }
""")

        self.setWindowTitle("Cadastro de Cliente")
        self.setGeometry(100, 100, 300, 200)

        criar_tabela_cliente()  # Cria a tabela ao iniciar

        # Componentes
        self.nome_label = QLabel("Nome do Cliente:")
        self.nome_input = QLineEdit()

        self.telefone_label = QLabel("Telefone:")
        self.telefone_input = QLineEdit()

        self.endereco_label = QLabel("Endereço:")
        self.endereco_input = QLineEdit()

        self.carro_label = QLabel("Carro:")
        self.carro_input = QLineEdit()

        self.placa_label = QLabel("Placa:")
        self.placa_input = QLineEdit()

        self.ano_label = QLabel("Ano:") 
        self.ano_input = QLineEdit() 

        self.km_label = QLabel("KM:")
        self.km_input = QLineEdit()

        self.obs_label = QLabel("Observações:")
        self.obs_input = QLineEdit()

        self.btn_salvar = QPushButton("Salvar")
        self.btn_salvar.clicked.connect(self.salvar_dados)

        # Layout
        layout = QVBoxLayout()
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(10)
        layout.addWidget(self.nome_label)
        layout.addWidget(self.nome_input)
        layout.addWidget(self.telefone_label)
        layout.addWidget(self.telefone_input)
        layout.addWidget(self.endereco_label)
        layout.addWidget(self.endereco_input)
        layout.addWidget(self.carro_label)
        layout.addWidget(self.carro_input)
        layout.addWidget(self.placa_label)
        layout.addWidget(self.placa_input)
        layout.addWidget(self.ano_label)
        layout.addWidget(self.ano_input)
        layout.addWidget(self.km_label)
        layout.addWidget(self.km_input)
        layout.addWidget(self.obs_label)
        layout.addWidget(self.obs_input)
        layout.addWidget(self.btn_salvar)
      
        self.setLayout(layout)

    def salvar_dados(self):
        nome = self.nome_input.text()
        telefone = self.telefone_input.text()
        endereco = self.endereco_input.text()
        carro = self.carro_input.text()
        placa = self.placa_input.text()
        ano = self.ano_input.text()
        km = self.km_input.text()
        observacoes = self.obs_input.text()

        salvar_cliente(nome, telefone, endereco, carro, placa, ano, km, observacoes)

        # Limpar campos
        self.nome_input.clear()
        self.telefone_input.clear()
        self.endereco_input.clear()
        self.carro_input.clear()
        self.placa_input.clear()
        self.ano_input.clear()
        self.km_input.clear()
        self.obs_input.clear()


class MenuPrincipal(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("""
    QWidget {
        background-color: #f7f7f7;
        font-family: "Segoe UI", "Helvetica Neue", sans-serif;
        font-size: 14px;
        color: #333;
    }

    QLabel {
        font-weight: 500;
        margin-top: 4px;
    }

    QLineEdit {
        background-color: #ffffff;
        border: 1px solid #ccc;
        border-radius: 6px;
        padding: 6px;
        margin-bottom: 6px;
    }

    QLineEdit:focus {
        border: 1px solid #5c9ded;
        outline: none;
    }

    QPushButton {
        background-color: #ffffff;
        border: 1px solid #ccc;
        border-radius: 6px;
        padding: 6px 14px;
        min-width: 100px;
    }

    QPushButton:hover {
        background-color: #eaeaea;
    }

    QTableWidget {
        background-color: #ffffff;
        border: 1px solid #dcdcdc;
        border-radius: 8px;
        padding: 6px;
        gridline-color: #eee;
    }

    QHeaderView::section {
        background-color: #f0f0f0;
        padding: 6px;
        border: none;
        font-weight: 600;
    }
""")

        self.setWindowTitle("Sistema da Oficina")
        self.setGeometry(100, 100, 800, 400)

        layout = QVBoxLayout()
        self.setLayout(layout)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(10)


        self.tabela = QTableWidget()
        self.tabela.setColumnCount(8)
        self.tabela.setColumnWidth(0, 140)  # Nome
        self.tabela.setColumnWidth(1, 100)  # Telefone
        self.tabela.setColumnWidth(2, 180)  # Endereço
        self.tabela.setColumnWidth(3, 100)  # Carro
        self.tabela.setColumnWidth(4, 80)   # Placa
        self.tabela.setColumnWidth(5, 60)   # Ano
        self.tabela.setColumnWidth(6, 80)   # KM
        self.tabela.setColumnWidth(7, 220)  # Observações

        self.tabela.setHorizontalHeaderLabels(["Nome", "Telefone ", "Endereço", "Carro", "Placa", "Ano", "KM", "Observações"
    ])
        self.carregar_clientes()
        layout.addWidget(self.tabela)

        botoes_layout = QHBoxLayout()

        btn_cadastrar = QPushButton("Cadastrar Cliente")
        btn_cadastrar.clicked.connect(self.abrir_cadastro)

        btn_nota = QPushButton("Gerar Nota")
        btn_nota.clicked.connect(self.gerar_nota)

        btn_sair = QPushButton("Encerrar")
        btn_sair.clicked.connect(self.close)

        botoes_layout.addWidget(btn_cadastrar)
        botoes_layout.addWidget(btn_nota)
        botoes_layout.addWidget(btn_sair)

        layout.addLayout(botoes_layout)

    def carregar_clientes(self):
     from models.db import conectar
     conn = conectar()
     cursor = conn.cursor()

    # Agora sem o ID
     cursor.execute("SELECT nome, telefone, endereco, carro, placa, ano, km, observacoes FROM clientes")
     dados = cursor.fetchall()
     self.tabela.setRowCount(len(dados))

     for i, (nome, telefone, endereco, carro, placa, ano, km, observacoes) in enumerate(dados):
         self.tabela.setItem(i, 0, QTableWidgetItem(nome))
         self.tabela.setItem(i, 1, QTableWidgetItem(telefone))
         self.tabela.setItem(i, 2, QTableWidgetItem(endereco))
         self.tabela.setItem(i, 3, QTableWidgetItem(carro))
         self.tabela.setItem(i, 4, QTableWidgetItem(placa))
         self.tabela.setItem(i, 5, QTableWidgetItem(ano))
         self.tabela.setItem(i, 6, QTableWidgetItem(km))
         self.tabela.setItem(i, 7, QTableWidgetItem(observacoes))

     conn.close()
     self.tabela.resizeColumnsToContents()
     self.tabela.resizeRowsToContents()
     self.tabela.horizontalHeader().setStretchLastSection(True)
     self.tabela.setHorizontalScrollMode(QTableWidget.ScrollPerPixel)
     self.tabela.setVerticalScrollMode(QTableWidget.ScrollPerPixel)
     self.tabela.verticalHeader().setVisible(False)  
     self.tabela.setShowGrid(False)  
     self.tabela.setAlternatingRowColors(True)

    def abrir_cadastro(self):
        self.cadastro = CadastroCliente()
        self.cadastro.show()

    def gerar_nota(self):
        print("Função de gerar nota será implementada...")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    janela = MenuPrincipal()
    janela.show()
    sys.exit(app.exec_())

# This code is a simple PyQt5 application for managing a workshop's client database.