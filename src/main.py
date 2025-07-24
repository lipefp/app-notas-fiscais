import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QLabel, QVBoxLayout, QWidget, QLineEdit, QPushButton
)
import models.db

from models.db import criar_tabela_cliente, salvar_cliente

class CadastroCliente(QWidget):
    def __init__(self):
        super().__init__()
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

        self.btn_salvar = QPushButton("Salvar")
        self.btn_salvar.clicked.connect(self.salvar_dados)

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.nome_label)
        layout.addWidget(self.nome_input)
        layout.addWidget(self.telefone_label)
        layout.addWidget(self.telefone_input)
        layout.addWidget(self.endereco_label)
        layout.addWidget(self.endereco_input)
        layout.addWidget(self.btn_salvar)

        self.setLayout(layout)

    def salvar_dados(self):
        nome = self.nome_input.text()
        telefone = self.telefone_input.text()
        endereco = self.endereco_input.text()
        salvar_cliente(nome, telefone, endereco)

        # Limpar campos
        self.nome_input.clear()
        self.telefone_input.clear()
        self.endereco_input.clear()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    janela = CadastroCliente()
    janela.show()
    sys.exit(app.exec_())
