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
from zoneinfo import ZoneInfo
# ============================================================

# CONFIGURAÇÃO E INICIALIZAÇÃO ÚNICA

# ============================================================

st.set_page_config(

    page_title="Sistema de Análise de Tarefas",

    page_icon="📊",

    layout="wide",

    initial_sidebar_state="expanded"

)



# Inicialização centralizada

if "logged_in" not in st.session_state: st.session_state.logged_in = False

if "pagina" not in st.session_state: st.session_state.pagina = "home"

if "formularios" not in st.session_state: st.session_state["formularios"] = []



# Leitura da URL (Prioridade total para permitir acesso ao formulário)

query_params = st.query_params

if "page" in query_params:

    st.session_state.pagina = query_params["page"]

st.markdown("""
    <style>
    /* Oculta a coluna de índice do data_editor */
    div[data-testid="stDataEditor"] > div > div > div > div:first-child {
        display: none !important;
    }
    </style>
    """, unsafe_allow_html=True)


# --- LISTA DE PERGUNTAS DISC ---
perguntas_disc = [
    "Quando surge um problema inesperado: (A) Age rápido | (B) Comunica a todos | (C) Analisa riscos | (D) Segue processo",
    "Em situações de pressão: (A) Foca no resultado | (B) Mantém o otimismo | (C) Mantém a calma | (D) Busca precisão",
    "Ao receber tarefa difícil: (A) Aceita o desafio | (B) Busca ajuda social | (C) Planeja passos | (D) Estuda as regras",
    "No trabalho em equipe: (A) Lidera o grupo | (B) Motiva os colegas | (C) Apoia os outros | (D) Organiza as tarefas",
    "Em reuniões: (A) Vai direto ao ponto | (B) Interage e brinca | (C) Escuta mais | (D) Anota detalhes",
    "Ao lidar com conflitos: (A) Enfrenta direto | (B) Tenta apaziguar | (C) Evita o confronto | (D) Usa lógica e fatos",
    "Seu ritmo de trabalho: (A) Rápido/Impaciente | (B) Rápido/Entusiasmado | (C) Calmo/Constante | (D) Metódico/Cauteloso",
    "Prefere tarefas: (A) Desafiadoras | (B) Variadas e sociais | (C) Rotineiras e seguras | (D) Técnicas e detalhadas",
    "Seu foco principal: (A) Resultados | (B) Relacionamentos | (C) Estabilidade | (D) Qualidade e Processos",
    "Ao decidir, você é: (A) Decidido e firme | (B) Impulsivo e intuitivo | (C) Cuidadoso e lento | (D) Lógico e analítico",
    "Confia mais em: (A) Sua intuição | (B) Opinião alheia | (C) Experiência passada | (D) Dados e provas",
    "Prefere decisões: (A) Independentes | (B) Em grupo | (C) Consensuais | (D) Baseadas em normas",
    "Estilo de organização: (A) Prático | (B) Criativo/Bagunçado | (C) Tradicional | (D) Muito organizado",
    "Lida melhor com: (A) Mudanças rápidas | (B) Novas ideias | (C) Rotinas claras | (D) Regras rígidas",
    "Prefere trabalhar: (A) Sozinho/Comando | (B) Ambiente festivo | (C) Ambiente tranquilo | (D) Ambiente silencioso",
    "Seu ponto forte: (A) Coragem | (B) Comunicação | (C) Paciência | (D) Organização",
    "Você se considera: (A) Dominante | (B) Influente | (C) Estável | (D) Conforme/Analítico",
    "Se motiva por: (A) Poder/Bônus | (B) Reconhecimento | (C) Segurança/Paz | (D) Conhecimento Técnico",
    "Reação a cobranças: (A) Mais esforço | (B) Desculpas criativas | (C) Ansiedade | (D) Argumentos técnicos",
    "Ambiente ideal: (A) Competitivo | (B) Amigável | (C) Previsível | (D) Disciplinado",
    "Ao lidar com feedback: (A) Aceita e ajusta | (B) Comenta e debate | (C) Analisa e planeja | (D) Segue regras",
    "Como prefere aprender: (A) Fazendo | (B) Interagindo | (C) Observando | (D) Estudando materiais",
    "Gestão de tempo: (A) Prioriza resultados | (B) Mantém relações | (C) Planeja com cuidado | (D) Segue processos",
    "Como se comunica: (A) Direto e objetivo | (B) Amigável e motivador | (C) Calmo e ponderado | (D) Técnico e detalhista"
]

# --- FUNÇÕES DE EXPORTAÇÃO (COLE NO TOPO DO SEU ARQUIVO) ---
from docx import Document
from fpdf import FPDF
import io

def gerar_word(form):
    doc = Document()
    doc.add_heading(f"Relatório: {form.get('Nome', 'Colaborador')}", 0)
    doc.add_paragraph(f"Data de Envio: {form.get('DataEnvio', 'N/A')}")
    
    # 1. Informações Gerais
    doc.add_heading("Informações de Identificação", level=1)
    campos_gerais = ['Setor', 'Departamento', 'Cargo', 'Chefe', 'Empresa', 'Escolaridade', 'Cursos', 'Objetivo']
    for campo in campos_gerais:
        doc.add_paragraph(f"{campo}: {form.get(campo, 'N/A')}")
    
    # 2. Tabelas (Atividades, Dificuldades, Sugestões)
    secoes = {
        "Atividades": ["Atividade Descrita", "Frequência", "Tempo Gasto"],
        "Dificuldades": ["Dificuldade", "Setor/Parceiro Envolvido", "Tempo Perdido"],
        "Sugestoes": ["Sugestão de Melhoria", "Impacto Esperado"]
    }
    
    for chave, colunas in secoes.items():
        if chave in form and isinstance(form[chave], list):
            doc.add_heading(f"📋 {chave}", level=1)
            # Filtra apenas itens que tenham conteúdo real
            dados = [item for item in form[chave] if any(str(item.get(c, '')).strip() for c in colunas)]
            
            if dados:
                table = doc.add_table(rows=1, cols=len(colunas))
                table.style = 'Table Grid'
                # Cabeçalho
                for i, col in enumerate(colunas):
                    table.rows[0].cells[i].text = col
                # Linhas
                for item in dados:
                    row = table.add_row().cells
                    for i, col in enumerate(colunas):
                        row[i].text = str(item.get(col, ''))
            else:
                doc.add_paragraph("Nenhum dado preenchido nesta seção.")

    # 3. Avaliação DISC
    doc.add_heading("📊 Avaliação DISC (Perguntas e Respostas)", level=1)
    for i, pergunta in enumerate(perguntas_disc, 1):
        valor_resposta = form.get(f"Q{i}", "Não respondido")
        doc.add_paragraph(f"{i}. {pergunta}", style='Heading 2')
        doc.add_paragraph(f"Resposta: {valor_resposta}")
        doc.add_paragraph("-" * 20)
    
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
    elementos.append(Paragraph(f"Relatório: {form.get('Nome', 'Colaborador')}", styles['Title']))
    elementos.append(Paragraph(f"Data: {form.get('DataEnvio', 'N/A')}", styles['Normal']))
    elementos.append(Spacer(1, 12))

    # Informações Gerais
    elementos.append(Paragraph("Informações Gerais", styles['Heading2']))
    campos_gerais = ['Setor', 'Departamento', 'Cargo', 'Chefe', 'Empresa', 'Escolaridade', 'Cursos', 'Objetivo']
    for campo in campos_gerais:
        elementos.append(Paragraph(f"<b>{campo}:</b> {form.get(campo, 'N/A')}", styles['Normal']))
    
    elementos.append(Spacer(1, 12))

    # Tabelas (Atividades, Dificuldades, Sugestoes)
    secoes = {
        "Atividades": ["Atividade Descrita", "Frequência", "Tempo Gasto"],
        "Dificuldades": ["Dificuldade", "Setor/Parceiro Envolvido", "Tempo Perdido"],
        "Sugestoes": ["Sugestão de Melhoria", "Impacto Esperado"]
    }
    
    for titulo, colunas in secoes.items():
        if titulo in form and isinstance(form[titulo], list):
            elementos.append(Paragraph(titulo, styles['Heading2']))
            dados = [item for item in form[titulo] if any(str(item.get(c, '')).strip() for c in colunas)]
            
            if dados:
                data = [colunas] # Cabeçalho
                for item in dados:
                    data.append([str(item.get(c, '')) for c in colunas])
                
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
    elementos.append(Paragraph("Avaliação DISC", styles['Heading2']))
    for i, pergunta in enumerate(perguntas_disc, 1):
        valor_resposta = form.get(f"Q{i}", "Não respondido")
        elementos.append(Paragraph(f"<b>{i}. {pergunta}</b>", styles['Normal']))
        elementos.append(Paragraph(f"Resposta: {valor_resposta}", styles['Italic']))
        elementos.append(Spacer(1, 6))

    doc.build(elementos)
    buffer.seek(0)
    return buffer

