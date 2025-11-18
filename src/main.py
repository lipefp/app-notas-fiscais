import sys
import os
import json
from datetime import datetime

from PyQt5.QtWidgets import (
    QApplication, QLabel, QVBoxLayout, QWidget, QLineEdit, QPushButton, 
    QTableWidget, QTableWidgetItem, QHBoxLayout, QHeaderView, QDialog, 
    QDialogButtonBox, QFileDialog, QMessageBox, QAbstractItemView,
    QComboBox, QFrame
)
from PyQt5.QtGui import QIntValidator, QDoubleValidator, QColor, QFont
from PyQt5.QtCore import Qt

# --- BIBLIOTECAS PARA O PDF ---
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors

# --- IMPORTAÇÃO DO BANCO DE DADOS ---
try:
    import models.db as db
    from models.db import conectar, salvar_cliente
except ImportError:
    print("ERRO CRÍTICO: Pasta 'models' ou arquivo 'db.py' não encontrados.")
    sys.exit(1)

# =============================================================================
# ESTILO GLOBAL (CSS) - TEMA CLEAN / MACOS INSPIRED
# =============================================================================
STYLESHEET = """
    QWidget {
        background-color: #FFFFFF;
        color: #333333;
        font-family: "Segoe UI", "Helvetica Neue", Arial, sans-serif;
        font-size: 14px;
    }
    
    /* Janelas de Diálogo */
    QDialog {
        background-color: #FFFFFF;
    }

    /* Campos de Texto */
    QLineEdit, QComboBox {
        border: 1px solid #E5E5E5;
        border-radius: 8px;
        padding: 8px 12px;
        background-color: #F9F9F9;
        selection-background-color: #007AFF;
    }
    QLineEdit:focus, QComboBox:focus {
        border: 1px solid #007AFF;
        background-color: #FFFFFF;
    }

    /* Tabelas */
    QTableWidget {
        border: 1px solid #E5E5E5;
        border-radius: 8px;
        gridline-color: #F0F0F0;
        alternate-background-color: #FAFAFA;
        selection-background-color: #E3F2FD;
        selection-color: #333333;
    }
    QHeaderView::section {
        background-color: #FFFFFF;
        border: none;
        border-bottom: 2px solid #F0F0F0;
        padding: 8px;
        font-weight: bold;
        color: #555555;
    }

    /* Botões Genéricos */
    QPushButton {
        background-color: #F5F5F7;
        border: 1px solid #E5E5E5;
        border-radius: 8px;
        padding: 8px 16px;
        color: #333333;
        font-weight: 500;
    }
    QPushButton:hover {
        background-color: #EBEBEB;
        border-color: #D1D1D1;
    }
    QPushButton:pressed {
        background-color: #E0E0E0;
    }

    /* Botões de Ação Primária (Azul) */
    QPushButton[class="primary"] {
        background-color: #007AFF;
        color: white;
        border: none;
    }
    QPushButton[class="primary"]:hover {
        background-color: #0069D9;
    }

    /* Botões de Perigo (Vermelho) */
    QPushButton[class="danger"] {
        background-color: #FFF2F2;
        color: #D32F2F;
        border: 1px solid #FFCDD2;
    }
    QPushButton[class="danger"]:hover {
        background-color: #FFEBEE;
        border-color: #EF9A9A;
    }
    
    /* Botões de Sucesso (Verde) */
    QPushButton[class="success"] {
        background-color: #F1F8E9;
        color: #388E3C;
        border: 1px solid #C8E6C9;
    }
    
    /* Labels de Título */
    QLabel[class="title"] {
        font-size: 18px;
        font-weight: bold;
        color: #111111;
        margin-bottom: 10px;
    }
"""

