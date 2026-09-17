# 🥗 NutriDAY — Prescrição Nutricional & Gestão Clínica

> Sistema web intuitivo e moderno para cálculo antropométrico, elaboração de planos alimentares com base na tabela TACO e geração de relatórios clínicos em PDF. Desenvolvido para a **Dra. Andressa Santos**.

---

## 🚀 Funcionalidades

- 📊 **Avaliação Antropométrica:** Cálculo automático do IMC, classificação segundo a OMS e indicação do Peso Ideal Recomendado.
- 🚫 **Gestão de Restrições:** Campo dedicado para registro de alergias, intolerâncias e restrições alimentares do paciente.
- 🍎 **Tabela TACO Integrada:** Busca simplificada e otimizada por alimentos da Tabela Brasileira de Composição de Alimentos.
- 🍽️ **Montagem de Refeições:** Divisão por refeições (Desjejum, Almoço, Lanche, Jantar e Ceia) com opção de inclusão e remoção rápida de alimentos em 1 clique.
- 📈 **Balanço Nutricional em Tempo Real:** Soma automática de calorias totais (kcal), proteínas (g), carboidratos (g) e lipídeos (g).
- 📄 **Exportação de PDF:** Gerador de plano alimentar profissional assinado pela nutricionista, pronto para impressão ou envio por WhatsApp/e-mail.

---

## 🛠️ Tecnologias Utilizadas

- **Linguagem:** Python 3.12
- **Interface Web:** [Streamlit](https://streamlit.io/)
- **Processamento de Dados:** [Pandas](https://pandas.pydata.org/)
- **Geração de PDF:** [ReportLab](https://www.reportlab.com/)

---

## 📁 Estrutura do Projeto

```text
NUTRIDAY/
├── app.py                 # Interface principal da aplicação Streamlit
├── requirements.txt       # Dependências do projeto
├── dados/
│   └── tabela_taco.csv    # Base de dados da Tabela TACO
└── modulos/
    ├── calculos.py        # Cálculos de IMC, peso ideal e totais diários
    ├── pdf.py             # Montagem e estilização do relatório em PDF
    └── taco.py            # Tratamento e busca na tabela TACO

    git clone [https://github.com/rezende28/NUTRIDAY.git](https://github.com/rezende28/NUTRIDAY.git)
cd NUTRIDAY

Instale as dependências: 
pip install -r requirements.txt

Execute a aplicação:
streamlit run app.py