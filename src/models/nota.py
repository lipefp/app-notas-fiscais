# models/nota.py
from PyQt5.QtWidgets import QDialog, QLabel, QVBoxLayout, QLineEdit, QPushButton, QComboBox, QHBoxLayout, QMessageBox
from PyQt5.QtCore import Qt
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
import os

class NotaDialog(QDialog):
    def __init__(self, clientes):
        super().__init__()
        self.setWindowTitle("Gerar Nota")
        self.setGeometry(300, 200, 400, 320)
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
            QLineEdit, QComboBox {
                background-color: #fff;
                border: 1px solid #ccc;
                border-radius: 6px;
                padding: 6px;
                margin-bottom: 8px;
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

        # Seleção do cliente
        self.cliente_combo = QComboBox()
        for cliente in clientes:
            nome = cliente[0]
            carro = cliente[3]
            placa = cliente[4]
            self.cliente_combo.addItem(f"{nome} - {carro} ({placa})", cliente)
        layout.addWidget(QLabel("Selecione o Cliente:"))
        layout.addWidget(self.cliente_combo)

        # Campos da nota
        self.servico_input = QLineEdit()
        self.servico_input.setPlaceholderText("Serviço realizado")
        layout.addWidget(QLabel("Serviço:"))
        layout.addWidget(self.servico_input)

        self.valor_input = QLineEdit()
        self.valor_input.setPlaceholderText("Valor (R$)")
        layout.addWidget(QLabel("Valor:"))
        layout.addWidget(self.valor_input)

        self.data_input = QLineEdit()
        self.data_input.setPlaceholderText("Data (DD/MM/AAAA)")
        layout.addWidget(QLabel("Data:"))
        layout.addWidget(self.data_input)

        # Botão salvar
        btn_salvar = QPushButton("Salvar Nota")
        btn_salvar.clicked.connect(self.salvar_nota)
        layout.addWidget(btn_salvar)

        self.setLayout(layout)

    def salvar_nota(self):
        cliente = self.cliente_combo.currentData()
        servico = self.servico_input.text()
        valor = self.valor_input.text()
        data = self.data_input.text()

        if not servico or not valor or not data:
            QMessageBox.warning(self, "Atenção", "Preencha todos os campos da nota.")
            return

        nome, telefone, endereco, carro, placa, ano, km, obs = cliente

        nome_pdf = f"nota_{nome.replace(' ', '_')}_{placa}.pdf"
        c = canvas.Canvas(nome_pdf, pagesize=A4)

        y = 800
        c.drawString(50, y, "📋 NOTA DE SERVIÇO - SISTEMA DA OFICINA")
        y -= 30
        c.drawString(50, y, f"Cliente: {nome}")
        y -= 20
        c.drawString(50, y, f"Telefone: {telefone}")
        y -= 20
        c.drawString(50, y, f"Endereço: {endereco}")
        y -= 20
        c.drawString(50, y, f"Carro: {carro} | Placa: {placa} | Ano: {ano} | KM: {km}")
        y -= 30
        c.drawString(50, y, f"Serviços Realizados:")
        y -= 20
        for linha in servico.splitlines():
            c.drawString(60, y, f"- {linha}")
            y -= 20
        y -= 10
        c.drawString(50, y, f"Valor Total: R$ {valor}")
        y -= 30
        c.drawString(50, y, "Assinatura do cliente: ___________________________")

        c.save()

        QMessageBox.information(self, "Sucesso", f"PDF gerado com sucesso:\n{nome_pdf}")
        self.close()