# =============================================================================
# FUNÇÕES DE CONFIGURAÇÃO
# =============================================================================
def verificar_banco_historico():
    try:
        conn = conectar()
        cursor = conn.cursor()
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
        self.setWindowTitle(f"Histórico: {nome_cliente}")
        self.resize(700, 500)
        
        layout = QVBoxLayout()
        lbl_titulo = QLabel(f"Serviços: {nome_cliente}")
        lbl_titulo.setProperty("class", "title")
        layout.addWidget(lbl_titulo)
        
        self.tabela = QTableWidget()
        self.tabela.setColumnCount(3)
        self.tabela.setHorizontalHeaderLabels(["Data", "Resumo do Serviço", "Valor Total"])
        self.tabela.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.tabela.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tabela.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tabela.setAlternatingRowColors(True)
        self.tabela.setShowGrid(False)
        layout.addWidget(self.tabela)
        
        btn = QPushButton("Fechar")
        btn.clicked.connect(self.close)
        layout.addWidget(btn)
        
        self.setLayout(layout)
        self.carregar_dados(id_cliente)

    def carregar_dados(self, id_cliente):
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("SELECT data_servico, itens_json, valor_total FROM historico_servicos WHERE id_cliente=? ORDER BY id DESC", (id_cliente,))
        dados = cursor.fetchall()
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
        self.setWindowTitle("Relatório Financeiro")
        self.resize(400, 250)
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        
        lbl_tit = QLabel("Faturamento Total")
        lbl_tit.setProperty("class", "title")
        lbl_tit.setAlignment(Qt.AlignCenter)
        layout.addWidget(lbl_tit)
        
        total = self.calcular_total()
        
        lbl = QLabel(f"R$ {total:,.2f}")
        lbl.setStyleSheet("font-size: 32px; color: #2E7D32; font-weight: bold;")
        lbl.setAlignment(Qt.AlignCenter)
        layout.addWidget(lbl)
        
        layout.addWidget(QLabel("Soma de todas as notas geradas no sistema."), alignment=Qt.AlignCenter)
        self.setLayout(layout)

    def calcular_total(self):
        try:
            conn = conectar()
            res = conn.cursor().execute("SELECT SUM(valor_total) FROM historico_servicos").fetchone()[0]
            conn.close()
            return res if res else 0.0
        except: return 0.0

