import sys
import os
import json
from datetime import datetime

from PyQt5.QtWidgets import (
    QApplication, QLabel, QVBoxLayout, QWidget, QLineEdit, QPushButton, 
    QTableWidget, QTableWidgetItem, QHBoxLayout, QHeaderView, QDialog, 
    QDialogButtonBox, QFileDialog, QMessageBox, QAbstractItemView,
    QComboBox, QFrame, QGridLayout
)
from PyQt5.QtGui import QIntValidator, QColor, QFont
from PyQt5.QtCore import Qt

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors

import models.db as db
from models.db import conectar, salvar_cliente

# =============================================================================
# ESTILO GLOBAL (CSS) - TEMA CLEAN / MACOS INSPIRED
# =============================================================================
STYLESHEET = """
    /* Fundo Geral */
    QWidget {
        background-color: #FFFFFF;
        color: #333333;
        font-family: "Segoe UI", "Helvetica Neue", Arial, sans-serif;
        font-size: 14px;
    }

    /* Janelas Modais */
    QDialog {
        background-color: #FFFFFF;
    }

    /* Campos de Texto e Combobox */
    QLineEdit, QComboBox {
        background-color: #F5F5F7;
        border: 1px solid #E5E5EA;
        border-radius: 8px;
        padding: 8px 12px;
        color: #1D1D1F;
    }
    QLineEdit:focus, QComboBox:focus {
        border: 1px solid #007AFF;
        background-color: #FFFFFF;
    }

    /* Tabelas */
    QTableWidget {
        border: 1px solid #E5E5EA;
        border-radius: 10px;
        gridline-color: #F0F0F0;
        background-color: #FFFFFF;
        selection-background-color: #E3F2FD;
        selection-color: #1D1D1F;
    }
    QHeaderView::section {
        background-color: #F5F5F7;
        border: none;
        border-bottom: 1px solid #E5E5EA;
        padding: 10px;
        font-weight: bold;
        color: #666666;
    }

    /* Botões Padrão (Cinza Suave) */
    QPushButton {
        background-color: #F5F5F7;
        border: 1px solid #E5E5EA;
        border-radius: 8px;
        padding: 8px 16px;
        color: #1D1D1F;
        font-weight: 500;
    }
    QPushButton:hover {
        background-color: #EBEBEB;
        border-color: #D1D1D6;
    }
    QPushButton:pressed {
        background-color: #DEDEDE;
    }

    /* Botões de Destaque (Azul) */
    QPushButton[class="primary"] {
        background-color: #007AFF;
        color: white;
        border: none;
    }
    QPushButton[class="primary"]:hover {
        background-color: #0062CC;
    }
    
    /* Botões de Sucesso (Verde) */
    QPushButton[class="success"] {
        background-color: #34C759;
        color: white;
        border: none;
    }
    QPushButton[class="success"]:hover {
        background-color: #2DB84C;
    }

    /* Botões de Perigo (Vermelho Suave) */
    QPushButton[class="danger"] {
        background-color: #FFF2F2;
        color: #D32F2F;
        border: 1px solid #FFCDD2;
    }
    QPushButton[class="danger"]:hover {
        background-color: #FFEBEE;
        border-color: #EF9A9A;
    }

    /* Labels de Título */
    QLabel[class="titulo"] {
        font-size: 22px;
        font-weight: bold;
        color: #1D1D1F;
        margin-bottom: 15px;
    }
    
    /* Labels Financeiros */
    QLabel[class="card-value"] { font-size: 24px; font-weight: bold; color: #2E7D32; }
    QLabel[class="card-title"] { font-size: 14px; color: #666; font-weight: 600; }
    QFrame[class="card"] { 
        background-color: #FAFAFA; border: 1px solid #EEEEEE; border-radius: 12px; 
    }
"""