# ============================================================
# CALCULAR DISC PERCENTUAL E DOMINANTE
# ============================================================

def calcular_disc(respostas_disc):
    contagem = {"D":0, "I":0, "S":0, "C":0}
    for r in respostas_disc.values():
        if r in contagem:
            contagem[r] += 1
    total = sum(contagem.values())
    if total > 0:
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
    pesos = {"D":1.0,"I":0.9,"S":0.85,"C":0.95}
    total = sum(disc.values())
    if total == 0:
        return 0
    calculo = sum(disc[k]*pesos.get(k,1) for k in disc)
    return round((calculo/total)*100,2)



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
if getattr(sys, 'frozen', False):
    base_dir = os.path.dirname(sys.executable)
else:
    base_dir = os.path.dirname(os.path.abspath(__file__))

# Definimos o diretório de dados como absoluto
dados_dir = os.path.join(base_dir, "dados")

# Criamos a pasta 'dados' se ela não existir
os.makedirs(dados_dir, exist_ok=True)

# --- FUNÇÃO DE CARREGAMENTO DINÂMICO ---
def carregar_todos_formularios():
    """
    Lê todos os arquivos .json da pasta 'dados' individualmente.
    """
    lista_formularios = []
    # Usamos a variável global dados_dir definida acima
    if os.path.exists(dados_dir):
        for nome_arquivo in os.listdir(dados_dir):
            if nome_arquivo.endswith(".json"):
                caminho_completo = os.path.join(dados_dir, nome_arquivo)
                try:
                    with open(caminho_completo, "r", encoding="utf-8") as f:
                        dados = json.load(f)
                        if isinstance(dados, dict):
                            lista_formularios.append(dados)
                except Exception:
                    continue
    return lista_formularios

# --- CARREGAMENTO INICIAL ---
# Agora chamamos a função que criamos para ler os arquivos individuais
if "formularios" not in st.session_state:
    st.session_state["formularios"] = carregar_todos_formularios()
# ============================================================
# LOGIN (Com Bypass para o Formulário)
# ============================================================
# Só bloqueia o acesso se NÃO estiver logado E NÃO for a página de formulário
if not st.session_state.logged_in and st.session_state.pagina != "formulario":
    st.title("🔐 Acesso")
    usuario = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")

    if st.button("Entrar", key="login_button"):
        if (usuario == "admin" and senha == "admin123") or (usuario == "Luciano" and senha == "123"):
            st.session_state.logged_in = True
            st.session_state.user_nome = usuario
            st.session_state.is_admin = True
            
            # ATUALIZAÇÃO: Definimos a variável que o painel de exportação espera
            if usuario == "Luciano":
                st.session_state["usuario_logado"] = "Luciano 123"
            else:
                st.session_state["usuario_logado"] = usuario
                
            st.rerun()
        else:
            st.error("Usuário ou senha incorretos")
    
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


st.sidebar.markdown("---")

btn_logout = st.sidebar.button("🚪 Logout")

pagina_anterior = st.session_state.pagina

if btn_home:
    st.session_state.pagina = "home"
elif btn_analise:
    st.session_state.pagina = "analise"
elif btn_comparar:
    st.session_state.pagina = "comparar"
elif btn_disc:
    st.session_state.pagina = "disc"
elif btn_parecer:
    st.session_state.pagina = "parecer"
elif btn_visualizar:
    st.session_state.pagina = "visualizar"
# O elif abaixo verifica a URL sem precisar de botão
elif st.session_state.pagina == "formulario":
    pass # Este comando é obrigatório para não dar erro de sintaxe
elif btn_logout:
    st.session_state.logged_in = False
    st.session_state.pagina = "home"

if pagina_anterior != st.session_state.pagina:
    st.rerun()

# ============================================================
# PÁGINA PERFIL DISC
# ============================================================