class DialogoSelecionarCliente(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Selecione o Cliente")
        self.resize(700, 450)
        self.cliente_selecionado = None 

        layout = QVBoxLayout()
        lbl = QLabel("Selecione um cliente para gerar nota:")
        lbl.setProperty("class", "title")
        layout.addWidget(lbl)
        
        self.tabela = QTableWidget()
        self.tabela.setColumnCount(5)
        self.tabela.setHorizontalHeaderLabels(["Nome", "Telefone", "Carro", "Placa", "Ano"])
        self.tabela.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tabela.setSelectionMode(QAbstractItemView.SingleSelection)
        self.tabela.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tabela.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabela.setAlternatingRowColors(True)
        self.tabela.setShowGrid(False)
        layout.addWidget(self.tabela)
        
        self.carregar_clientes()
        
        btns = QHBoxLayout()
        btn_ok = QPushButton("Confirmar Seleção")
        btn_ok.setProperty("class", "primary")
        btn_ok.clicked.connect(self.confirmar)
        
        btn_cancel = QPushButton("Cancelar")
        btn_cancel.clicked.connect(self.reject)
        
        btns.addWidget(btn_cancel)
        btns.addWidget(btn_ok)
        layout.addLayout(btns)
        self.setLayout(layout)

    def carregar_clientes(self):
        conn = conectar()
        dados = conn.cursor().execute("SELECT id, nome, telefone, carro, placa, ano FROM clientes").fetchall()
        self.tabela.setRowCount(len(dados))
        for i, row in enumerate(dados):
            item_nome = QTableWidgetItem(str(row[1]))
            item_nome.setData(Qt.UserRole, row[0])
            self.tabela.setItem(i, 0, item_nome)
            self.tabela.setItem(i, 1, QTableWidgetItem(str(row[2])))
            self.tabela.setItem(i, 2, QTableWidgetItem(str(row[3])))
            self.tabela.setItem(i, 3, QTableWidgetItem(str(row[4])))
            self.tabela.setItem(i, 4, QTableWidgetItem(str(row[5])))
        conn.close()

    def confirmar(self):
        r = self.tabela.currentRow()
        if r < 0: 
            QMessageBox.warning(self, "Aviso", "Selecione um cliente.")
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
        self.setWindowTitle(f"Nova Nota: {cliente['nome']}")
        self.resize(700, 550)
        layout = QVBoxLayout()
        
        # Info Header
        header_frame = QFrame()
        header_frame.setStyleSheet("background-color: #F5F5F7; border-radius: 8px; padding: 10px;")
        header_layout = QVBoxLayout(header_frame)
        
        lbl_cli = QLabel(f"Cliente: {cliente['nome']}")
        lbl_cli.setStyleSheet("font-weight: bold; font-size: 15px;")
        lbl_car = QLabel(f"Veículo: {cliente['carro']}  |  Placa: {cliente['placa']}")
        lbl_car.setStyleSheet("color: #555;")
        
        header_layout.addWidget(lbl_cli)
        header_layout.addWidget(lbl_car)
        layout.addWidget(header_frame)
        
        self.tabela = QTableWidget(0, 3)
        self.tabela.setHorizontalHeaderLabels(["Qtd", "Descrição", "Valor Unit. (R$)"])
        self.tabela.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.tabela.setAlternatingRowColors(True)
        layout.addWidget(self.tabela)
        
        # Botões de Item
        h_btns = QHBoxLayout()
        btn_add = QPushButton("Adicionar Item")
        btn_add.clicked.connect(self.add_item)
        btn_rem = QPushButton("Remover Item")
        btn_rem.clicked.connect(self.remover_item)
        h_btns.addWidget(btn_add)
        h_btns.addWidget(btn_rem)
        h_btns.addStretch()
        layout.addLayout(h_btns)
        
        # Total
        self.lbl_total = QLabel("Total: R$ 0,00")
        self.lbl_total.setStyleSheet("font-size: 22px; font-weight: bold; color: #007AFF; margin-top: 10px;")
        self.lbl_total.setAlignment(Qt.AlignRight)
        layout.addWidget(self.lbl_total)
        
        # Botões Finais
        bb = QDialogButtonBox()
        btn_ok = bb.addButton("Gerar Nota e Salvar", QDialogButtonBox.AcceptRole)
        btn_ok.setProperty("class", "primary")
        btn_cancel = bb.addButton("Cancelar", QDialogButtonBox.RejectRole)
        
        bb.accepted.connect(self.validar_e_aceitar)
        bb.rejected.connect(self.reject)
        layout.addWidget(bb)
        
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
        
        texto_total = f"Total: R$ {tot:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
        self.lbl_total.setText(texto_total)
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
        self.setWindowTitle("Novo Cliente")
        self.resize(400, 550)
        
        layout = QVBoxLayout()
        layout.setSpacing(12)
        
        lbl = QLabel("Dados do Cliente")
        lbl.setProperty("class", "title")
        layout.addWidget(lbl)
        
        self.inputs = {}
        campos = ["Nome", "Telefone", "Endereço", "Carro", "Placa", "Ano", "KM", "Observações"]
        
        for c in campos:
            l = QLabel(c)
            l.setStyleSheet("font-weight: bold; color: #555;")
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
            
        layout.addSpacing(10)
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
        self.setWindowTitle("Detalhes do Cliente")
        self.resize(400, 600)
        
        layout = QVBoxLayout()
        layout.setSpacing(10)
        
        lbl_tit = QLabel(dados[0]) # Nome
        lbl_tit.setProperty("class", "title")
        layout.addWidget(lbl_tit)
        
        labels = ["Nome", "Telefone", "Endereço", "Carro", "Placa", "Ano", "KM", "Observações"]
        for l, v in zip(labels, dados):
            layout.addWidget(QLabel(f"{l}:"))
            inp = QLineEdit(str(v))
            inp.setReadOnly(True)
            layout.addWidget(inp)
            
        layout.addWidget(QLabel("Status Atual:"))
        self.cb_status = QComboBox()
        self.cb_status.addItems(["Aberto", "Aguardando Peça", "Em Andamento", "Concluído", "Entregue"])
        self.cb_status.setCurrentText(status)
        self.cb_status.currentTextChanged.connect(self.mudar_status)
        layout.addWidget(self.cb_status)
        
        layout.addSpacing(15)
        
        h_btns = QHBoxLayout()
        btn_hist = QPushButton("Ver Histórico")
        btn_hist.clicked.connect(lambda: DialogoHistorico(id_cli, dados[0], self).exec_())
        
        btn_del = QPushButton("Excluir")
        btn_del.setProperty("class", "danger")
        btn_del.setCursor(Qt.PointingHandCursor)
        btn_del.clicked.connect(self.excluir)
        
        h_btns.addWidget(btn_hist)
        h_btns.addWidget(btn_del)
        layout.addLayout(h_btns)
        
        self.setLayout(layout)
        
    def mudar_status(self, txt):
        conn = conectar()
        conn.cursor().execute("UPDATE clientes SET status=? WHERE id=?", (txt, self.id_cli))
        conn.commit()
        conn.close()
        if self.parent: self.parent.carregar()
        
    def excluir(self):
        conn = conectar()
        conn.cursor().execute("DELETE FROM clientes WHERE id=?", (self.id_cli,))
        conn.commit()
        conn.close()
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
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Tabela
        colunas = ["Status", "Nome", "Telefone", "Endereço", "Carro", "Placa", "Ano", "KM", "Obs"]
        self.tabela = QTableWidget(0, len(colunas))
        self.tabela.setHorizontalHeaderLabels(colunas)
        self.tabela.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tabela.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tabela.horizontalHeader().setSectionResizeMode(8, QHeaderView.Stretch)
        self.tabela.setShowGrid(False)
        self.tabela.setAlternatingRowColors(True)
        self.tabela.verticalHeader().setVisible(False)
        layout.addWidget(self.tabela)
        
        # Botões Principais
        hbox = QHBoxLayout()
        
        b1 = QPushButton("Novo Cliente")
        b1.setProperty("class", "primary") # Estilo azul
        b1.setCursor(Qt.PointingHandCursor)
        b1.clicked.connect(self.abrir_cadastro)
        
        b2 = QPushButton("Gerar Nota")
        b2.setProperty("class", "success") # Estilo verde
        b2.setCursor(Qt.PointingHandCursor)
        b2.clicked.connect(self.gerar_nota)
        
        b3 = QPushButton("Financeiro")
        b3.setCursor(Qt.PointingHandCursor)
        b3.clicked.connect(self.abrir_financeiro)
        
        b_sair = QPushButton("Sair")
        b_sair.setCursor(Qt.PointingHandCursor)
        b_sair.clicked.connect(self.close)
        
        hbox.addWidget(b1)
        hbox.addWidget(b2)
        hbox.addWidget(b3)
        hbox.addStretch() # Empurra o sair para a direita
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
            
            # Cores baseadas no status (QColor)
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
                        
                        # Salvar Histórico
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
        
        # Cabeçalho
        c.setFont("Helvetica-Bold", 16)
        c.drawCentredString(w/2, y, "Auto Elétrica Diniz")
        y -= 20
        c.setFont("Helvetica", 11)
        c.drawCentredString(w/2, y, "Av Almirante Tamandaré, 700 - Piratininga")
        y -= 15
        c.drawCentredString(w/2, y, "Telefone: (21) 97612-4007")
        y -= 20
        c.drawCentredString(w/2, y, f"Data: {datetime.now().strftime('%d/%m/%Y')}")
        
        # Linha divisória
        y -= 20
        c.setLineWidth(1)
        c.line(m, y, w-m, y)
        
        # Cliente
        y -= 40
        c.setFont("Helvetica-Bold", 12)
        c.drawString(m, y, f"Cliente: {cliente['nome']}")
        
        # Tabela Config
        y -= 30
        col_qtd = m
        col_desc = m + 40
        col_val = w - 150
        col_end = w - m
        h_row = 20
        
        # Cabeçalho Tabela
        c.setFillColor(colors.lightgrey)
        c.rect(col_qtd, y-5, col_end-col_qtd, h_row, fill=1, stroke=1)
        c.setFillColor(colors.black)
        
        c.line(col_desc, y-5, col_desc, y+15)
        c.line(col_val, y-5, col_val, y+15)
        
        c.setFont("Helvetica-Bold", 11)
        c.drawString(col_qtd+5, y, "Qtd.")
        c.drawString(col_desc+5, y, "Descrição")
        c.drawString(col_val+5, y, "Valor Total")
        
        y -= h_row
        c.setFont("Helvetica", 11)
        
        # Itens
        for q, d, v in itens:
            c.rect(col_qtd, y-5, col_end-col_qtd, h_row, fill=0, stroke=1)
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

        # Totais
        y -= 20
        c.setFont("Helvetica-Bold", 12)
        c.drawString(m, y, f"Valor Total: R$ {total:,.2f}".replace('.', ','))
        
        y -= 30
        c.setFont("Helvetica-Bold", 11)
        c.drawString(m, y, "Forma de Pagamento: [Dinheiro / PIX / Cartão / Transferência]")
        
        # Rodapé
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
    app.setStyleSheet(STYLESHEET) # APLICA O TEMA GLOBAL AQUI
    window = MenuPrincipal()
    window.show()
    sys.exit(app.exec_())