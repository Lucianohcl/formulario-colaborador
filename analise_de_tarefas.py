# ============================================================
# IMPORTS
# ============================================================

import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime
from statistics import mean

# PDF
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from datetime import datetime
import pytz
import time
# ============================================================

# CONFIGURAÇÃO E INICIALIZAÇÃO ÚNICA

# ============================================================

st.set_page_config(

page_title=&quot;Sistema de Análise de Tarefas&quot;,

page_icon=&quot;  &quot;,

layout=&quot;wide&quot;,

initial_sidebar_state=&quot;expanded&quot;

)

# Inicialização centralizada

if &quot;logged_in&quot; not in st.session_state: st.session_state.logged_in = False

if &quot;pagina&quot; not in st.session_state: st.session_state.pagina = &quot;home&quot;

if &quot;formularios&quot; not in st.session_state: st.session_state[&quot;formularios&quot;] = []

# Leitura da URL (Prioridade total para permitir acesso ao formulário)

query_params = st.query_params

if &quot;page&quot; in query_params:

st.session_state.pagina = query_params[&quot;page&quot;]

st.markdown(&quot;&quot;&quot;
&lt;style&gt;
/* Oculta a coluna de índice do data_editor */
div[data-testid=&quot;stDataEditor&quot;] &gt; div &gt; div &gt; div &gt; div:first-child {
display: none !important;
}

&lt;/style&gt;
&quot;&quot;&quot;, unsafe_allow_html=True)

# --- LISTA DE PERGUNTAS DISC ---
perguntas_disc = [
&quot;Quando surge um problema inesperado: (A) Age rápido | (B) Comunica a todos | (C) Analisa
riscos | (D) Segue processo&quot;,
&quot;Em situações de pressão: (A) Foca no resultado | (B) Mantém o otimismo | (C) Mantém a
calma | (D) Busca precisão&quot;,
&quot;Ao receber tarefa difícil: (A) Aceita o desafio | (B) Busca ajuda social | (C) Planeja passos |
(D) Estuda as regras&quot;,
&quot;No trabalho em equipe: (A) Lidera o grupo | (B) Motiva os colegas | (C) Apoia os outros |
(D) Organiza as tarefas&quot;,
&quot;Em reuniões: (A) Vai direto ao ponto | (B) Interage e brinca | (C) Escuta mais | (D) Anota
detalhes&quot;,
&quot;Ao lidar com conflitos: (A) Enfrenta direto | (B) Tenta apaziguar | (C) Evita o confronto | (D)
Usa lógica e fatos&quot;,
&quot;Seu ritmo de trabalho: (A) Rápido/Impaciente | (B) Rápido/Entusiasmado | (C)
Calmo/Constante | (D) Metódico/Cauteloso&quot;,
&quot;Prefere tarefas: (A) Desafiadoras | (B) Variadas e sociais | (C) Rotineiras e seguras | (D)
Técnicas e detalhadas&quot;,
&quot;Seu foco principal: (A) Resultados | (B) Relacionamentos | (C) Estabilidade | (D) Qualidade e
Processos&quot;,
&quot;Ao decidir, você é: (A) Decidido e firme | (B) Impulsivo e intuitivo | (C) Cuidadoso e lento |
(D) Lógico e analítico&quot;,
&quot;Confia mais em: (A) Sua intuição | (B) Opinião alheia | (C) Experiência passada | (D) Dados e
provas&quot;,
&quot;Prefere decisões: (A) Independentes | (B) Em grupo | (C) Consensuais | (D) Baseadas em
normas&quot;,
&quot;Estilo de organização: (A) Prático | (B) Criativo/Bagunçado | (C) Tradicional | (D) Muito
organizado&quot;,
&quot;Lida melhor com: (A) Mudanças rápidas | (B) Novas ideias | (C) Rotinas claras | (D) Regras
rígidas&quot;,
&quot;Prefere trabalhar: (A) Sozinho/Comando | (B) Ambiente festivo | (C) Ambiente tranquilo |
(D) Ambiente silencioso&quot;,

&quot;Seu ponto forte: (A) Coragem | (B) Comunicação | (C) Paciência | (D) Organização&quot;,
&quot;Você se considera: (A) Dominante | (B) Influente | (C) Estável | (D) Conforme/Analítico&quot;,
&quot;Se motiva por: (A) Poder/Bônus | (B) Reconhecimento | (C) Segurança/Paz | (D)
Conhecimento Técnico&quot;,
&quot;Reação a cobranças: (A) Mais esforço | (B) Desculpas criativas | (C) Ansiedade | (D)
Argumentos técnicos&quot;,
&quot;Ambiente ideal: (A) Competitivo | (B) Amigável | (C) Previsível | (D) Disciplinado&quot;,
&quot;Ao lidar com feedback: (A) Aceita e ajusta | (B) Comenta e debate | (C) Analisa e planeja |
(D) Segue regras&quot;,
&quot;Como prefere aprender: (A) Fazendo | (B) Interagindo | (C) Observando | (D) Estudando
materiais&quot;,
&quot;Gestão de tempo: (A) Prioriza resultados | (B) Mantém relações | (C) Planeja com cuidado |
(D) Segue processos&quot;,
&quot;Como se comunica: (A) Direto e objetivo | (B) Amigável e motivador | (C) Calmo e
ponderado | (D) Técnico e detalhista&quot;
]

# --- FUNÇÕES DE EXPORTAÇÃO (COLE NO TOPO DO SEU ARQUIVO) ---
from docx import Document
from fpdf import FPDF
import io