if st.session_state.pagina == "disc":

    import plotly.express as px
    import pandas as pd

    st.title("🧠 Análise de Perfil DISC")

    if not st.session_state.get("formularios"):
        st.warning("Nenhum formulário encontrado.")
        st.stop()

    # ============================================================
    # SELEÇÃO DE COLABORADOR (AJUSTADO)
    # ============================================================

    # Recarregamos a lista para garantir que novos envios apareçam
    st.session_state["formularios"] = carregar_todos_formularios()
    
    # Criamos um dicionário para mapear o texto do selectbox ao objeto real do formulário
    # Isso elimina o erro de busca do 'next'
    opcoes_colaboradores = {
        f"{f.get('nome', 'Sem Nome')} - {f.get('cargo', 'Sem Cargo')}": f 
        for f in st.session_state["formularios"]
    }

    if not opcoes_colaboradores:
        st.warning("Nenhum formulário encontrado na pasta de dados.")
        st.stop()

    colaborador_chave = st.selectbox(
        "Escolha o colaborador",
        options=list(opcoes_colaboradores.keys())
    )

    # Recuperamos o formulário diretamente do dicionário
    formulario_sel = opcoes_colaboradores.get(colaborador_chave)

    # ============================================================
    # BOTÃO GERAR ANÁLISE
    # ============================================================

    if formulario_sel and st.button("🔎 Gerar análise DISC"):

        form = formulario_sel

        mapa_disc = {
            "A": "D",
            "B": "I",
            "C": "S",
            "D": "C"
        }

        # Extraímos as respostas garantindo que o dicionário 'disc' existe no JSON
        respostas_raw = form.get("disc", {})
        respostas_disc = {}

        for k, v in respostas_raw.items():
            if v in mapa_disc:
                respostas_disc[k] = mapa_disc[v]

        # Cálculos
        percentuais, dominante = calcular_disc(respostas_disc)
        score = score_disc(percentuais)

        st.markdown("## 🔹 Painel DISC do Colaborador")
        col1, col2 = st.columns([2,1])

        # ============================================================
        # GRÁFICO DISC
        # ============================================================

        fig = px.bar(
            x=list(percentuais.keys()),
            y=list(percentuais.values()),
            labels={'x':'Tipo','y':'Percentual (%)'},
            text=list(percentuais.values()),
            color=list(percentuais.keys()),
            color_discrete_map={
                "D":"#FF4136",
                "I":"#FF851B",
                "S":"#2ECC40",
                "C":"#0074D9"
            }
        )

        fig.update_layout(
            yaxis_range=[0,100],
            title=f"Distribuição DISC - {form.get('nome','')}"
        )

        fig.update_layout(template="plotly_white")
        fig.update_layout(margin=dict(l=20, r=20, t=40, b=20))
        fig.update_layout(height=400)


        col1.plotly_chart(fig, use_container_width=True)

        # ============================================================
        # MÉTRICAS
        # ============================================================

        col2.metric("Tipo Dominante", dominante if dominante else "N/A")
        col2.metric("Score DISC", f"{score}%")

        # ============================================================
        # BASE DE CONHECIMENTO DISC
        # ============================================================

        disc_info = {

            "D": {
                "caracteristicas": [
                    "Decidido",
                    "Direto",
                    "Focado em resultados",
                    "Competitivo"
                ],
                "cargos": [
                    "Gerente",
                    "Diretor",
                    "Coordenador",
                    "Líder de equipe"
                ],
                "tarefas": [
                    "Tomada de decisão",
                    "Gestão de crises",
                    "Negociação",
                    "Gestão de metas"
                ]
            },

            "I": {
                "caracteristicas": [
                    "Comunicativo",
                    "Sociável",
                    "Persuasivo",
                    "Motivador"
                ],
                "cargos": [
                    "Marketing",
                    "Vendas",
                    "Relacionamento com cliente",
                    "Treinamentos"
                ],
                "tarefas": [
                    "Apresentações",
                    "Networking",
                    "Relacionamento",
                    "Eventos"
                ]
            },

            "S": {
                "caracteristicas": [
                    "Paciente",
                    "Cooperativo",
                    "Leal",
                    "Estável"
                ],
                "cargos": [
                    "RH",
                    "Suporte",
                    "Atendimento",
                    "Administração"
                ],
                "tarefas": [
                    "Treinamento",
                    "Apoio operacional",
                    "Suporte interno",
                    "Gestão de processos"
                ]
            },

            "C": {
                "caracteristicas": [
                    "Analítico",
                    "Detalhista",
                    "Organizado",
                    "Preciso"
                ],
                "cargos": [
                    "Contabilidade",
                    "Controladoria",
                    "Qualidade",
                    "Auditoria"
                ],
                "tarefas": [
                    "Auditorias",
                    "Controle de processos",
                    "Análise de dados",
                    "Padronização"
                ]
            }

        }

        info = disc_info.get(dominante)

        # ============================================================
        # PERFIL COMPORTAMENTAL
        # ============================================================

        if info:

            st.markdown("### 🔹 Características do Perfil")

            colA, colB, colC = st.columns(3)

            colA.write("**Características**")
            for c in info["caracteristicas"]:
                colA.write(f"• {c}")

            colB.write("**Cargos Sugeridos**")
            for c in info["cargos"]:
                colB.write(f"• {c}")

            colC.write("**Tarefas Recomendadas**")
            for t in info["tarefas"]:
                colC.write(f"• {t}")

        # ============================================================
        # PARECER INTEGRADO
        # ============================================================

        st.markdown("### 🔹 Parecer Integrado")

        dificuldades = len(form.get("dificuldades", []))
        sugestoes = len(form.get("sugestoes", []))

        st.info(
            f"""
Perfil predominante **{dominante}**.

Este perfil tende a apresentar melhor desempenho em tarefas como:

{", ".join(info['tarefas']) if info else "Não identificado"}.

O colaborador registrou:

• **{dificuldades} dificuldades operacionais**  
• **{sugestoes} sugestões de melhoria**

A análise indica aderência comportamental às funções que exigem
{", ".join(info['caracteristicas']) if info else "características não identificadas"}.
"""
        )

        # ============================================================
        # DASHBOARD EQUIPE
        # ============================================================

        st.markdown("### 🔹 Distribuição DISC da Equipe")

        df = pd.DataFrame(
            [calcular_disc(f.get("disc", {}))[0] for f in st.session_state["formularios"]]
        )

        fig_eq = px.bar(
            df.sum().reset_index(),
            x="index",
            y=0,
            labels={"index":"Tipo","0":"Total (%)"},
            color="index",
            color_discrete_map={
                "D":"#FF4136",
                "I":"#FF851B",
                "S":"#2ECC40",
                "C":"#0074D9"
            }
        )

        fig_eq.update_layout(template="plotly_white")
        fig_eq.update_layout(margin=dict(l=20, r=20, t=40, b=20))
        fig_eq.update_layout(height=400)

        st.plotly_chart(fig_eq, use_container_width=True)

        # ============================================================
        # RADAR DISC
        # ============================================================

        st.markdown("### 🔹 Radar DISC do Colaborador")

        fig_radar = px.line_polar(
            r=list(percentuais.values()),
            theta=list(percentuais.keys()),
            line_close=True,
            markers=True
        )

        fig_radar.update_traces(
            fill='toself',
            line_color='darkblue'
        )

        fig_radar.update_layout(template="plotly_white")
        fig_radar.update_layout(margin=dict(l=20, r=20, t=40, b=20))
        fig_radar.update_layout(height=400)

        st.plotly_chart(fig_radar, use_container_width=True)

        
        # ============================================================
        # COMPATIBILIDADE CARGO × PERFIL DISC
        # ============================================================

        st.markdown("### 🔹 Compatibilidade Cargo × Perfil DISC")

        cargo_atual = form.get("cargo", "").lower()

        compatibilidade = {
            "D": ["gerente", "diretor", "coordenador", "lider"],
            "I": ["vendas", "marketing", "comercial", "relacionamento"],
            "S": ["rh", "suporte", "atendimento", "administrativo"],
            "C": ["contabilidade", "qualidade", "auditoria", "financeiro"]
        }

        cargos_compatíveis = compatibilidade.get(dominante, [])

        match = any(c in cargo_atual for c in cargos_compatíveis)

        colA, colB = st.columns(2)

        colA.metric("Cargo Atual", form.get("cargo","N/A"))
        colB.metric("Perfil DISC", dominante if dominante else "N/A")

        if match:
            st.success("✔ Alta compatibilidade entre perfil comportamental e cargo atual.")
        else:
            st.warning("⚠ Baixa compatibilidade entre perfil e cargo atual.")

        # gráfico visual de compatibilidade

        df_comp = pd.DataFrame({
            "Indicador":["Compatível","Não compatível"],
            "Valor":[100 if match else 30, 0 if match else 70]
        })

        fig_comp = px.bar(
            df_comp,
            x="Indicador",
            y="Valor",
            color="Indicador",
            color_discrete_map={
                "Compatível":"#2ECC40",
                "Não compatível":"#FF4136"
            }
        )

        fig_comp.update_layout(
            title="Aderência Perfil × Cargo",
            yaxis_range=[0,100]
        )

        st.plotly_chart(fig_comp, use_container_width=True)



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
dados_dir = os.path.join(base_dir, "dados")
os.makedirs(dados_dir, exist_ok=True)

# Função para carregar todos os JSONs da pasta 'dados'
def carregar_todos_formularios():
    lista_formularios = []
    if os.path.exists(dados_dir):
        for nome_arquivo in os.listdir(dados_dir):
            if nome_arquivo.endswith(".json"):
                caminho_completo = os.path.join(dados_dir, nome_arquivo)
                try:
                    with open(caminho_completo, "r", encoding="utf-8") as f:
                        dados = json.load(f)
                        if isinstance(dados, dict):
                            lista_formularios.append(dados)
                except Exception:
                    continue
    return lista_formularios

# Inicializa o estado da sessão com os dados carregados
if "formularios" not in st.session_state:
    st.session_state["formularios"] = carregar_todos_formularios()