# =============================================================================
# FUNÇÕES DE CONFIGURAÇÃO
# =============================================================================
def verificar_banco_historico():
    """Garante que as tabelas existam."""
    try:
        conn = conectar()
        cursor = conn.cursor()
        
        # Histórico
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS historico_servicos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                id_cliente INTEGER,
                data_servico TEXT,
                itens_json TEXT,
                valor_total REAL,
                arquivo_path TEXT
            )
        """)
        
        # Fechamentos
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS fechamentos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tipo TEXT,
                periodo TEXT,
                valor REAL,
                data_registro TEXT
            )
        """)

        try:
            cursor.execute("SELECT status FROM clientes LIMIT 1")
        except:
            cursor.execute("ALTER TABLE clientes ADD COLUMN status TEXT DEFAULT 'Aberto'")
            
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Erro ao verificar banco: {e}")

# =============================================================================
# JANELAS AUXILIARES
# =============================================================================

class DialogoHistorico(QDialog):
    def __init__(self, id_cliente, nome_cliente, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Histórico - {nome_cliente}")
        self.resize(700, 500)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        
        lbl = QLabel(f"Histórico de Serviços")
        lbl.setProperty("class", "titulo")
        layout.addWidget(lbl)
        
        self.tabela = QTableWidget()
        self.tabela.setColumnCount(3)
        self.tabela.setHorizontalHeaderLabels(["Data", "Resumo", "Total"])
        self.tabela.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.tabela.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tabela.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tabela.setAlternatingRowColors(True)
        self.tabela.setShowGrid(False)
        layout.addWidget(self.tabela)
        
        btn = QPushButton("Fechar")
        btn.setCursor(Qt.PointingHandCursor)
        btn.clicked.connect(self.close)
        layout.addWidget(btn, alignment=Qt.AlignRight)
        
        self.setLayout(layout)
        self.carregar_dados(id_cliente)

    def carregar_dados(self, id_cliente):
        dados = db.listar_historico(id_cliente)
        self.tabela.setRowCount(len(dados))
        for i, (data, itens_json, valor) in enumerate(dados):
            self.tabela.setItem(i, 0, QTableWidgetItem(data))
            try:
                lista = json.loads(itens_json)
                resumo = ", ".join([item[1] for item in lista])
            except: resumo = "-"
            self.tabela.setItem(i, 1, QTableWidgetItem(resumo))
            self.tabela.setItem(i, 2, QTableWidgetItem(f"R$ {valor:,.2f}"))
        conn.close()

class DialogoFinanceiro(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Gestão Financeira")
        self.resize(850, 600)
        
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(25, 25, 25, 25)
        
        lbl_tit = QLabel("Painel Financeiro")
        lbl_tit.setProperty("class", "titulo")
        layout.addWidget(lbl_tit)
        
        # --- ÁREA DE CARDS (DIA E MÊS) ---
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(20)
        
        # Card Dia
        self.card_dia = self.criar_card("Hoje", "R$ 0,00", "Fechar Caixa do Dia", self.fechar_dia)
        cards_layout.addWidget(self.card_dia)
        
        # Card Mês
        self.card_mes = self.criar_card("Mês Atual", "R$ 0,00", "Encerrar Mês", self.fechar_mes)
        cards_layout.addWidget(self.card_mes)
        
        layout.addLayout(cards_layout)
        
        # --- TABELA DE REGISTROS ---
        layout.addWidget(QLabel("Histórico de Fechamentos:", styleSheet="font-weight: bold; margin-top: 15px; font-size: 16px; color: #333;"))
        
        self.tabela = QTableWidget(0, 4)
        self.tabela.setHorizontalHeaderLabels(["Tipo", "Período", "Valor Fechado", "Data do Registro"])
        self.tabela.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self.tabela.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tabela.setAlternatingRowColors(True)
        self.tabela.setShowGrid(False)
        self.tabela.verticalHeader().setVisible(False)
        layout.addWidget(self.tabela)
        
        btn_close = QPushButton("Sair")
        btn_close.setCursor(Qt.PointingHandCursor)
        btn_close.clicked.connect(self.close)
        layout.addWidget(btn_close, alignment=Qt.AlignRight)
        
        self.setLayout(layout)
        self.atualizar_dados()

    def criar_card(self, titulo, valor_inicial, texto_botao, funcao_botao):
        frame = QFrame()
        frame.setProperty("class", "card")
        l = QVBoxLayout(frame)
        l.setContentsMargins(20, 20, 20, 20)
        l.setSpacing(10)
        
        lbl_t = QLabel(titulo)
        lbl_t.setProperty("class", "card-title")
        
        lbl_v = QLabel(valor_inicial)
        lbl_v.setProperty("class", "card-value")
        lbl_v.setAlignment(Qt.AlignCenter)
        
        btn = QPushButton(texto_botao)
        btn.setProperty("class", "primary")
        btn.setCursor(Qt.PointingHandCursor)
        btn.clicked.connect(funcao_botao)
        
        l.addWidget(lbl_t, alignment=Qt.AlignCenter)
        l.addWidget(lbl_v, alignment=Qt.AlignCenter)
        l.addWidget(btn)
        
        frame.lbl_valor = lbl_v 
        return frame

    def atualizar_dados(self):
        # Card Dia
        hoje = datetime.now().strftime("%d/%m/%Y")
        total_dia = db.calcular_total_dia(hoje)
        self.card_dia.lbl_valor.setText(f"R$ {total_dia:,.2f}")
        
        # Card Mês
        mes = datetime.now().strftime("%m")
        ano = datetime.now().strftime("%Y")
        total_mes = db.calcular_total_mes(mes, ano)
        self.card_mes.lbl_valor.setText(f"R$ {total_mes:,.2f}")
        
        # Tabela com Correção de Desempacotamento (Robustez)
        registros = db.listar_fechamentos()
        self.tabela.setRowCount(len(registros))
        for i, row in enumerate(registros):
            # Aqui está a correção: pegamos apenas os 4 primeiros itens, independente de quantos vierem
            # Isso previne o erro "too many values to unpack"
            if len(row) >= 4:
                tipo, periodo, valor, data_reg = row[:4]
                
                self.tabela.setItem(i, 0, QTableWidgetItem(tipo))
                self.tabela.setItem(i, 1, QTableWidgetItem(periodo))
                
                item_val = QTableWidgetItem(f"R$ {valor:,.2f}")
                item_val.setForeground(QColor("#2E7D32")) # Verde
                self.tabela.setItem(i, 2, item_val)
                self.tabela.setItem(i, 3, QTableWidgetItem(data_reg))

    def fechar_dia(self):
        hoje = datetime.now().strftime("%d/%m/%Y")
        valor = db.calcular_total_dia(hoje)
        
        if valor == 0:
            QMessageBox.warning(self, "Aviso", "Não há faturamento hoje para fechar.")
            return

        msg = QMessageBox.question(self, "Confirmar Fechamento", 
                                   f"Deseja fechar o caixa de HOJE ({hoje})?\n\nValor Total: R$ {valor:,.2f}",
                                   QMessageBox.Yes | QMessageBox.No)
        
        if msg == QMessageBox.Yes:
            db.registrar_fechamento("Diário", hoje, valor)
            QMessageBox.information(self, "Sucesso", "Caixa diário fechado e registrado!")
            self.atualizar_dados()

    def fechar_mes(self):
        mes_ano = datetime.now().strftime("%m/%Y")
        mes = datetime.now().strftime("%m")
        ano = datetime.now().strftime("%Y")
        valor = db.calcular_total_mes(mes, ano)
        
        if valor == 0:
            QMessageBox.warning(self, "Aviso", "Não há faturamento neste mês.")
            return

        msg = QMessageBox.question(self, "Confirmar Fechamento", 
                                   f"Deseja encerrar o caixa do MÊS ({mes_ano})?\n\nValor Total: R$ {valor:,.2f}",
                                   QMessageBox.Yes | QMessageBox.No)
        
        if msg == QMessageBox.Yes:
            db.registrar_fechamento("Mensal", mes_ano, valor)
            QMessageBox.information(self, "Sucesso", "Caixa mensal encerrado e registrado!")
            self.atualizar_dados()

class DialogoSelecionarCliente(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Nova Nota")
        self.resize(700, 450)
        self.cliente_selecionado = None 

        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        
        lbl = QLabel("Selecione o Cliente")
        lbl.setProperty("class", "titulo")
        layout.addWidget(lbl)
        
        self.tabela = QTableWidget()
        self.tabela.setColumnCount(5)
        self.tabela.setHorizontalHeaderLabels(["Nome", "Telefone", "Carro", "Placa", "Ano"])
        self.tabela.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tabela.setSelectionMode(QAbstractItemView.SingleSelection)
        self.tabela.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tabela.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabela.setShowGrid(False)
        self.tabela.setAlternatingRowColors(True)
        layout.addWidget(self.tabela)
        
        self.carregar_clientes()
        
        btns = QHBoxLayout()
        btn_ok = QPushButton("Confirmar")
        btn_ok.setProperty("class", "primary")
        btn_ok.setCursor(Qt.PointingHandCursor)
        btn_ok.clicked.connect(self.confirmar)
        
        btn_cancel = QPushButton("Cancelar")
        btn_cancel.clicked.connect(self.reject)
        
        btns.addStretch()
        btns.addWidget(btn_cancel)
        btns.addWidget(btn_ok)
        layout.addLayout(btns)
        self.setLayout(layout)

    def carregar_clientes(self):
        dados = db.listar_clientes()
        self.tabela.setRowCount(len(dados))
        for i, row in enumerate(dados):
            item_nome = QTableWidgetItem(str(row[2]))
            item_nome.setData(Qt.UserRole, row[0])
            self.tabela.setItem(i, 0, item_nome)
            self.tabela.setItem(i, 1, QTableWidgetItem(str(row[3])))
            self.tabela.setItem(i, 2, QTableWidgetItem(str(row[5])))
            self.tabela.setItem(i, 3, QTableWidgetItem(str(row[6])))
            self.tabela.setItem(i, 4, QTableWidgetItem(str(row[7])))

    def confirmar(self):
        r = self.tabela.currentRow()
        if r < 0: 
            QMessageBox.warning(self, "Aviso", "Selecione um cliente da lista.")
            return
        self.cliente_selecionado = {
            "id": self.tabela.item(r, 0).data(Qt.UserRole),
            "nome": self.tabela.item(r, 0).text(),
            "telefone": self.tabela.item(r, 1).text(),
            "carro": self.tabela.item(r, 2).text(),
            "placa": self.tabela.item(r, 3).text()
        }
        self.accept()
    
    def get_dados(self): return self.cliente_selecionado

class DialogoServico(QDialog):
    def __init__(self, cliente, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Emitir Nota")
        self.resize(800, 600)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Cabeçalho com Card
        card = QFrame()
        card.setProperty("class", "card")
        l_card = QVBoxLayout(card)
        lbl_cli = QLabel(f"{cliente['nome']}")
        lbl_cli.setStyleSheet("font-size: 18px; font-weight: bold; color: #1D1D1F;")
        lbl_det = QLabel(f"{cliente['carro']} • {cliente['placa']}")
        lbl_det.setStyleSheet("font-size: 14px; color: #6e6e73;")
        
        l_card.addWidget(lbl_cli)
        l_card.addWidget(lbl_det)
        layout.addWidget(card)
        
        layout.addWidget(QLabel("Itens do Serviço"))
        
        self.tabela = QTableWidget(0, 3)
        self.tabela.setHorizontalHeaderLabels(["Qtd", "Descrição", "Valor Unit. (R$)"])
        self.tabela.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.tabela.setAlternatingRowColors(True)
        self.tabela.setShowGrid(False)
        layout.addWidget(self.tabela)
        
        # Botões de Ação da Tabela
        h_act = QHBoxLayout()
        btn_add = QPushButton("+ Adicionar Item")
        btn_add.setCursor(Qt.PointingHandCursor)
        btn_add.clicked.connect(self.add_item)
        
        btn_rem = QPushButton("Remover Selecionado")
        btn_rem.setProperty("class", "danger")
        btn_rem.setCursor(Qt.PointingHandCursor)
        btn_rem.clicked.connect(self.remover_item)
        
        h_act.addWidget(btn_add)
        h_act.addWidget(btn_rem)
        h_act.addStretch()
        layout.addLayout(h_act)
        
        # Total
        self.lbl_total = QLabel("Total: R$ 0,00")
        self.lbl_total.setStyleSheet("font-size: 24px; font-weight: bold; color: #007AFF; margin-top: 10px;")
        self.lbl_total.setAlignment(Qt.AlignRight)
        layout.addWidget(self.lbl_total)
        
        # Rodapé
        h_foot = QHBoxLayout()
        btn_cancel = QPushButton("Cancelar")
        btn_cancel.clicked.connect(self.reject)
        
        btn_save = QPushButton("Gerar PDF e Salvar")
        btn_save.setProperty("class", "primary")
        btn_save.setCursor(Qt.PointingHandCursor)
        btn_save.clicked.connect(self.validar_e_aceitar)
        
        h_foot.addStretch()
        h_foot.addWidget(btn_cancel)
        h_foot.addWidget(btn_save)
        layout.addLayout(h_foot)
        
        self.setLayout(layout)
        self.add_item()
        self.tabela.itemChanged.connect(self.calc)
        
    def add_item(self):
        r = self.tabela.rowCount()
        self.tabela.insertRow(r)
        self.tabela.setItem(r, 0, QTableWidgetItem("1"))
        self.tabela.setItem(r, 1, QTableWidgetItem(""))
        self.tabela.setItem(r, 2, QTableWidgetItem("0,00"))
    
    def remover_item(self):
        r = self.tabela.currentRow()
        if r >= 0:
            self.tabela.removeRow(r)
            self.calc()
        
    def calc(self):
        tot = 0.0
        erro = False
        for r in range(self.tabela.rowCount()):
            item_v = self.tabela.item(r, 2)
            if not item_v: continue
            txt = item_v.text().replace('R$', '').replace('.', '').replace(',', '.').strip()
            if not txt: continue
            try:
                val = float(txt)
                tot += val
                item_v.setBackground(QColor("white"))
            except ValueError:
                item_v.setBackground(QColor("#FFEBEE"))
                erro = True
        
        txt_tot = f"Total: R$ {tot:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
        self.lbl_total.setText(txt_tot)
        if erro: self.lbl_total.setText("Erro no valor!")
        
    def validar_e_aceitar(self):
        self.calc()
        self.accept()

    def get_data(self):
        itens = []
        tot = 0.0
        for r in range(self.tabela.rowCount()):
            q = self.tabela.item(r, 0).text()
            d = self.tabela.item(r, 1).text()
            try: 
                raw = self.tabela.item(r, 2).text().replace(',', '.').strip()
                v = float(raw)
            except: v = 0.0
            tot += v
            itens.append((q, d, v))
        return itens, tot

class CadastroCliente(QWidget):
    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent
        self.setWindowTitle("Novo Cadastro")
        self.resize(450, 600)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(15)
        
        lbl = QLabel("Dados do Cliente")
        lbl.setProperty("class", "titulo")
        layout.addWidget(lbl)
        
        self.inputs = {}
        campos = ["Nome", "Telefone", "Endereço", "Carro", "Placa", "Ano", "KM", "Observações"]
        
        for c in campos:
            l = QLabel(c)
            l.setStyleSheet("font-weight: 600; color: #555;")
            layout.addWidget(l)
            inp = QLineEdit()
            if c == "Placa":
                inp.setPlaceholderText("ABC1234")
                inp.setMaxLength(7)
                inp.textChanged.connect(lambda t, x=inp: x.setText(t.upper()))
            elif c in ["Ano", "KM"]:
                inp.setValidator(QIntValidator())
            
            self.inputs[c] = inp
            layout.addWidget(inp)
            
        layout.addStretch()
        btn = QPushButton("Salvar Cadastro")
        btn.setProperty("class", "primary")
        btn.setCursor(Qt.PointingHandCursor)
        btn.clicked.connect(self.salvar)
        layout.addWidget(btn)
        
        self.setLayout(layout)
        
    def salvar(self):
        dados = [self.inputs[k].text() for k in self.inputs]
        if not dados[0].strip() or not dados[4].strip():
            QMessageBox.warning(self, "Atenção", "Nome e Placa são obrigatórios.")
            return
        salvar_cliente(*dados)
        if self.parent: self.parent.carregar()
        self.close()

class DetalheCliente(QWidget):
    def __init__(self, id_cli, dados, status, parent=None):
        super().__init__()
        self.parent = parent
        self.id_cli = id_cli
        self.dados = dados
        self.setWindowTitle("Detalhes")
        self.resize(400, 650)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(10)
        
        lbl_nome = QLabel(dados[0])
        lbl_nome.setProperty("class", "titulo")
        layout.addWidget(lbl_nome)
        
        labels = ["Nome", "Telefone", "Endereço", "Carro", "Placa", "Ano", "KM", "Observações"]
        for l, v in zip(labels, dados):
            layout.addWidget(QLabel(f"{l}:", styleSheet="font-weight: bold; color: #666;"))
            inp = QLineEdit(str(v))
            inp.setReadOnly(True)
            inp.setStyleSheet("background-color: #F5F5F7; border: none;")
            layout.addWidget(inp)
            
        layout.addSpacing(10)
        layout.addWidget(QLabel("Status do Serviço:", styleSheet="font-weight: bold;"))
        
        self.cb_status = QComboBox()
        self.cb_status.addItems(["Aberto", "Aguardando Peça", "Em Andamento", "Concluído", "Entregue"])
        self.cb_status.setCurrentText(status)
        self.cb_status.currentTextChanged.connect(self.mudar_status)
        layout.addWidget(self.cb_status)
        
        layout.addSpacing(20)
        
        btn_hist = QPushButton("Ver Histórico Completo")
        btn_hist.setCursor(Qt.PointingHandCursor)
        btn_hist.clicked.connect(lambda: DialogoHistorico(id_cli, dados[0], self).exec_())
        
        btn_del = QPushButton("Excluir Cliente")
        btn_del.setProperty("class", "danger")
        btn_del.setCursor(Qt.PointingHandCursor)
        btn_del.clicked.connect(self.excluir)
        layout.addWidget(btn_del)
        
        self.setLayout(layout)
        
    def mudar_status(self, txt):
        db.atualizar_status(self.id_cli, txt)
        if self.parent: self.parent.carregar()
        
    def excluir(self):
        if QMessageBox.question(self, "Excluir", "Tem certeza?") == QMessageBox.Yes:
            db.deletar_cliente(self.id_cli)
            if self.parent: self.parent.carregar()
            self.close()

# =============================================================================
# MENU PRINCIPAL
# =============================================================================

class MenuPrincipal(QWidget):
    def __init__(self):
        super().__init__()
        verificar_banco_historico()
        
        self.setWindowTitle("Sistema Oficina Pro")
        self.setGeometry(100, 100, 1200, 700)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # Header da Tela Principal
        header = QHBoxLayout()
        lbl_logo = QLabel("Sistema de Gestão")
        lbl_logo.setProperty("class", "titulo")
        header.addWidget(lbl_logo)
        header.addStretch()
        layout.addLayout(header)
        
        # Tabela
        colunas = ["Status", "Nome", "Telefone", "Endereço", "Carro", "Placa", "Ano", "KM", "Obs"]
        self.tabela = QTableWidget(0, len(colunas))
        self.tabela.setHorizontalHeaderLabels(colunas)
        self.tabela.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tabela.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tabela.horizontalHeader().setSectionResizeMode(8, QHeaderView.Stretch)
        self.tabela.verticalHeader().setVisible(False)
        self.tabela.setShowGrid(False)
        self.tabela.setAlternatingRowColors(True)
        layout.addWidget(self.tabela)
        
        # Barra de Ações (Botões)
        hbox = QHBoxLayout()
        hbox.setSpacing(15)
        
        b_novo = QPushButton("Novo Cliente")
        b_novo.setProperty("class", "primary")
        b_novo.setCursor(Qt.PointingHandCursor)
        b_novo.clicked.connect(self.abrir_cadastro)
        
        b_nota = QPushButton("Gerar Nota")
        b_nota.setCursor(Qt.PointingHandCursor)
        b_nota.clicked.connect(self.gerar_nota)
        
        b_fin = QPushButton("Financeiro")
        b_fin.setCursor(Qt.PointingHandCursor)
        b_fin.clicked.connect(self.abrir_financeiro)
        
        b_sair = QPushButton("Sair")
        b_sair.clicked.connect(self.close)
        
        hbox.addWidget(b_novo)
        hbox.addWidget(b_nota)
        hbox.addWidget(b_fin)
        hbox.addStretch()
        hbox.addWidget(b_sair)
        
        layout.addLayout(hbox)
        self.setLayout(layout)
        
        self.carregar()
        self.tabela.cellDoubleClicked.connect(self.detalhes)
        
    def abrir_cadastro(self):
        self.janela_cadastro = CadastroCliente(self)
        self.janela_cadastro.show()

    def abrir_financeiro(self):
        self.janela_financeiro = DialogoFinanceiro(self)
        self.janela_financeiro.show()

    def carregar(self):
        conn = conectar()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT id, status, nome, telefone, endereco, carro, placa, ano, km, observacoes FROM clientes")
        except:
            cursor = conn.cursor()
            cursor.execute("SELECT id, 'Aberto', nome, telefone, endereco, carro, placa, ano, km, observacoes FROM clientes")
            
        dados = cursor.fetchall()
        self.tabela.setRowCount(len(dados))
        for i, row in enumerate(dados):
            id_cli = row[0]
            status = row[1] if row[1] else 'Aberto'
            
            item_st = QTableWidgetItem(status)
            item_st.setData(Qt.UserRole, id_cli)
            
            if status in ["Concluído", "Entregue"]: 
                item_st.setForeground(QColor("#2E7D32"))
                item_st.setFont(QFont("Segoe UI", weight=QFont.Bold))
            elif status == "Aguardando Peça": 
                item_st.setForeground(QColor("#E65100"))
            elif status == "Em Andamento": 
                item_st.setForeground(QColor("#1565C0"))
            
            self.tabela.setItem(i, 0, item_st)
            for j in range(2, 10): 
                self.tabela.setItem(i, j-1, QTableWidgetItem(str(row[j])))
        conn.close()
                
    def detalhes(self, r, c):
        id_cli = self.tabela.item(r, 0).data(Qt.UserRole)
        status = self.tabela.item(r, 0).text()
        dados = [self.tabela.item(r, x).text() for x in range(1, 9)]
        self.janela_detalhes = DetalheCliente(id_cli, dados, status, self)
        self.janela_detalhes.show()
        
    def gerar_nota(self):
        sel = DialogoSelecionarCliente(self)
        if sel.exec_():
            cli = sel.get_dados()
            serv = DialogoServico(cli, self)
            if serv.exec_():
                itens, tot = serv.get_data()
                path, _ = QFileDialog.getSaveFileName(self, "Salvar PDF", f"Nota_{cli['nome']}.pdf", "PDF (*.pdf)")
                if path:
                    try:
                        self.criar_pdf(path, cli, itens, tot)
                        
                        try:
                            conn = conectar()
                            js = json.dumps(itens)
                            hj = datetime.now().strftime('%d/%m/%Y')
                            conn.cursor().execute("INSERT INTO historico_servicos (id_cliente, data_servico, itens_json, valor_total, arquivo_path) VALUES (?,?,?,?,?)", (cli['id'], hj, js, tot, path))
                            conn.commit()
                            conn.close()
                        except Exception as e:
                            print(f"Erro ao salvar histórico: {e}")

                        QMessageBox.information(self, "Sucesso", "Nota salva com sucesso!")
                    except Exception as e: QMessageBox.critical(self, "Erro", str(e))

    def criar_pdf(self, arquivo, cliente, itens, total):
        c = canvas.Canvas(arquivo, pagesize=A4)
        w, h = A4; m = 50; y = 800
        
        c.setFont("Helvetica-Bold", 16)
        c.drawCentredString(w/2, y, "Auto Elétrica Diniz")
        y -= 20
        c.setFont("Helvetica", 11)
        c.drawCentredString(w/2, y, "Av Almirante Tamandaré, 700 - Piratininga")
        y -= 15
        c.drawCentredString(w/2, y, "Telefone: (21) 97612-4007")
        y -= 20
        c.drawCentredString(w/2, y, f"Data: {datetime.now().strftime('%d/%m/%Y')}")
        
        y -= 20
        c.setLineWidth(1)
        c.line(m, y, w-m, y)
        
        y -= 40
        c.setFont("Helvetica-Bold", 12)
        c.drawString(m, y, f"Cliente: {cliente['nome']}")
        
        y -= 30
        col_qtd = m
        col_desc = m + 40
        col_val = w - 150
        h_row = 20
        
        c.setFillColor(colors.lightgrey)
        c.rect(col_qtd, y-5, w-(m*2), h_row, fill=1, stroke=1)
        c.setFillColor(colors.black)
        
        c.line(col_desc, y-5, col_desc, y+15)
        c.line(col_val, y-5, col_val, y+15)
        
        c.setFont("Helvetica-Bold", 11)
        c.drawString(col_qtd+5, y, "Qtd.")
        c.drawString(col_desc+5, y, "Descrição")
        c.drawString(col_val+5, y, "Valor Total")
        
        y -= h_row
        c.setFont("Helvetica", 11)
        
        for q, d, v in itens:
            c.rect(col_qtd, y-5, w-(m*2), h_row, fill=0, stroke=1)
            c.line(col_desc, y-5, col_desc, y+15)
            c.line(col_val, y-5, col_val, y+15)
            
            c.drawString(col_qtd+5, y, str(q))
            c.drawString(col_desc+5, y, d)
            c.drawString(col_val+5, y, f"R$ {v:,.2f}".replace('.', ','))
            y -= h_row
            
            if y < 100:
                c.showPage()
                y = 800
                c.setFont("Helvetica", 11)

        y -= 20
        c.setFont("Helvetica-Bold", 12)
        c.drawString(m, y, f"Valor Total: R$ {total:,.2f}".replace('.', ','))
        
        y -= 30
        c.setFont("Helvetica-Bold", 11)
        c.drawString(m, y, "Forma de Pagamento: [Dinheiro / PIX / Cartão / Transferência]")
        
        y -= 50
        c.setFont("Helvetica-Oblique", 11)
        c.drawString(m, y, "Observações:")
        y -= 20
        c.setFont("Helvetica-Oblique", 10)
        c.drawString(m, y, "- Garantia de 90 dias conforme o Código de Defesa do Consumidor.")
        y -= 15
        c.drawString(m, y, "- Qualquer problema, favor entrar em contato imediatamente.")
        
        c.save()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(STYLESHEET)
    window = MenuPrincipal()
    window.show()
    sys.exit(app.exec_())