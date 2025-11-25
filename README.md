🚗 Sistema de Gestão - Oficina

Um sistema desktop completo para gestão de oficinas mecânicas e autoelétricas, focado em agilidade no atendimento, organização financeira e emissão de documentos.

O sistema conta com uma interface limpa e intuitiva.

🚀 Funcionalidades Principais

📋 Cadastro de Clientes e Veículos: Registro detalhado com validação automática de placas (padrão Mercosul e Antigo).

📝 Geração de Notas de Serviço: Criação rápida de ordens de serviço com múltiplos itens (peças e mão de obra).

🖨️ Exportação PDF Profissional: Gera orçamentos e recibos em PDF com layout corporativo, pronto para impressão ou envio via WhatsApp.

💰 Controle Financeiro: Relatório instantâneo de faturamento acumulado e fluxo de caixa.

📂 Histórico (Prontuário): Consulta completa de todos os serviços já realizados em um veículo específico.

🎨 Interface Clean: Design moderno, responsivo e fácil de usar.

🛠️ Tecnologias Utilizadas

Linguagem: Python 3

GUI (Interface Gráfica): PyQt5

Banco de Dados: SQLite3 (Nativo, sem necessidade de servidor externo)

Relatórios: ReportLab (Engine de geração de PDFs)

Controle de Versão: Git & GitHub

🗂️ Estrutura do Projeto

app-notas-fiscais/

├── src/

│   ├── main.py          # Interface e Lógica Principal

│   └── models/

│       └── db.py        # Camada de Banco de Dados (SQLite)

├── assets/              # Imagens e demonstrações

├── .gitignore           # Arquivos ignorados pelo Git

├── LICENSE              # Licença de uso

└── README.md            # Documentação do projeto