# --- BLOCO DE CSS PARA OCULTAÇÃO ---
if st.query_params.get("page") == "formulario":
    st.markdown("""
    <style>
        [data-testid="stSidebar"] {display: none !important;}
        #MainMenu, footer, header {visibility: hidden !important;}
    </style>
    """, unsafe_allow_html=True)
# --- LISTA DE PERGUNTAS DISC ---
perguntas_disc = [
    "Quando surge um problema inesperado: (A) Age rápido | (B) Comunica a todos | (C) Analisa riscos | (D) Segue processo",
    "Em situações de pressão: (A) Foca no resultado | (B) Mantém o otimismo | (C) Mantém a calma | (D) Busca precisão",
    "Ao receber tarefa difícil: (A) Aceita o desafio | (B) Busca ajuda social | (C) Planeja passos | (D) Estuda as regras",
    "No trabalho em equipe: (A) Lidera o grupo | (B) Motiva os colegas | (C) Apoia os outros | (D) Organiza as tarefas",
    "Em reuniões: (A) Vai direto ao ponto | (B) Interage e brinca | (C) Escuta mais | (D) Anota detalhes",
    "Ao lidar com conflitos: (A) Enfrenta direto | (B) Tenta apaziguar | (C) Evita o confronto | (D) Usa lógica e fatos",
    "Seu ritmo de trabalho: (A) Rápido/Impaciente | (B) Rápido/Entusiasmado | (C) Calmo/Constante | (D) Metódico/Cauteloso",
    "Prefere tarefas: (A) Desafiadoras | (B) Variadas e sociais | (C) Rotineiras e seguras | (D) Técnicas e detalhadas",
    "Seu foco principal: (A) Resultados | (B) Relacionamentos | (C) Estabilidade | (D) Qualidade e Processos",
    "Ao decidir, você é: (A) Decidido e firme | (B) Impulsivo e intuitivo | (C) Cuidadoso e lento | (D) Lógico e analítico",
    "Confia mais em: (A) Sua intuição | (B) Opinião alheia | (C) Experiência passada | (D) Dados e provas",
    "Prefere decisões: (A) Independentes | (B) Em grupo | (C) Consensuais | (D) Baseadas em normas",
    "Estilo de organização: (A) Prático | (B) Criativo/Bagunçado | (C) Tradicional | (D) Muito organizado",
    "Lida melhor com: (A) Mudanças rápidas | (B) Novas ideias | (C) Rotinas claras | (D) Regras rígidas",
    "Prefere trabalhar: (A) Sozinho/Comando | (B) Ambiente festivo | (C) Ambiente tranquilo | (D) Ambiente silencioso",
    "Seu ponto forte: (A) Coragem | (B) Comunicação | (C) Paciência | (D) Organização",
    "Você se considera: (A) Dominante | (B) Influente | (C) Estável | (D) Conforme/Analítico",
    "Se motiva por: (A) Poder/Bônus | (B) Reconhecimento | (C) Segurança/Paz | (D) Conhecimento Técnico",
    "Reação a cobranças: (A) Mais esforço | (B) Desculpas criativas | (C) Ansiedade | (D) Argumentos técnicos",
    "Ambiente ideal: (A) Competitivo | (B) Amigável | (C) Previsível | (D) Disciplinado",
    "Ao lidar com feedback: (A) Aceita e ajusta | (B) Comenta e debate | (C) Analisa e planeja | (D) Segue regras",
    "Como prefere aprender: (A) Fazendo | (B) Interagindo | (C) Observando | (D) Estudando materiais",
    "Gestão de tempo: (A) Prioriza resultados | (B) Mantém relações | (C) Planeja com cuidado | (D) Segue processos",
    "Como se comunica: (A) Direto e objetivo | (B) Amigável e motivador | (C) Calmo e ponderado | (D) Técnico e detalhista"
]


