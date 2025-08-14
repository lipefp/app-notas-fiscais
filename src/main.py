import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QLabel, QVBoxLayout, QWidget, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QHBoxLayout, QHeaderView
)
from PyQt5.QtCore import Qt
import models.db

from models.db import criar_tabela_cliente, salvar_cliente

class CadastroCliente(QWidget):
    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent  # Referência à tela principal
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

        # Atualiza a tabela da tela principal
        if self.parent:
            self.parent.carregar_clientes()
        self.close()  # Fecha a janela de cadastro após salvar


class DetalheCliente(QWidget):
    def __init__(self, cliente, parent=None):
        super().__init__()
        self.parent = parent
        self.cliente = cliente
        self.setWindowTitle("Detalhes do Cliente")
        self.setStyleSheet("""
            QWidget {
                background-color: #f7f7f7;
                font-family: "Segoe UI", "Helvetica Neue", sans-serif;
                font-size: 14px;
                color: #333;
            }
            QLabel {
                font-weight: 500;
                margin-top: 8px;
                margin-bottom: 4px;
            }
            QPushButton {
                background-color: #fff;
                border: 1px solid #ccc;
                border-radius: 6px;
                padding: 6px 14px;
                min-width: 100px;
                margin-top: 12px;
            }
            QPushButton:hover {
                background-color: #eaeaea;
            }
        """)
        layout = QVBoxLayout()
        for campo, valor in zip(
            ["Nome", "Telefone", "Endereço", "Carro", "Placa", "Ano", "KM", "Observações"],
            cliente
        ):
            label = QLabel(f"<b>{campo}:</b> {valor}")
            label.setTextFormat(Qt.RichText)
            layout.addWidget(label)

        self.btn_excluir = QPushButton("Excluir Cliente")
        self.btn_excluir.clicked.connect(self.excluir_cliente)
        layout.addWidget(self.btn_excluir)

        self.setLayout(layout)

    def excluir_cliente(self):
        from models.db import conectar
        conn = conectar()
        cursor = conn.cursor()
        # Exclui pelo nome e telefone (ajuste se tiver ID único)
        cursor.execute(
            "DELETE FROM clientes WHERE nome=? AND telefone=?",
            (self.cliente[0], self.cliente[1])
        )
        conn.commit()
        conn.close()
        if self.parent:
            self.parent.carregar_clientes()
        self.close()

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
        self.setGeometry(100, 100, 1200, 400)

        layout = QVBoxLayout()
        self.setLayout(layout)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(10)

        self.tabela = QTableWidget()
        self.tabela.setColumnCount(8)
        self.tabela.setHorizontalHeaderLabels([
            "Nome", "Telefone", "Endereço", "Carro", "Placa", "Ano", "KM", "Observações"
        ])
        header = self.tabela.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # Nome
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # Telefone
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Endereço
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Carro
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Placa
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)  # Ano
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)  # KM
        header.setSectionResizeMode(7, QHeaderView.Stretch)           # Observações
        layout.addWidget(self.tabela)

        botoes_layout = QHBoxLayout()
        btn_cadastrar = QPushButton("Cadastrar Cliente")
        btn_cadastrar.clicked.connect(self.abrir_cadastro)
        botoes_layout.addWidget(btn_cadastrar)

        btn_nota = QPushButton("Gerar Nota")
        btn_nota.clicked.connect(self.gerar_nota)
        botoes_layout.addWidget(btn_nota)

        btn_sair = QPushButton("Encerrar")
        btn_sair.clicked.connect(self.close)
        botoes_layout.addWidget(btn_sair)

        layout.addLayout(botoes_layout)

        self.carregar_clientes()

        self.tabela.cellDoubleClicked.connect(self.abrir_detalhe_cliente)

    def carregar_clientes(self):
        from models.db import conectar
        conn = conectar()
        cursor = conn.cursor()
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
        self.tabela.setHorizontalScrollMode(QTableWidget.ScrollPerPixel)
        self.tabela.setVerticalScrollMode(QTableWidget.ScrollPerPixel)
        self.tabela.verticalHeader().setVisible(False)
        self.tabela.setShowGrid(False)
        self.tabela.setAlternatingRowColors(True)

    def abrir_cadastro(self):
        self.cadastro = CadastroCliente(parent=self)
        self.cadastro.show()

    def abrir_detalhe_cliente(self, row, column):
        cliente = []
        for col in range(self.tabela.columnCount()):
            item = self.tabela.item(row, col)
            cliente.append(item.text() if item else "")
        self.detalhe = DetalheCliente(cliente, parent=self)
        self.detalhe.show()

    def gerar_nota(self):
        print("Função de gerar nota será implementada...")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    janela = MenuPrincipal()
    janela.show()
    sys.exit(app.exec_())