def gerar_word(form):
doc = Document()
doc.add_heading(f&quot;Relatório: {form.get(&#39;Nome&#39;, &#39;Colaborador&#39;)}&quot;, 0)
doc.add_paragraph(f&quot;Data de Envio: {form.get(&#39;DataEnvio&#39;, &#39;N/A&#39;)}&quot;)

# 1. Informações Gerais
doc.add_heading(&quot;Informações de Identificação&quot;, level=1)
campos_gerais = [&#39;Setor&#39;, &#39;Departamento&#39;, &#39;Cargo&#39;, &#39;Chefe&#39;, &#39;Empresa&#39;, &#39;Escolaridade&#39;, &#39;Cursos&#39;,
&#39;Objetivo&#39;]
for campo in campos_gerais:
doc.add_paragraph(f&quot;{campo}: {form.get(campo, &#39;N/A&#39;)}&quot;)

# 2. Tabelas (Atividades, Dificuldades, Sugestões)
secoes = {
&quot;Atividades&quot;: [&quot;Atividade Descrita&quot;, &quot;Frequência&quot;, &quot;Tempo Gasto&quot;],
&quot;Dificuldades&quot;: [&quot;Dificuldade&quot;, &quot;Setor/Parceiro Envolvido&quot;, &quot;Tempo Perdido&quot;],
&quot;Sugestoes&quot;: [&quot;Sugestão de Melhoria&quot;, &quot;Impacto Esperado&quot;]
}

for chave, colunas in secoes.items():
if chave in form and isinstance(form[chave], list):
doc.add_heading(f&quot;   {chave}&quot;, level=1)
# Filtra apenas itens que tenham conteúdo real
dados = [item for item in form[chave] if any(str(item.get(c, &#39;&#39;)).strip() for c in colunas)]

if dados:
table = doc.add_table(rows=1, cols=len(colunas))
table.style = &#39;Table Grid&#39;
# Cabeçalho
for i, col in enumerate(colunas):
table.rows[0].cells[i].text = col
# Linhas
for item in dados:
row = table.add_row().cells
for i, col in enumerate(colunas):
row[i].text = str(item.get(col, &#39;&#39;))
else:
doc.add_paragraph(&quot;Nenhum dado preenchido nesta seção.&quot;)

# 3. Avaliação DISC
doc.add_heading(&quot;   Avaliação DISC (Perguntas e Respostas)&quot;, level=1)
for i, pergunta in enumerate(perguntas_disc, 1):
valor_resposta = form.get(f&quot;Q{i}&quot;, &quot;Não respondido&quot;)

doc.add_paragraph(f&quot;{i}. {pergunta}&quot;, style=&#39;Heading 2&#39;)
doc.add_paragraph(f&quot;Resposta: {valor_resposta}&quot;)
doc.add_paragraph(&quot;-&quot; * 20)

buffer = io.BytesIO()
doc.save(buffer)
buffer.seek(0)
return buffer

from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

def gerar_pdf(form):
buffer = io.BytesIO()
doc = SimpleDocTemplate(buffer, pagesize=letter)
styles = getSampleStyleSheet()
elementos = []

# Título
elementos.append(Paragraph(f&quot;Relatório: {form.get(&#39;Nome&#39;, &#39;Colaborador&#39;)}&quot;, styles[&#39;Title&#39;]))
elementos.append(Paragraph(f&quot;Data: {form.get(&#39;DataEnvio&#39;, &#39;N/A&#39;)}&quot;, styles[&#39;Normal&#39;]))
elementos.append(Spacer(1, 12))

# Informações Gerais
elementos.append(Paragraph(&quot;Informações Gerais&quot;, styles[&#39;Heading2&#39;]))
campos_gerais = [&#39;Setor&#39;, &#39;Departamento&#39;, &#39;Cargo&#39;, &#39;Chefe&#39;, &#39;Empresa&#39;, &#39;Escolaridade&#39;, &#39;Cursos&#39;,
&#39;Objetivo&#39;]
for campo in campos_gerais:
elementos.append(Paragraph(f&quot;&lt;b&gt;{campo}:&lt;/b&gt; {form.get(campo, &#39;N/A&#39;)}&quot;,
styles[&#39;Normal&#39;]))

elementos.append(Spacer(1, 12))

# Tabelas (Atividades, Dificuldades, Sugestoes)
secoes = {
&quot;Atividades&quot;: [&quot;Atividade Descrita&quot;, &quot;Frequência&quot;, &quot;Tempo Gasto&quot;],
&quot;Dificuldades&quot;: [&quot;Dificuldade&quot;, &quot;Setor/Parceiro Envolvido&quot;, &quot;Tempo Perdido&quot;],
&quot;Sugestoes&quot;: [&quot;Sugestão de Melhoria&quot;, &quot;Impacto Esperado&quot;]
}

for titulo, colunas in secoes.items():
if titulo in form and isinstance(form[titulo], list):
elementos.append(Paragraph(titulo, styles[&#39;Heading2&#39;]))
dados = [item for item in form[titulo] if any(str(item.get(c, &#39;&#39;)).strip() for c in colunas)]

if dados:
data = [colunas] # Cabeçalho
for item in dados:
data.append([str(item.get(c, &#39;&#39;)) for c in colunas])

from reportlab.platypus import Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors

if data:  # assumindo que 'data' seja a lista de listas
    tabela = Table(data, repeatRows=1)
    tabela.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.grey),
        ('GRID', (0,0), (-1,-1), 0.5, colors.black),
        ('FONTSIZE', (0,0), (-1,-1), 8)
    ]))
    elementos.append(tabela)
else:
    elementos.append(Paragraph("Nenhum dado preenchido.", styles['Normal']))

elementos.append(Spacer(1, 12))

# DISC
elementos.append(Paragraph(&quot;Avaliação DISC&quot;, styles[&#39;Heading2&#39;]))
for i, pergunta in enumerate(perguntas_disc, 1):
valor_resposta = form.get(f&quot;Q{i}&quot;, &quot;Não respondido&quot;)
elementos.append(Paragraph(f&quot;&lt;b&gt;{i}. {pergunta}&lt;/b&gt;&quot;, styles[&#39;Normal&#39;]))
elementos.append(Paragraph(f&quot;Resposta: {valor_resposta}&quot;, styles[&#39;Italic&#39;]))
elementos.append(Spacer(1, 6))

doc.build(elementos)
buffer.seek(0)
return buffer

# ============================================================
# DEFINIÇÃO E CARREGAMENTO DO BANCO DE DADOS (AJUSTADO)
# ============================================================
import streamlit as st
import pandas as pd
import os
import json
import sys

import os
import sys
import json
import streamlit as st

# --- DEFINIÇÃO DE CAMINHO À PROVA DE ERROS ---
if getattr(sys, &#39;frozen&#39;, False):
base_dir = os.path.dirname(sys.executable)
else:

base_dir = os.path.dirname(os.path.abspath(__file__))

# Definimos o diretório de dados como absoluto
dados_dir = os.path.join(base_dir, &quot;dados&quot;)

# Criamos a pasta &#39;dados&#39; se ela não existir
os.makedirs(dados_dir, exist_ok=True)

# --- FUNÇÃO DE CARREGAMENTO DINÂMICO ---
def carregar_todos_formularios():
&quot;&quot;&quot;
Lê todos os arquivos .json da pasta &#39;dados&#39; individualmente.
&quot;&quot;&quot;
lista_formularios = []
# Usamos a variável global dados_dir definida acima
if os.path.exists(dados_dir):
for nome_arquivo in os.listdir(dados_dir):
if nome_arquivo.endswith(&quot;.json&quot;):
caminho_completo = os.path.join(dados_dir, nome_arquivo)
try:
with open(caminho_completo, &quot;r&quot;, encoding=&quot;utf-8&quot;) as f:
dados = json.load(f)
if isinstance(dados, dict):
lista_formularios.append(dados)
except Exception:
continue
return lista_formularios

# --- CARREGAMENTO INICIAL ---
# Agora chamamos a função que criamos para ler os arquivos individuais
if &quot;formularios&quot; not in st.session_state:

st.session_state[&quot;formularios&quot;] = carregar_todos_formularios()
# ============================================================
# LOGIN (Com Bypass para o Formulário)
# ============================================================
# Só bloqueia o acesso se NÃO estiver logado E NÃO for a página de formulário
if not st.session_state.logged_in and st.session_state.pagina != &quot;formulario&quot;:
st.title(&quot;   Acesso&quot;)
usuario = st.text_input(&quot;Usuário&quot;)
senha = st.text_input(&quot;Senha&quot;, type=&quot;password&quot;)

if st.button(&quot;Entrar&quot;, key=&quot;login_button&quot;):
if (usuario == &quot;admin&quot; and senha == &quot;admin123&quot;) or (usuario == &quot;Luciano&quot; and senha ==
&quot;123&quot;):
st.session_state.logged_in = True
st.session_state.user_nome = usuario
st.session_state.is_admin = True

# ATUALIZAÇÃO: Definimos a variável que o painel de exportação espera
if usuario == &quot;Luciano&quot;:
st.session_state[&quot;usuario_logado&quot;] = &quot;Luciano 123&quot;
else:
st.session_state[&quot;usuario_logado&quot;] = usuario

st.rerun()
else:
st.error(&quot;Usuário ou senha incorretos&quot;)

st.stop()

# ============================================================
# SIDEBAR

# ============================================================

st.sidebar.title("📌 Menu de Navegação")

btn_home = st.sidebar.button("🏠 Home")
btn_analise = st.sidebar.button("📊 Análise Inteligente")
btn_comparar = st.sidebar.button("⚖️ Comparar Colaboradores")
btn_disc = st.sidebar.button("🧠 Perfil DISC")
btn_parecer = st.sidebar.button("📄 Parecer Estratégico")
btn_visualizar = st.sidebar.button("👁️ Visualizar Dados")
btn_produtividade = st.sidebar.button("🚀 Produtividade")

st.sidebar.markdown(&quot;---&quot;)

btn_logout = st.sidebar.button(&quot;   Logout&quot;)

pagina_anterior = st.session_state.pagina

if btn_home:
st.session_state.pagina = &quot;home&quot;
elif btn_analise:
st.session_state.pagina = &quot;analise&quot;
elif btn_comparar:
st.session_state.pagina = &quot;comparar&quot;
elif btn_disc:
st.session_state.pagina = &quot;disc&quot;
elif btn_parecer:
st.session_state.pagina = &quot;parecer&quot;
elif btn_visualizar:
st.session_state.pagina = &quot;visualizar&quot;

# O elif abaixo verifica a URL sem precisar de botão
elif st.session_state.pagina == &quot;formulario&quot;:
pass # Este comando é obrigatório para não dar erro de sintaxe
elif btn_logout:
st.session_state.logged_in = False
st.session_state.pagina = &quot;home&quot;

if pagina_anterior != st.session_state.pagina:
st.rerun()

import streamlit as st
import pandas as pd
import os
import json
import sys

# ============================================================
# CONFIGURAÇÃO DE DIRETÓRIO E CARREGAMENTO
# ============================================================

# Define o diretório base e a pasta de dados
base_dir = os.path.dirname(os.path.abspath(__file__))
dados_dir = os.path.join(base_dir, &quot;dados&quot;)
os.makedirs(dados_dir, exist_ok=True)

# Função para carregar todos os JSONs da pasta &#39;dados&#39;
def carregar_todos_formularios():
lista_formularios = []
if os.path.exists(dados_dir):
for nome_arquivo in os.listdir(dados_dir):
if nome_arquivo.endswith(&quot;.json&quot;):

caminho_completo = os.path.join(dados_dir, nome_arquivo)
try:
with open(caminho_completo, &quot;r&quot;, encoding=&quot;utf-8&quot;) as f:
dados = json.load(f)
if isinstance(dados, dict):
lista_formularios.append(dados)
except Exception:
continue
return lista_formularios

# Inicializa o estado da sessão com os dados carregados
if &quot;formularios&quot; not in st.session_state:
st.session_state[&quot;formularios&quot;] = carregar_todos_formularios()

# --- BLOCO DE CSS PARA OCULTAÇÃO ---
if st.query_params.get(&quot;page&quot;) == &quot;formulario&quot;:
st.markdown(&quot;&quot;&quot;
&lt;style&gt;
[data-testid=&quot;stSidebar&quot;] {display: none !important;}
#MainMenu, footer, header {visibility: hidden !important;}
&lt;/style&gt;
&quot;&quot;&quot;, unsafe_allow_html=True)
# --- LISTA DE PERGUNTAS DISC ---
perguntas_disc = [
&quot;Quando surge um problema inesperado: (A) Age rápido | (B) Comunica a todos | (C) Analisa
riscos | (D) Segue processo&quot;,
&quot;Em situações de pressão: (A) Foca no resultado | (B) Mantém o otimismo | (C) Mantém a
calma | (D) Busca precisão&quot;,
&quot;Ao receber tarefa difícil: (A) Aceita o desafio | (B) Busca ajuda social | (C) Planeja passos |
(D) Estuda as regras&quot;,
&quot;No trabalho em equipe: (A) Lidera o grupo | (B) Motiva os colegas | (C) Apoia os outros |
(D) Organiza as tarefas&quot;,

&quot;Em reuniões: (A) Vai direto ao ponto | (B) Interage e brinca | (C) Escuta mais | (D) Anota
detalhes&quot;,
&quot;Ao lidar com conflitos: (A) Enfrenta direto | (B) Tenta apaziguar | (C) Evita o confronto | (D)
Usa lógica e fatos&quot;,
&quot;Seu ritmo de trabalho: (A) Rápido/Impaciente | (B) Rápido/Entusiasmado | (C)
Calmo/Constante | (D) Metódico/Cauteloso&quot;,
&quot;Prefere tarefas: (A) Desafiadoras | (B) Variadas e sociais | (C) Rotineiras e seguras | (D)
Técnicas e detalhadas&quot;,
&quot;Seu foco principal: (A) Resultados | (B) Relacionamentos | (C) Estabilidade | (D) Qualidade e
Processos&quot;,
&quot;Ao decidir, você é: (A) Decidido e firme | (B) Impulsivo e intuitivo | (C) Cuidadoso e lento |
(D) Lógico e analítico&quot;,
&quot;Confia mais em: (A) Sua intuição | (B) Opinião alheia | (C) Experiência passada | (D) Dados e
provas&quot;,
&quot;Prefere decisões: (A) Independentes | (B) Em grupo | (C) Consensuais | (D) Baseadas em
normas&quot;,
&quot;Estilo de organização: (A) Prático | (B) Criativo/Bagunçado | (C) Tradicional | (D) Muito
organizado&quot;,
&quot;Lida melhor com: (A) Mudanças rápidas | (B) Novas ideias | (C) Rotinas claras | (D) Regras
rígidas&quot;,
&quot;Prefere trabalhar: (A) Sozinho/Comando | (B) Ambiente festivo | (C) Ambiente tranquilo |
(D) Ambiente silencioso&quot;,
&quot;Seu ponto forte: (A) Coragem | (B) Comunicação | (C) Paciência | (D) Organização&quot;,
&quot;Você se considera: (A) Dominante | (B) Influente | (C) Estável | (D) Conforme/Analítico&quot;,
&quot;Se motiva por: (A) Poder/Bônus | (B) Reconhecimento | (C) Segurança/Paz | (D)
Conhecimento Técnico&quot;,
&quot;Reação a cobranças: (A) Mais esforço | (B) Desculpas criativas | (C) Ansiedade | (D)
Argumentos técnicos&quot;,
&quot;Ambiente ideal: (A) Competitivo | (B) Amigável | (C) Previsível | (D) Disciplinado&quot;,
&quot;Ao lidar com feedback: (A) Aceita e ajusta | (B) Comenta e debate | (C) Analisa e planeja |
(D) Segue regras&quot;,
&quot;Como prefere aprender: (A) Fazendo | (B) Interagindo | (C) Observando | (D) Estudando
materiais&quot;,
&quot;Gestão de tempo: (A) Prioriza resultados | (B) Mantém relações | (C) Planeja com cuidado |
(D) Segue processos&quot;,
&quot;Como se comunica: (A) Direto e objetivo | (B) Amigável e motivador | (C) Calmo e
ponderado | (D) Técnico e detalhista&quot;

]

# --- FORMULÁRIO ---
if st.query_params.get(&quot;page&quot;) == &quot;formulario&quot;:
st.title(&quot;   Formulário Completo do Colaborador&quot;)

# Listas padronizadas (devem vir antes do form)
lista_horas = [f&quot;{i} h&quot; for i in range(25)]
lista_minutos = [f&quot;{i} min&quot; for i in range(0, 60, 5)]
lista_frequencia = [&quot;DVD&quot;, &quot;D&quot;, &quot;S&quot;, &quot;Q&quot;, &quot;M&quot;, &quot;T&quot;, &quot;A&quot;]

# ÚNICO BLOCO DO FORMULÁRIO
with st.form(&quot;form_colaborador&quot;):
# Dados de Identificação
col1, col2 = st.columns(2)
nome = col1.text_input(&quot;Nome do colaborador&quot;)
setor = col2.text_input(&quot;Setor&quot;)
cargo = col1.text_input(&quot;Cargo&quot;)
chefe = col2.text_input(&quot;Chefe imediato&quot;)
departamento = col1.text_input(&quot;Departamento&quot;)
empresa = col2.text_input(&quot;Empresa / Unidade&quot;)
escolaridade = col1.text_input(&quot;Escolaridade&quot;)
devolucao = col2.text_input(&quot;Devolver preenchido em&quot;)

cursos = st.text_area(&quot;Cursos obrigatórios ou diferenciais&quot;)
objetivo = st.text_area(&quot;Trabalho e principal objetivo&quot;)

# --- SEÇÃO DE ATIVIDADES ---

st.markdown(&quot;---&quot;)

# Mude para 3 colunas
col1, col2, col3 = st.columns(3)

# Supondo que você tenha definido col1, col2 e col3 anteriormente
with col1:
st.info(&quot;&quot;&quot;
**   LEGENDA DE FREQUÊNCIA:**
* **DVD**: Diário Várias Vezes
* **D**: Diário | **S**: Semanal
* **Q**: Quinzenal | **M**: Mensal
* **T**: Trimestral | **A**: Anual
&quot;&quot;&quot;)

with col2:
st.warning(&quot;&quot;&quot;
**⏱️ COMO REGISTRAR O TEMPO:**
* **Horas e Minutos**: Selecione o valor em cada coluna.
* **Menos de 1 hora?**: Selecione **0 h** e o tempo real em minutos.
* **Não se aplica?**: Selecione **0 h** e **0 min** em ambos.
&quot;&quot;&quot;)

with col3:
st.error(&quot;&quot;&quot;
**⚠️ DETALHE:**
* A numeração lateral (nones) é um comportamento nativo do sistema que polui a
página.
* Ignore-a e preencha normalmente; isso não afeta em nada os seus dados.
&quot;&quot;&quot;)

st.subheader(&quot;   Atividades Executadas&quot;)

edit_ativ = st.data_editor(
pd.DataFrame({
&quot;Atividade Descrita&quot;: [&quot;&quot;] * 20,
&quot;Frequência&quot;: [&quot;&quot;] * 20,
&quot;Horas&quot;: [&quot;&quot;] * 20,
&quot;Minutos&quot;: [&quot;&quot;] * 20
}).reset_index(drop=True), # Limpeza do índice
column_config={
&quot;Frequência&quot;: st.column_config.SelectboxColumn(&quot;Frequência&quot;,
options=lista_frequencia),
&quot;Horas&quot;: st.column_config.SelectboxColumn(&quot;Horas&quot;, options=lista_horas),
&quot;Minutos&quot;: st.column_config.SelectboxColumn(&quot;Minutos&quot;, options=lista_minutos),
},
hide_index=True,
num_rows=&quot;fixed&quot;,
use_container_width=True
)

# --- SEÇÃO DE DIFICULDADES ---
st.markdown(&quot;---&quot;)
st.subheader(&quot;⚠️ Dificuldades e Bloqueios&quot;)

edit_dif = st.data_editor(
pd.DataFrame({
&quot;Dificuldade&quot;: [&quot;&quot;] * 20,
&quot;Setor/Parceiro Envolvido&quot;: [&quot;&quot;] * 20,
&quot;Horas Perdidas&quot;: [&quot;&quot;] * 20,

&quot;Minutos Perdidos&quot;: [&quot;&quot;] * 20
}).reset_index(drop=True), # Limpeza do índice para remover os &quot;nones&quot;
column_config={
&quot;Horas Perdidas&quot;: st.column_config.SelectboxColumn(
&quot;Horas Perdidas&quot;,
options=lista_horas
),
&quot;Minutos Perdidos&quot;: st.column_config.SelectboxColumn(
&quot;Minutos Perdidos&quot;,
options=lista_minutos
),
},
hide_index=True,
num_rows=&quot;fixed&quot;,
use_container_width=True,
key=&quot;dif_editor&quot;
)

# --- SEÇÃO DE SUGESTÕES ATUALIZADA ---
st.markdown(&quot;---&quot;)
st.subheader(&quot;   Sugestões de Melhoria e Impacto&quot;)

edit_sug = st.data_editor(
pd.DataFrame({
&quot;Sugestão de Melhoria&quot;: [&quot;&quot;] * 20,
&quot;Impacto Esperado&quot;: [&quot;&quot;] * 20,
&quot;Redução Horas&quot;: [&quot;&quot;] * 20,
&quot;Redução Minutos&quot;: [&quot;&quot;] * 20,
&quot;Frequência do Impacto&quot;: [&quot;&quot;] * 20
}).reset_index(drop=True),
column_config={

&quot;Redução Horas&quot;: st.column_config.SelectboxColumn(
&quot;Redução Horas&quot;,
options=lista_horas
),
&quot;Redução Minutos&quot;: st.column_config.SelectboxColumn(
&quot;Redução Minutos&quot;,
options=lista_minutos
),
&quot;Frequência do Impacto&quot;: st.column_config.SelectboxColumn(
&quot;Frequência do Impacto&quot;,
options=lista_frequencia
),
},
hide_index=True,
num_rows=&quot;fixed&quot;,
use_container_width=True,
key=&quot;sug_editor&quot;
)

st.markdown(&quot;---&quot;)
st.subheader(&quot;   Questionário DISC&quot;)
for i, pergunta in enumerate(perguntas_disc, 1):
st.radio(
label=f&quot;{i}. {pergunta}&quot;,
options=[&quot;A&quot;, &quot;B&quot;, &quot;C&quot;, &quot;D&quot;],
key=f&quot;disc_{i}&quot;,
horizontal=True,

index=None
)
# BOTÃO DO FORMULÁRIO
enviar = st.form_submit_button(&quot;   ENVIAR FORMULÁRIO FINAL&quot;)

# -------------------------------------------------
# VALIDAÇÕES E PROCESSAMENTO
# -------------------------------------------------

if enviar:

# 1. VALIDAÇÃO DE CAMPOS
if not nome or not setor or not cargo or not chefe or not departamento or not empresa:
st.error(&quot;⚠️ Erro: Preencha todos os campos de identificação!&quot;)

# 2. VALIDAÇÃO DO DISC
elif any(st.session_state.get(f&quot;disc_{i}&quot;) is None for i in range(1, 25)):
st.error(&quot;⚠️ Erro: Responda todas as perguntas do DISC!&quot;)

else:

import os
import json

base_dir = os.path.dirname(os.path.abspath(__file__))
dados_dir = os.path.join(base_dir, &quot;dados&quot;)
os.makedirs(dados_dir, exist_ok=True)

# 3. EVITAR DUPLICIDADE
nome_limpo = nome.strip().replace(&quot; &quot;, &quot;_&quot;)
arquivos_existentes = [f for f in os.listdir(dados_dir) if f.startswith(nome_limpo)]

if arquivos_existentes:
st.error(f&quot;⚠️ Já existe um formulário enviado para &#39;{nome}&#39;.&quot;)

else:

# 4. CONFIRMAÇÃO
if not st.session_state.get(&quot;confirmado&quot;, False):

st.warning(
&quot;⚠️ Revise o formulário. Clique novamente no botão para confirmar o envio.&quot;
)

st.session_state[&quot;confirmado&quot;] = True

# 5. ENVIO FINAL
else:

st.success(&quot;✅ Formulário enviado com sucesso!&quot;)

dados = {
&quot;nome&quot;: nome,
&quot;setor&quot;: setor,
&quot;cargo&quot;: cargo,
&quot;chefe&quot;: chefe,
&quot;departamento&quot;: departamento,
&quot;empresa&quot;: empresa,
&quot;escolaridade&quot;: escolaridade,
&quot;devolucao&quot;: devolucao,
&quot;cursos&quot;: cursos,
&quot;objetivo&quot;: objetivo,

&quot;atividades&quot;: edit_ativ.to_dict(),
&quot;dificuldades&quot;: edit_dif.to_dict(),
&quot;sugestoes&quot;: edit_sug.to_dict(),
&quot;disc&quot;: {
f&quot;disc_{i}&quot;: st.session_state.get(f&quot;disc_{i}&quot;)
for i in range(1, 25)
}
}

caminho = os.path.join(dados_dir, f&quot;{nome_limpo}.json&quot;)

with open(caminho, &quot;w&quot;, encoding=&quot;utf-8&quot;) as f:
json.dump(dados, f, ensure_ascii=False, indent=4)

st.session_state[&quot;confirmado&quot;] = False

# --- VISUALIZAÇÃO ---
if st.session_state.get(&quot;pagina&quot;) == &quot;visualizar&quot;:
st.title(&quot;  ️ Visualização de Registros&quot;)

# 1. Carrega os dados frescos do disco
lista_de_arquivos = carregar_todos_formularios()

# 2. Se a sua função carregar_todos_formularios() já retorna a lista,
# apenas certifique-se de que não estamos adicionando isso ao session_state de forma
acumulativa.
if not lista_de_arquivos:
st.warning(&quot;⚠️ Nenhum formulário encontrado.&quot;)
else:
# Mostra o total para conferência

st.success(f&quot;Foram encontrados {len(lista_de_arquivos)} formulários.&quot;)

# 3. Exibição limpa
for idx, form in enumerate(lista_de_arquivos, 1):
nome_exibir = str(form.get(&#39;Nome&#39;, f&#39;Colaborador {idx}&#39;)).upper()

with st.expander(f&quot;   FORMULÁRIO DE: {nome_exibir} ({form.get(&#39;DataEnvio&#39;, &#39;Sem
Data&#39;)})&quot;):
# [Aqui você mantém o seu código de exibição de dados]

# 1. Cabeçalho Completo
st.subheader(&quot;   Informações de Identificação&quot;)
col1, col2 = st.columns(2)
col1.write(f&quot;**Data de Envio:** {form.get(&#39;DataEnvio&#39;, &#39;N/A&#39;)}&quot;)
col2.write(f&quot;**Devolver em:** {form.get(&#39;Devolver&#39;, &#39;N/A&#39;)}&quot;)

col_a, col_b = st.columns(2)
col_a.write(f&quot;**Setor:** {form.get(&#39;Setor&#39;, &#39;N/A&#39;)}&quot;)
col_b.write(f&quot;**Departamento:** {form.get(&#39;Departamento&#39;, &#39;N/A&#39;)}&quot;)
col_a.write(f&quot;**Cargo:** {form.get(&#39;Cargo&#39;, &#39;N/A&#39;)}&quot;)
col_b.write(f&quot;**Chefe Imediato:** {form.get(&#39;Chefe&#39;, &#39;N/A&#39;)}&quot;)
col_a.write(f&quot;**Empresa/Unidade:** {form.get(&#39;Empresa&#39;, &#39;N/A&#39;)}&quot;)
col_b.write(f&quot;**Escolaridade:** {form.get(&#39;Escolaridade&#39;, &#39;N/A&#39;)}&quot;)

st.write(f&quot;**Cursos:** {form.get(&#39;Cursos&#39;, &#39;N/A&#39;)}&quot;)
st.info(f&quot;**Objetivo Principal:**\n\n{form.get(&#39;Objetivo&#39;, &#39;N/A&#39;)}&quot;)

# 2. Tabelas Dinâmicas

secoes = {
&quot;Atividades&quot;: &quot;   Atividades Executadas&quot;,
&quot;Dificuldades&quot;: &quot;⚠️ Dificuldades e Bloqueios&quot;,
&quot;Sugestoes&quot;: &quot;   Sugestões de Melhoria&quot;
}

for chave, titulo in secoes.items():
st.markdown(&quot;---&quot;)
st.subheader(titulo)
if chave in form and form[chave]:
df = pd.DataFrame(form[chave])
df = df.replace(&quot;&quot;, None).dropna(how=&#39;all&#39;)
if not df.empty:
st.table(df)
else:
st.write(&quot;Nenhum dado preenchido nesta seção.&quot;)
else:
st.write(&quot;Seção não encontrada ou vazia.&quot;)

# 3. Questionário DISC (Exibição Completa e Legível)
st.markdown(&quot;---&quot;)
st.subheader(&quot;   Avaliação DISC (Perguntas e Respostas)&quot;)

for i, pergunta in enumerate(perguntas_disc, 1):
valor_resposta = form.get(f&quot;Q{i}&quot;, &quot;Não respondido&quot;)
st.write(f&quot;**{i}. {pergunta}**&quot;)
st.info(f&quot;Resposta selecionada: **{valor_resposta}**&quot;)
st.markdown(&quot;---&quot;)

# --- BLOCO DE EXPORTAÇÃO (SÓ WORD E PDF) ---
if st.session_state.get(&quot;usuario_logado&quot;) == &quot;Luciano 123&quot;:

st.markdown(&quot;---&quot;)
st.subheader(&quot;⚙️ Painel de Exportação&quot;)

# Usamos 2 colunas para ficar mais harmônico
col1, col2 = st.columns(2)

# Padronização do nome do arquivo para ambos
data_clean = form.get(&#39;DataEnvio&#39;, &#39;&#39;).replace(&#39;/&#39;, &#39;&#39;).replace(&#39; &#39;, &#39;_&#39;).replace(&#39;:&#39;, &#39;&#39;)
nome_clean = form.get(&#39;Nome&#39;, &#39;Colaborador&#39;).replace(&#39; &#39;, &#39;_&#39;)
nome_arquivo = f&quot;Relatorio_{nome_clean}_{data_clean}&quot;

with col1:
st.download_button(
label=&quot;   Baixar em Word&quot;,
data=gerar_word(form),
file_name=f&quot;{nome_arquivo}.docx&quot;,
mime=&quot;application/vnd.openxmlformats-
officedocument.wordprocessingml.document&quot;
)

with col2:
st.download_button(
label=&quot;   Baixar em PDF&quot;,
data=gerar_pdf(form),
file_name=f&quot;{nome_arquivo}.pdf&quot;,
mime=&quot;application/pdf&quot;
)
# --- FIM DO BLOCO ---

# Botão de Limpeza
st.markdown(&quot;---&quot;)
if st.button(&quot;  ️ LIMPAR TODOS OS FORMULÁRIOS&quot;):
for arquivo in os.listdir(dados_dir):
if arquivo.endswith(&quot;.json&quot;):
os.remove(os.path.join(dados_dir, arquivo))
st.session_state[&quot;formularios&quot;] = []
st.success(&quot;✅ Banco de dados limpo!&quot;); st.rerun()

# ============================================================
# CALCULAR DISC PERCENTUAL E DOMINANTE
# ============================================================

def calcular_disc(respostas_disc):
contagem = {&quot;D&quot;:0, &quot;I&quot;:0, &quot;S&quot;:0, &quot;C&quot;:0}
for r in respostas_disc.values():
if r in contagem:
contagem[r] += 1
total = sum(contagem.values())
if total &gt; 0:
percentuais = {k: round(v/total*100,1) for k,v in contagem.items()}
dominante = max(percentuais, key=percentuais.get)
else:
percentuais = contagem
dominante = None
return percentuais, dominante

# ============================================================
# SCORE DISC PONDERADO
# ============================================================

def score_disc(disc):
pesos = {&quot;D&quot;:1.0,&quot;I&quot;:0.9,&quot;S&quot;:0.85,&quot;C&quot;:0.95}
total = sum(disc.values())
if total == 0:
return 0
calculo = sum(disc[k]*pesos.get(k,1) for k in disc)
return round((calculo/total)*100,2)

# ============================================================
# CALCULAR CARGA HORÁRIA
# ============================================================

def calcular_carga(atividades):
total_min = 0
for at in atividades:
try:
tempo = float(at.get(&quot;tempo&quot;,&quot;0&quot;))
except:
tempo = 0
freq = at.get(&quot;frequencia&quot;,&quot;semanal&quot;).lower()
if freq == &quot;diaria&quot;:
total_min += tempo * 5
elif freq == &quot;mensal&quot;:
total_min += tempo / 4
else:
total_min += tempo
horas = total_min / 60
status = &quot;Adequado&quot;
if horas &gt; 44: status = &quot;Sobrecarga&quot;
elif horas &lt; 30: status = &quot;Subutilização&quot;
return round(horas,2), status

# ============================================================
# GERAR ATIVIDADES IDEAIS (GPT)
# ============================================================

def gerar_atividades_ideais(cargo, setor, client=None):
if client is None:
return [{
&quot;nome_atividade&quot;: &quot;Atividade de exemplo&quot;,
&quot;descricao&quot;: &quot;Descrição de exemplo&quot;,
&quot;frequencia_ideal&quot;: &quot;semanal&quot;,
&quot;tempo_medio_minutos&quot;: 60,
&quot;justificativa_tecnica&quot;: &quot;Exemplo&quot;
}]

prompt = f&quot;&quot;&quot;
Gere 12 atividades ideais para:
Cargo: {cargo}
Setor: {setor}
Para cada atividade informe:
- nome_atividade
- descricao
- frequencia_ideal
- tempo_medio_minutos
- justificativa_tecnica
Responda SOMENTE JSON válido.
&quot;&quot;&quot;
try:
response = client.chat.completions.create(
model=&quot;gpt-4o-mini&quot;,
messages=[{&quot;role&quot;:&quot;user&quot;,&quot;content&quot;:prompt}],

temperature=0.3
)
return json.loads(response.choices[0].message.content)
except:
return [{
&quot;nome_atividade&quot;: &quot;Atividade de exemplo&quot;,
&quot;descricao&quot;: &quot;Descrição de exemplo&quot;,
&quot;frequencia_ideal&quot;: &quot;semanal&quot;,
&quot;tempo_medio_minutos&quot;: 60,
&quot;justificativa_tecnica&quot;: &quot;Exemplo&quot;
}]

# ============================================================
# COMPARAÇÃO SEMÂNTICA
# ============================================================

def comparar_semanticamente(reais, ideais, client=None):
if client is None:
return {&quot;score_aderencia&quot;:0,&quot;tempo_gap_medio_percentual&quot;:0,&quot;atividades_desvio&quot;:[]}

prompt = f&quot;&quot;&quot;
Compare semanticamente:
Atividades reais: {reais}
Atividades ideais: {ideais}
Retorne JSON com:
- score_aderencia (0-100)
- tempo_gap_medio_percentual
- atividades_desvio
&quot;&quot;&quot;
try:
r = client.chat.completions.create(

model=&quot;gpt-4o-mini&quot;,
messages=[{&quot;role&quot;:&quot;user&quot;,&quot;content&quot;:prompt}],
temperature=0.2
)
return json.loads(r.choices[0].message.content)
except:
return {&quot;score_aderencia&quot;:0,&quot;tempo_gap_medio_percentual&quot;:0,&quot;atividades_desvio&quot;:[]}

# ============================================================
# CLASSIFICAR DIFICULDADES
# ============================================================

def classificar_dificuldades_gpt(dificuldades, client=None):
if client is None:
return {}

prompt = f&quot;&quot;&quot;
Classifique semanticamente as dificuldades abaixo em:
- Processo
- Tempo
- Comunicação
- Estrutura
- Liderança
- Sistema
Retorne JSON com contagem por categoria.
Dificuldades: {dificuldades}
&quot;&quot;&quot;
try:
r = client.chat.completions.create(
model=&quot;gpt-4o-mini&quot;,
messages=[{&quot;role&quot;:&quot;user&quot;,&quot;content&quot;:prompt}],

temperature=0.2
)
return json.loads(r.choices[0].message.content)
except:
return {}

# ============================================================
# ÍNDICE GERAL DO CARGO
# ============================================================

def indice_geral(score_aderencia, score_disc, status_carga):
fator_carga = 100
if status_carga == &quot;Sobrecarga&quot;: fator_carga = 70
elif status_carga == &quot;Subutilização&quot;: fator_carga = 75
return round(mean([score_aderencia, score_disc, fator_carga]),2)

# ============================================================
# MOTOR PRINCIPAL COMPLETO – ANÁLISE CORPORATIVA
# ============================================================

def gerar_analise_corporativa(dados, client=None):
&quot;&quot;&quot;
Gera análise completa de um colaborador com base em:
- Atividades reais
- Perfil DISC
- Dificuldades
Retorna:
- parecer (texto)
- indicadores (dict)
&quot;&quot;&quot;
# 1️⃣ Atividades ideais

ideais = gerar_atividades_ideais(dados[&quot;cargo&quot;], dados[&quot;setor&quot;], client)

# 2️⃣ Comparação semântica (reais x ideais)
comparacao = comparar_semanticamente(dados[&quot;atividades&quot;], ideais, client)

# 3️⃣ Carga horária
horas, status_carga = calcular_carga(dados[&quot;atividades&quot;])

# 4️⃣ Score DISC
disc_score = score_disc(dados[&quot;disc&quot;])

# 5️⃣ Classificação de dificuldades
dificuldades_classificadas = classificar_dificuldades_gpt(dados[&quot;dificuldades&quot;], client)

# 6️⃣ Score de aderência
score_aderencia = comparacao.get(&quot;score_aderencia&quot;,0)

# 7️⃣ Índice geral
indice = indice_geral(score_aderencia, disc_score, status_carga)

# 8️⃣ Classificação de risco
risco = &quot;Baixo&quot; if indice &lt; 60 else &quot;Moderado&quot; if indice &lt; 75 else &quot;Alto&quot;

# 9️⃣ Prompt final para parecer estratégico
prompt_final = f&quot;&quot;&quot;
Gere parecer estratégico completo considerando:
- Score aderência: {score_aderencia}
- Horas semanais: {horas}
- Status carga: {status_carga}
- Score DISC: {disc_score}
- Dificuldades: {dificuldades_classificadas}

- Índice geral do cargo: {indice}
- Classificação de risco: {risco}

Inclua:
- Diagnóstico estrutural
- Análise de desvios
- Avaliação comportamental
- Riscos organizacionais
- Recomendação detalhada de redistribuição
- Atividades corretas para o cargo com tempo e frequência ideais
- Conclusão executiva
&quot;&quot;&quot;

# 10️⃣ Obter parecer do GPT
parecer = &quot;&quot;
try:
if client:
resposta = client.chat.completions.create(
model=&quot;gpt-4o-mini&quot;,
messages=[{&quot;role&quot;:&quot;user&quot;,&quot;content&quot;:prompt_final}],
temperature=0.3
)
parecer = resposta.choices[0].message.content
else:
parecer = &quot;GPT não disponível. Retorno padrão: análise resumida.&quot;
except:
parecer = &quot;Erro ao gerar parecer com GPT.&quot;

# 11️⃣ Indicadores
indicadores = {
&quot;score_aderencia&quot;: score_aderencia,

&quot;horas_semanais&quot;: horas,
&quot;status_carga&quot;: status_carga,
&quot;score_disc&quot;: disc_score,
&quot;indice_geral&quot;: indice,
&quot;risco&quot;: risco
}

return parecer, indicadores

# ============================================================
# GERAR PDF DO PARECER
# ============================================================

def gerar_pdf(parecer, nome):
&quot;&quot;&quot;
Recebe:
- parecer (texto)
- nome do colaborador
Cria arquivo PDF pronto para download
&quot;&quot;&quot;
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch

nome_arquivo = f&quot;{nome}_parecer.pdf&quot;
doc = SimpleDocTemplate(nome_arquivo)
elements = []
styles = getSampleStyleSheet()

# Título
elements.append(Paragraph(&quot;PARECER ESTRATÉGICO ORGANIZACIONAL&quot;, styles[&quot;Title&quot;]))

elements.append(Spacer(1, 0.5*inch))

# Conteúdo linha a linha
for linha in parecer.split(&quot;\n&quot;):
if linha.strip(): # evita parágrafos vazios
elements.append(Paragraph(linha, styles[&quot;Normal&quot;]))
elements.append(Spacer(1, 0.2*inch))

doc.build(elements)
return nome_arquivo

# ============================================================
# PASTA BASE PARA FORMULÁRIOS (JSON)
# ============================================================
# Usamos &#39;dados_dir&#39; para manter o padrão que já criamos
json_master = os.path.join(dados_dir, &quot;formularios.json&quot;)

# Inicializa arquivo JSON se não existir
if not os.path.exists(json_master):
with open(json_master, &quot;w&quot;, encoding=&quot;utf-8&quot;) as f:
json.dump([], f, ensure_ascii=False, indent=4)

# ============================================================
# FUNÇÃO PARA SALVAR FORMULÁRIO EM JSON
# ============================================================
def salvar_formulario_json(formulario):
&quot;&quot;&quot;
Recebe um dicionário do formulário preenchido, salva no arquivo
JSON único dentro da pasta &#39;dados&#39; e atualiza a sessão para
espelhamento imediato na interface.
&quot;&quot;&quot;