# --- FORMULÁRIO ---
if st.query_params.get("page") == "formulario":
    st.title("📋 Formulário Completo do Colaborador")
    
    # Listas padronizadas (devem vir antes do form)
    lista_horas = [f"{i} h" for i in range(25)]
    lista_minutos = [f"{i} min" for i in range(0, 60, 5)]
    lista_frequencia = ["DVD", "D", "S", "Q", "M", "T", "A"]
    
    # ÚNICO BLOCO DO FORMULÁRIO
    with st.form("form_colaborador"):
        # Dados de Identificação
        col1, col2 = st.columns(2)
        nome = col1.text_input("Nome do colaborador")
        setor = col2.text_input("Setor")
        cargo = col1.text_input("Cargo")
        chefe = col2.text_input("Chefe imediato")
        departamento = col1.text_input("Departamento")
        empresa = col2.text_input("Empresa / Unidade")
        escolaridade = col1.text_input("Escolaridade")
        devolucao = col2.text_input("Devolver preenchido em")
        
        cursos = st.text_area("Cursos obrigatórios ou diferenciais")
        objetivo = st.text_area("Trabalho e principal objetivo")
        
        
        
        # --- SEÇÃO DE ATIVIDADES ---
        st.markdown("---")
        
        # Mude para 3 colunas
        col1, col2, col3 = st.columns(3)
        
        # Supondo que você tenha definido col1, col2 e col3 anteriormente
        with col1:
            st.info("""
            **📋 LEGENDA DE FREQUÊNCIA:**
            * **DVD**: Diário Várias Vezes
            * **D**: Diário | **S**: Semanal
            * **Q**: Quinzenal | **M**: Mensal
            * **T**: Trimestral | **A**: Anual
            """)

        with col2:
            st.warning("""
            **⏱️ COMO REGISTRAR O TEMPO:**
            * **Horas e Minutos**: Selecione o valor em cada coluna.
            * **Menos de 1 hora?**: Selecione **0 h** e o tempo real em minutos.
            * **Não se aplica?**: Selecione **0 h** e **0 min** em ambos.
            """)
            
        with col3:
            st.error("""
            **⚠️ DETALHE:**
            * A numeração lateral (nones) é um comportamento nativo do sistema que polui a página.
            * Ignore-a e preencha normalmente; isso não afeta em nada os seus dados.
            """)        
        
        
        
        st.subheader("🔹 Atividades Executadas")
        
        edit_ativ = st.data_editor(
            pd.DataFrame({
                "Atividade Descrita": [""] * 20,
                "Frequência": [""] * 20,
                "Horas": [""] * 20,
                "Minutos": [""] * 20
            }).reset_index(drop=True), # Limpeza do índice
            column_config={
                "Frequência": st.column_config.SelectboxColumn("Frequência", options=lista_frequencia),
                "Horas": st.column_config.SelectboxColumn("Horas", options=lista_horas),
                "Minutos": st.column_config.SelectboxColumn("Minutos", options=lista_minutos),
            },
            hide_index=True,
            num_rows="fixed",
            use_container_width=True
        )

        # --- SEÇÃO DE DIFICULDADES ---
        st.markdown("---")
        st.subheader("⚠️ Dificuldades e Bloqueios")
        
        edit_dif = st.data_editor(
                pd.DataFrame({
                        "Dificuldade": [""] * 20,
                        "Setor/Parceiro Envolvido": [""] * 20,
                        "Frequência": [""] * 20,
                        "Horas Perdidas": [""] * 20,
                        "Minutos Perdidos": [""] * 20
                }),
                column_config={
                        "Frequência": st.column_config.SelectboxColumn(
                                "Frequência", 
                                options=lista_frequencia
                        ),
                        "Horas Perdidas": st.column_config.SelectboxColumn(
                                "Horas Perdidas", 
                                options=lista_horas
                        ),
                        "Minutos Perdidos": st.column_config.SelectboxColumn(
                                "Minutos Perdidos", 
                                options=lista_minutos
                        ),
                },
                hide_index=True,
                num_rows="fixed",
                use_container_width=True,
                key="dif_editor"
        )

        # --- SEÇÃO DE SUGESTÕES ATUALIZADA ---
        st.markdown("---")
        st.subheader("💡 Sugestões de Melhoria e Impacto")
        
        edit_sug = st.data_editor(
            pd.DataFrame({
                "Sugestão de Melhoria": [""] * 20,
                "Impacto Esperado": [""] * 20,
                "Redução Horas": [""] * 20,
                "Redução Minutos": [""] * 20,
                "Frequência do Impacto": [""] * 20
            }).reset_index(drop=True),
            column_config={
                "Redução Horas": st.column_config.SelectboxColumn(
                    "Redução Horas", 
                    options=lista_horas
                ),
                "Redução Minutos": st.column_config.SelectboxColumn(
                    "Redução Minutos", 
                    options=lista_minutos
                ),
                "Frequência do Impacto": st.column_config.SelectboxColumn(
                    "Frequência do Impacto", 
                    options=lista_frequencia
                ),
            },
            hide_index=True,
            num_rows="fixed",
            use_container_width=True,
            key="sug_editor"
        )

        

        

        st.markdown("---")
        st.subheader("📊 Questionário DISC")
        for i, pergunta in enumerate(perguntas_disc, 1):
            st.radio(
                label=f"{i}. {pergunta}", 
                options=["A", "B", "C", "D"], 
                key=f"disc_{i}", 
                horizontal=True, 
                index=None
            )
        # BOTÃO DO FORMULÁRIO
        enviar = st.form_submit_button("🚀 ENVIAR FORMULÁRIO FINAL")
          
        # -------------------------------------------------
        # VALIDAÇÕES E PROCESSAMENTO
        # -------------------------------------------------
        if enviar:

                # Inicializa pendencias para evitar NameError
                pendencias = {}

                # 1. DEFINIÇÃO DE CAMINHOS E VERIFICAÇÃO DE DUPLICIDADE (PRIORIDADE)
                nome_limpo = nome.strip().replace(" ", "_")
                base_dir = os.path.dirname(os.path.abspath(__file__))
                dados_dir = os.path.join(base_dir, "dados")

                if not os.path.exists(dados_dir):
                    os.makedirs(dados_dir, exist_ok=True)

                arquivo_esperado = f"{nome_limpo}.json"

                # Se o nome foi preenchido e o arquivo já existe, para aqui mesmo!
                if nome.strip() and arquivo_esperado in os.listdir(dados_dir):
                    st.error(f"⚠️ Já existe um formulário enviado para '{nome}'.")
                    st.session_state["confirmado"] = False
                    st.stop()

                # 2. SE NÃO HOUVER DUPLICIDADE, SEGUE PARA AS OUTRAS VALIDAÇÕES

                # -------------------------------------------------
                # 2. IDENTIFICAÇÃO
                # -------------------------------------------------
                campos_ident = {
                        "Nome": nome,
                        "Setor": setor,
                        "Cargo": cargo,
                        "Chefe": chefe,
                        "Departamento": departamento,
                        "Empresa": empresa,
                        "Escolaridade": escolaridade,
                        "Devolução preenchida em": devolucao
                }

                for campo, valor in campos_ident.items():
                        if not valor:
                                pendencias.setdefault("Identificação", []).append(campo)

                # -------------------------------------------------
                # 3. Cursos e Trabalho/Objetivo
                # -------------------------------------------------
                if not cursos:
                        pendencias.setdefault("Cursos e Trabalho/Objetivo", []).append("Cursos")
                if not objetivo:
                        pendencias.setdefault("Cursos e Trabalho/Objetivo", []).append("Trabalho/Principal Objetivo")

                # -------------------------------------------------
                # 4. ATIVIDADES (Mínimo 1 linha completa)
                # -------------------------------------------------
                atividades_limpas = []
                atividade_valida = False
                for i, row in edit_ativ.iterrows():
                        # Verifica se a linha tem qualquer conteúdo
                        tem_algo = any([row["Atividade Descrita"], row["Frequência"], row["Horas"], row["Minutos"]])
                        
                        if tem_algo:
                                faltantes = []
                                if not row["Atividade Descrita"]: faltantes.append("Descrição")
                                if not row["Frequência"]: faltantes.append("Frequência")
                                if row["Horas"] in ["", None]: faltantes.append("Horas")
                                if row["Minutos"] in ["", None]: faltantes.append("Minutos")
                                
                                if not faltantes:
                                        atividade_valida = True
                                        atividades_limpas.append(row.to_dict())
                                else:
                                        pendencias.setdefault("Atividades", []).append(f"Linha {i+1} incompleta: {', '.join(faltantes)}")

                if not atividade_valida:
                        pendencias.setdefault("Atividades", []).append("Preencha pelo menos uma linha completa de Atividades.")

                # -------------------------------------------------
                # 5. DIFICULDADES (Mínimo 1 linha completa)
                # -------------------------------------------------
                dificuldades_limpas = []
                dificuldade_valida = False
                for i, row in edit_dif.iterrows():
                        tem_algo = any([row["Dificuldade"], row["Setor/Parceiro Envolvido"], row["Frequência"], row["Horas Perdidas"], row["Minutos Perdidos"]])
                        
                        if tem_algo:
                                faltantes = []
                                if not row["Dificuldade"]: faltantes.append("Descrição")
                                if not row["Setor/Parceiro Envolvido"]: faltantes.append("Setor/Parceiro")
                                if not row["Frequência"]: faltantes.append("Frequência")
                                if row["Horas Perdidas"] in ["", None]: faltantes.append("Horas")
                                if row["Minutos Perdidos"] in ["", None]: faltantes.append("Minutos")
                                
                                if not faltantes:
                                        dificuldade_valida = True
                                        dificuldades_limpas.append(row.to_dict())
                                else:
                                        pendencias.setdefault("Dificuldades", []).append(f"Linha {i+1} incompleta: {', '.join(faltantes)}")

                if not dificuldade_valida:
                        pendencias.setdefault("Dificuldades", []).append("Preencha pelo menos uma linha completa de Dificuldades.")

                # -------------------------------------------------
                # 6. SUGESTÕES (Mínimo 1 linha completa)
                # -------------------------------------------------
                sugestoes_limpas = []
                sugestao_valida = False
                for i, row in edit_sug.iterrows():
                        tem_algo = any([row["Sugestão de Melhoria"], row["Impacto Esperado"], row["Frequência do Impacto"], row["Redução Horas"], row["Redução Minutos"]])
                        
                        if tem_algo:
                                faltantes = []
                                if not row["Sugestão de Melhoria"]: faltantes.append("Descrição")
                                if not row["Impacto Esperado"]: faltantes.append("Impacto Esperado")
                                if not row["Frequência do Impacto"]: faltantes.append("Frequência")
                                if row["Redução Horas"] in ["", None]: faltantes.append("Horas")
                                if row["Redução Minutos"] in ["", None]: faltantes.append("Minutos")
                                
                                if not faltantes:
                                        sugestao_valida = True
                                        sugestoes_limpas.append(row.to_dict())
                                else:
                                        pendencias.setdefault("Sugestões", []).append(f"Linha {i+1} incompleta: {', '.join(faltantes)}")

                if not sugestao_valida:
                        pendencias.setdefault("Sugestões", []).append("Preencha pelo menos uma linha completa de Sugestões.")

                # -------------------------------------------------
                # 7. DISC
                # -------------------------------------------------
                disc_faltando = []
                for i in range(1, 25):
                        if not st.session_state.get(f"disc_{i}"):
                                disc_faltando.append(f"Questão {i}")
                if disc_faltando:
                        pendencias["DISC"] = [", ".join(disc_faltando)]

                # -------------------------------------------------
                # RESULTADO DAS VALIDAÇÕES
                # -------------------------------------------------
                if pendencias:
                        st.error("⚠️ O formulário possui pendências. Confira abaixo:")
                        for secao, itens in pendencias.items():
                                st.write(f"**{secao}**:")
                                for item in itens:
                                        st.write(f"- {item}")
                        st.session_state["confirmado"] = False
                        st.stop()

                
                # -------------------------------------------------
                # CONFIRMAÇÃO EM DOIS CLIQUES
                # -------------------------------------------------
                if not st.session_state.get("confirmado", False):
                        st.warning("⚠️ Tudo certo! Revise suas respostas. O envio é único. Clique em ENVIAR novamente.")
                        st.session_state["confirmado"] = True
                        st.stop()

                # -------------------------------------------------
                # ENVIO FINAL (Salvar JSON)
                # -------------------------------------------------
                dados = {
                        "nome": nome,
                        "data_envio": datetime.now(ZoneInfo("America/Sao_Paulo")).strftime("%d/%m/%Y %H:%M"),
                        "setor": setor,
                        "cargo": cargo,
                        "chefe": chefe,
                        "departamento": departamento,
                        "empresa": empresa,
                        "escolaridade": escolaridade,
                        "devolucao": devolucao,
                        "cursos": cursos,
                        "objetivo": objetivo,
                        "atividades": atividades_limpas,
                        "dificuldades": dificuldades_limpas,
                        "sugestoes": sugestoes_limpas,
                        "disc": {f"disc_{i}": st.session_state.get(f"disc_{i}") for i in range(1, 25)}
                }

                caminho = os.path.join(dados_dir, f"{nome_limpo}.json")
                with open(caminho, "w", encoding="utf-8") as f:
                        json.dump(dados, f, ensure_ascii=False, indent=4)

                st.success("✅ Formulário enviado com sucesso!")
                st.session_state["confirmado"] = False


                


# --- VISUALIZAÇÃO ---
if st.session_state.get("pagina") == "visualizar":
    st.title("👁️ Visualização de Registros")
    
    # 1. Carrega os dados frescos do disco
    lista_de_arquivos = carregar_todos_formularios()
    
    # 2. Se a sua função carregar_todos_formularios() já retorna a lista, 
    # apenas certifique-se de que não estamos adicionando isso ao session_state de forma acumulativa.
    if not lista_de_arquivos:
        st.warning("⚠️ Nenhum formulário encontrado.")
    else:
        # Mostra o total para conferência
        st.success(f"Foram encontrados {len(lista_de_arquivos)} formulários.")
        
        # 3. Exibição limpa
        for idx, form in enumerate(lista_de_arquivos, 1):
            nome_exibir = str(form.get('nome', f'Colaborador {idx}')).upper()
            
           
            with st.expander(f"👤 FORMULÁRIO DE: {nome_exibir}", expanded=True):               
                
            
                            
                # 1. Cabeçalho Completo
                st.subheader("📝 Informações de Identificação")
                col1, col2 = st.columns(2)
                col1.write(f"**Data de Envio:** {form.get('data_envio', 'N/A')}")
                col2.write(f"**Devolver em:** {form.get('devolucao', 'N/A')}")
                
                col_a, col_b = st.columns(2)
                col_a.write(f"**Setor:** {form.get('setor', 'N/A')}")
                col_b.write(f"**Departamento:** {form.get('departamento', 'N/A')}")
                col_a.write(f"**Cargo:** {form.get('cargo', 'N/A')}")
                col_b.write(f"**Chefe Imediato:** {form.get('chefe', 'N/A')}")
                col_a.write(f"**Empresa/Unidade:** {form.get('empresa', 'N/A')}")
                col_b.write(f"**Escolaridade:** {form.get('escolaridade', 'N/A')}")
                
                st.subheader("🎓 Cursos Obrigatórios ou Diferenciais")

                st.info(
                    form.get("cursos", "Não informado")
                )

                st.subheader("🎯 Trabalho e Principal Objetivo")

                st.info(
                    form.get("objetivo", "Não informado")
                )
                
                # 2. Tabelas Dinâmicas
                secoes = {
                    "atividades": "📋 Atividades Executadas",
                    "dificuldades": "⚠️ Dificuldades e Bloqueios",
                    "sugestoes": "💡 Sugestões de Melhoria"
                }
                
                for chave, titulo in secoes.items():
                    st.markdown("---")
                    st.subheader(titulo)
                    if chave in form and form[chave]:
                        df = pd.DataFrame(form[chave])
                        df = df.replace("", None).dropna(how='all')
                        if not df.empty:
                            st.table(df)
                        else:
                            st.write("Nenhum dado preenchido nesta seção.")
                    else:
                        st.write("Seção não encontrada ou vazia.")
                
                # 3. Questionário DISC (Exibição Completa e Legível)
                st.markdown("---")
                st.subheader("📊 Avaliação DISC (Perguntas e Respostas)")
                
                for i, pergunta in enumerate(perguntas_disc, 1):
                    valor_resposta = form.get("disc", {}).get(f"disc_{i}", "Não respondido")
                    st.write(f"**{i}. {pergunta}**")
                    st.info(f"Resposta selecionada: **{valor_resposta}**")
                    st.markdown("---")

                                # -------------------------------------------------
                # EXPORTAÇÃO WORD + PDF (ESPELHO DO FORMULÁRIO)
                # -------------------------------------------------

                import io
                from docx import Document
                from reportlab.lib.pagesizes import A4
                from reportlab.pdfgen import canvas


                def gerar_word(form):

                    indent = " " * 16
                    doc = Document()

                    doc.add_heading("RELATÓRIO DO FORMULÁRIO DO COLABORADOR", level=1)

                    doc.add_heading("1. Dados de Identificação", level=2)

                    campos = [
                        ("Nome", "nome"),
                        ("Data de Envio", "data_envio"),
                        ("Setor", "setor"),
                        ("Cargo", "cargo"),
                        ("Chefe", "chefe"),
                        ("Departamento", "departamento"),
                        ("Empresa", "empresa"),
                        ("Escolaridade", "escolaridade"),
                        ("Devolver preenchido em", "devolucao")
                    ]

                    for titulo, chave in campos:
                        doc.add_paragraph(f"{indent}{titulo}: {form.get(chave,'')}")

                    doc.add_paragraph("")
                    doc.add_paragraph(f"{indent}Cursos:")
                    doc.add_paragraph(f"{indent}{form.get('cursos','')}")

                    doc.add_paragraph("")
                    doc.add_paragraph(f"{indent}Objetivo do Trabalho:")
                    doc.add_paragraph(f"{indent}{form.get('objetivo','')}")

                    doc.add_heading("2. Atividades Executadas", level=2)

                    table = doc.add_table(rows=1, cols=4)
                    headers = ["Atividade", "Frequência", "Horas", "Minutos"]

                    for i, h in enumerate(headers):
                        table.rows[0].cells[i].text = h

                    for ativ in form.get("atividades", []):
                        row = table.add_row().cells
                        row[0].text = str(ativ.get("Atividade Descrita",""))
                        row[1].text = str(ativ.get("Frequência",""))
                        row[2].text = str(ativ.get("Horas",""))
                        row[3].text = str(ativ.get("Minutos",""))

                    doc.add_heading("3. Dificuldades e Bloqueios", level=2)

                    table = doc.add_table(rows=1, cols=5)
                    headers = ["Dificuldade","Setor/Parceiro","Frequência","Horas Perdidas","Minutos Perdidos"]

                    for i,h in enumerate(headers):
                        table.rows[0].cells[i].text = h

                    for dif in form.get("dificuldades", []):
                        row = table.add_row().cells
                        row[0].text = str(dif.get("Dificuldade",""))
                        row[1].text = str(dif.get("Setor/Parceiro Envolvido",""))
                        row[2].text = str(dif.get("Frequência",""))
                        row[3].text = str(dif.get("Horas Perdidas",""))
                        row[4].text = str(dif.get("Minutos Perdidos",""))

                    doc.add_heading("4. Sugestões de Melhoria", level=2)

                    table = doc.add_table(rows=1, cols=5)
                    headers = ["Sugestão","Impacto Esperado","Redução Horas","Redução Minutos","Frequência Impacto"]

                    for i,h in enumerate(headers):
                        table.rows[0].cells[i].text = h

                    for sug in form.get("sugestoes", []):
                        row = table.add_row().cells
                        row[0].text = str(sug.get("Sugestão de Melhoria",""))
                        row[1].text = str(sug.get("Impacto Esperado",""))
                        row[2].text = str(sug.get("Redução Horas",""))
                        row[3].text = str(sug.get("Redução Minutos",""))
                        row[4].text = str(sug.get("Frequência do Impacto",""))

                    doc.add_heading("5. Questionário DISC", level=2)

                    for i, pergunta in enumerate(perguntas_disc, 1):
                        resp = form.get("disc", {}).get(f"disc_{i}", "")
                        doc.add_paragraph(f"{indent}{i}. {pergunta}")
                        doc.add_paragraph(f"{indent}Resposta: {resp}")

                    buffer = io.BytesIO()
                    doc.save(buffer)
                    buffer.seek(0)

                    return buffer


                def gerar_pdf(form):

                    indent = " " * 16
                    buffer = io.BytesIO()

                    c = canvas.Canvas(buffer, pagesize=A4)

                    largura, altura = A4
                    y = altura - 40

                    def linha(texto):

                        nonlocal y

                        largura_max = 95
                        palavras = texto.split(" ")

                        linha_atual = ""

                        for palavra in palavras:

                            if len(linha_atual + palavra) <= largura_max:
                                linha_atual += palavra + " "

                            else:
                                c.drawString(40, y, linha_atual)
                                y -= 18
                                linha_atual = palavra + " "

                                if y < 40:
                                    c.showPage()
                                    c.setFont("Helvetica",11)
                                    y = altura - 40

                        if linha_atual:
                            c.drawString(40, y, linha_atual)
                            y -= 18

                    c.setFont("Helvetica-Bold",16)
                    linha("RELATÓRIO DO FORMULÁRIO DO COLABORADOR")

                    c.setFont("Helvetica",11)
                    linha("")
                    linha("1. Dados de Identificação")

                    campos = [
                        ("Nome","nome"),
                        ("Data de Envio","data_envio"),
                        ("Setor","setor"),
                        ("Cargo","cargo"),
                        ("Chefe","chefe"),
                        ("Departamento","departamento"),
                        ("Empresa","empresa"),
                        ("Escolaridade","escolaridade")
                    ]

                    for titulo,chave in campos:
                        linha(f"{indent}{titulo}: {form.get(chave,'')}")

                    linha("")
                    linha(f"{indent}Cursos: {form.get('cursos','')}")
                    linha(f"{indent}Objetivo: {form.get('objetivo','')}")

                    linha("")
                    linha("2. Atividades Executadas")

                    for ativ in form.get("atividades", []):
                        linha(f"{indent}Atividade: {ativ.get('Atividade Descrita','')}")
                        linha(f"{indent}Frequência: {ativ.get('Frequência','')}")
                        linha(f"{indent}Tempo: {ativ.get('Horas','')} {ativ.get('Minutos','')}")
                        linha("")

                    linha("3. Dificuldades")

                    for dif in form.get("dificuldades", []):
                        linha(f"{indent}Dificuldade: {dif.get('Dificuldade','')}")
                        linha(f"{indent}Setor: {dif.get('Setor/Parceiro Envolvido','')}")
                        linha(f"{indent}Frequência: {dif.get('Frequência','')}")
                        linha("")

                    linha("4. Sugestões")

                    for sug in form.get("sugestoes", []):
                        linha(f"{indent}Sugestão: {sug.get('Sugestão de Melhoria','')}")
                        linha(f"{indent}Impacto: {sug.get('Impacto Esperado','')}")
                        linha("")

                    linha("5. Questionário DISC")

                    for i, pergunta in enumerate(perguntas_disc, 1):
                        resp = form.get("disc", {}).get(f"disc_{i}", "")
                        linha(f"{indent}{i}. {pergunta}")
                        linha(f"{indent}Resposta: {resp}")
                        linha("")

                    c.save()
                    buffer.seek(0)

                    return buffer


                # -------------------------------------------------
                # BOTÕES DE EXPORTAÇÃO
                # -------------------------------------------------

                if st.session_state.get("usuario_logado") == "Luciano 123":

                    st.markdown("---")
                    st.subheader("⚙️ Painel de Exportação")

                    col1, col2 = st.columns(2)

                    nome = form.get("nome", "Colaborador")
                    data = form.get("data_envio", "")

                    nome_clean = nome.replace(" ", "_")
                    data_clean = data.replace("/", "").replace(":", "").replace(" ", "_")

                    nome_arquivo = f"Relatorio_{nome_clean}_{data_clean}"

                    with col1:
                        st.download_button(
                            "📄 Baixar Word",
                            gerar_word(form),
                            file_name=f"{nome_arquivo}.docx",
                            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                        )

                    with col2:
                        st.download_button(
                            "📑 Baixar PDF",
                            gerar_pdf(form),
                            file_name=f"{nome_arquivo}.pdf",
                            mime="application/pdf"
                        )



        st.markdown("---")
        st.subheader("🗑️ Excluir formulário específico")

        # Lista os arquivos
        arquivos_json = [f for f in os.listdir(dados_dir) if f.endswith(".json")]

        if arquivos_json:

            # Criar lista com nome do colaborador
            opcoes = []

            for arquivo in arquivos_json:
                caminho = os.path.join(dados_dir, arquivo)

                with open(caminho, "r", encoding="utf-8") as f:
                    try:
                        dados = json.load(f)

                        if isinstance(dados, dict):
                            nome = dados.get("nome", "Colaborador")
                        else:
                            nome = "Registro inválido"

                    except:
                        nome = "Arquivo corrompido"

                opcoes.append((arquivo, nome))

            # Mostrar opções
            nomes_para_select = [f"{nome} ({arquivo})" for arquivo, nome in opcoes]

            escolha = st.selectbox(
                "Selecione o formulário que deseja excluir:",
                nomes_para_select
            )

            if st.button("❌ Excluir formulário selecionado"):

                arquivo_escolhido = opcoes[nomes_para_select.index(escolha)][0]

                os.remove(os.path.join(dados_dir, arquivo_escolhido))

                st.success("✅ Formulário excluído com sucesso!")
                st.rerun()

        else:
            st.info("Nenhum formulário salvo.")

# ============================================================
# CALCULAR CARGA HORÁRIA
# ============================================================

def calcular_carga(atividades):
    total_min = 0
    for at in atividades:
        try:
            tempo = float(at.get("tempo","0"))
        except:
            tempo = 0
        freq = at.get("frequencia","semanal").lower()
        if freq == "diaria":
            total_min += tempo * 5
        elif freq == "mensal":
            total_min += tempo / 4
        else:
            total_min += tempo
    horas = total_min / 60
    status = "Adequado"
    if horas > 44: status = "Sobrecarga"
    elif horas < 30: status = "Subutilização"
    return round(horas,2), status

# ============================================================
# GERAR ATIVIDADES IDEAIS (GPT)
# ============================================================

def gerar_atividades_ideais(cargo, setor, client=None):
    if client is None:
        return [{
            "nome_atividade": "Atividade de exemplo",
            "descricao": "Descrição de exemplo",
            "frequencia_ideal": "semanal",
            "tempo_medio_minutos": 60,
            "justificativa_tecnica": "Exemplo"
        }]
    
    prompt = f"""
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
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role":"user","content":prompt}],
            temperature=0.3
        )
        return json.loads(response.choices[0].message.content)
    except:
        return [{
            "nome_atividade": "Atividade de exemplo",
            "descricao": "Descrição de exemplo",
            "frequencia_ideal": "semanal",
            "tempo_medio_minutos": 60,
            "justificativa_tecnica": "Exemplo"
        }]

# ============================================================
# COMPARAÇÃO SEMÂNTICA
# ============================================================

def comparar_semanticamente(reais, ideais, client=None):
    if client is None:
        return {"score_aderencia":0,"tempo_gap_medio_percentual":0,"atividades_desvio":[]}

    prompt = f"""
    Compare semanticamente:
    Atividades reais: {reais}
    Atividades ideais: {ideais}
    Retorne JSON com:
      - score_aderencia (0-100)
      - tempo_gap_medio_percentual
      - atividades_desvio
    """
    try:
        r = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role":"user","content":prompt}],
            temperature=0.2
        )
        return json.loads(r.choices[0].message.content)
    except:
        return {"score_aderencia":0,"tempo_gap_medio_percentual":0,"atividades_desvio":[]}

# ============================================================
# CLASSIFICAR DIFICULDADES
# ============================================================

def classificar_dificuldades_gpt(dificuldades, client=None):
    if client is None:
        return {}
    
    prompt = f"""
    Classifique semanticamente as dificuldades abaixo em:
    - Processo
    - Tempo
    - Comunicação
    - Estrutura
    - Liderança
    - Sistema
    Retorne JSON com contagem por categoria.
    Dificuldades: {dificuldades}
    """
    try:
        r = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role":"user","content":prompt}],
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
    if status_carga == "Sobrecarga": fator_carga = 70
    elif status_carga == "Subutilização": fator_carga = 75
    return round(mean([score_aderencia, score_disc, fator_carga]),2)

# ============================================================
# MOTOR PRINCIPAL COMPLETO – ANÁLISE CORPORATIVA
# ============================================================

def gerar_analise_corporativa(dados, client=None):
    """
    Gera análise completa de um colaborador com base em:
    - Atividades reais
    - Perfil DISC
    - Dificuldades
    Retorna:
    - parecer (texto)
    - indicadores (dict)
    """
    # 1️⃣ Atividades ideais
    ideais = gerar_atividades_ideais(dados["cargo"], dados["setor"], client)

    # 2️⃣ Comparação semântica (reais x ideais)
    comparacao = comparar_semanticamente(dados["atividades"], ideais, client)

    # 3️⃣ Carga horária
    horas, status_carga = calcular_carga(dados["atividades"])

    # 4️⃣ Score DISC
    disc_score = score_disc(dados["disc"])

    # 5️⃣ Classificação de dificuldades
    dificuldades_classificadas = classificar_dificuldades_gpt(dados["dificuldades"], client)

    # 6️⃣ Score de aderência
    score_aderencia = comparacao.get("score_aderencia",0)

    # 7️⃣ Índice geral
    indice = indice_geral(score_aderencia, disc_score, status_carga)

    # 8️⃣ Classificação de risco
    risco = "Baixo" if indice < 60 else "Moderado" if indice < 75 else "Alto"

    # 9️⃣ Prompt final para parecer estratégico
    prompt_final = f"""
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
    """

    # 10️⃣ Obter parecer do GPT
    parecer = ""
    try:
        if client:
            resposta = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role":"user","content":prompt_final}],
                temperature=0.3
            )
            parecer = resposta.choices[0].message.content
        else:
            parecer = "GPT não disponível. Retorno padrão: análise resumida."
    except:
        parecer = "Erro ao gerar parecer com GPT."

    # 11️⃣ Indicadores
    indicadores = {
        "score_aderencia": score_aderencia,
        "horas_semanais": horas,
        "status_carga": status_carga,
        "score_disc": disc_score,
        "indice_geral": indice,
        "risco": risco
    }

    return parecer, indicadores

# ============================================================
# GERAR PDF DO PARECER
# ============================================================

def gerar_pdf(parecer, nome):
    """
    Recebe:
    - parecer (texto)
    - nome do colaborador
    Cria arquivo PDF pronto para download
    """
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib.units import inch

    nome_arquivo = f"{nome}_parecer.pdf"
    doc = SimpleDocTemplate(nome_arquivo)
    elements = []
    styles = getSampleStyleSheet()

    # Título
    elements.append(Paragraph("PARECER ESTRATÉGICO ORGANIZACIONAL", styles["Title"]))
    elements.append(Spacer(1, 0.5*inch))

    # Conteúdo linha a linha
    for linha in parecer.split("\n"):
        if linha.strip():  # evita parágrafos vazios
            elements.append(Paragraph(linha, styles["Normal"]))
            elements.append(Spacer(1, 0.2*inch))

    doc.build(elements)
    return nome_arquivo

# ============================================================
# PASTA BASE PARA FORMULÁRIOS (JSON)
# ============================================================
# Usamos 'dados_dir' para manter o padrão que já criamos
json_master = os.path.join(dados_dir, "formularios.json")

# Inicializa arquivo JSON se não existir
if not os.path.exists(json_master):
    with open(json_master, "w", encoding="utf-8") as f:
        json.dump([], f, ensure_ascii=False, indent=4)

# ============================================================
# FUNÇÃO PARA SALVAR FORMULÁRIO EM JSON E ENVIAR PARA GITHUB
# ============================================================
def salvar_formulario_json(formulario):
    """
    Recebe um dicionário do formulário preenchido, salva no arquivo 
    JSON único dentro da pasta 'dados', atualiza a sessão e envia para GitHub.
    """
    # 1. Tenta carregar os dados existentes ou cria uma lista vazia
    try:
        with open(json_master, "r", encoding="utf-8") as f:
            dados_existentes = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        dados_existentes = []

    # 2. Adiciona o novo formulário à lista
    dados_existentes.append(formulario)

    # 3. Salva a lista completa de volta no arquivo local (container efêmero)
    with open(json_master, "w", encoding="utf-8") as f:
        json.dump(dados_existentes, f, ensure_ascii=False, indent=4)

    # 4. Atualiza o estado da sessão do Streamlit
    st.session_state["formularios"] = dados_existentes

    # 5. Envio automático para GitHub para persistência permanente
    import subprocess

    repo_url = "https://<TOKEN>@github.com/SeuUsuario/analise_formularios.git"  # substitua <TOKEN>
    try:
        if not os.path.exists(os.path.join(dados_dir, ".git")):
            subprocess.run(["git", "init"], cwd=dados_dir, check=True)
            subprocess.run(["git", "remote", "add", "origin", repo_url], cwd=dados_dir, check=True)

        subprocess.run(["git", "add", json_master], cwd=dados_dir, check=True)
        subprocess.run(["git", "commit", "-m", f"Formulário de {formulario['nome']}"], cwd=dados_dir, check=True)
        subprocess.run(["git", "push", "-u", "origin", "main"], cwd=dados_dir, check=True)
    except subprocess.CalledProcessError as e:
        st.warning(f"Não foi possível enviar para o GitHub automaticamente: {e}")