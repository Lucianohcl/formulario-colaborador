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
import plotly.express as px
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

# DEFINE O DIRETÓRIO (Isso resolve o problema da função não achar os arquivos)
dados_dir = "dados"
if not os.path.exists(dados_dir):
    os.makedirs(dados_dir)


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
# PÁGINA PERFIL DISC (VERSÃO SINCRO)
# ============================================================

if st.session_state.pagina == "disc":
    import plotly.express as px
    import pandas as pd

    st.title("🧠 Análise de Perfil DISC")

    # 1. FORÇAR LEITURA DIRETA (IGUAL AO VISUALIZAR REGISTROS)
    # Isso garante que não dependemos de um session_state que pode estar vazio
    lista_fresca = carregar_todos_formularios()

    if not lista_fresca:
        st.warning("Nenhum formulário encontrado na pasta de dados.")
        if st.button("♻️ Tentar recarregar dados"):
            st.rerun()
        st.stop()

    # 2. MAPEAMENTO SEGURO
    opcoes_colaboradores = {
        f"{f.get('nome', 'Sem Nome')} - {f.get('cargo', 'Sem Cargo')}": f 
        for f in lista_fresca
    }

    colaborador_chave = st.selectbox(
        "Escolha o colaborador",
        options=list(opcoes_colaboradores.keys())
    )

    # 3. RECUPERAÇÃO DO FORMULÁRIO
    formulario_sel = opcoes_colaboradores.get(colaborador_chave)

    # ============================================================
    # BOTÃO GERAR ANÁLISE
    # ============================================================

    if formulario_sel and st.button("🔎 Gerar análise DISC"):
        # A partir daqui o seu processamento continua normal
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

        # ============================================================
        # PAINEL DISC DO COLABORADOR (AJUSTADO)
        # ============================================================

        # 1️⃣ Função ajustada de cálculo de score
        def score_disc(percentuais):
            """
            Calcula a intensidade do perfil dominante considerando a diferença
            entre ele e o segundo maior perfil.
            Retorna um valor de 0 a 100, refletindo a certeza relativa.
            """
            if not percentuais:
                return 0
            
            valores = sorted(percentuais.values(), reverse=True)
            dominante_val = valores[0]
            segundo_val = valores[1] if len(valores) > 1 else 0
            
            diff = dominante_val - segundo_val
            score_normalizado = round((diff / dominante_val) * 100, 1) if dominante_val > 0 else 0
            score_normalizado = max(0, min(score_normalizado, 100))
            
            return score_normalizado

        # 2️⃣ Cálculos
        percentuais, dominante = calcular_disc(respostas_disc)
        score = score_disc(percentuais)

        st.markdown("## 🔹 Painel DISC do Colaborador")

        # 3️⃣ Gráfico e Métricas lado a lado
        col_graf, col_met = st.columns([2,1])

        with col_graf:
            fig = px.bar(
                x=list(percentuais.keys()),
                y=list(percentuais.values()),
                labels={'x':'Tipo','y':'Percentual (%)'},
                text=list(percentuais.values()),
                color=list(percentuais.keys()),
                color_discrete_map={"D":"#FF4136","I":"#FF851B","S":"#2ECC40","C":"#0074D9"}
            )
            fig.update_layout(
                yaxis_range=[0,100], 
                height=350, 
                margin=dict(l=20, r=20, t=30, b=20), 
                template="plotly_white",
                showlegend=False
            )
            st.plotly_chart(fig, use_container_width=True)

        with col_met:
            st.metric("Perfil Dominante", dominante)
            st.metric("Intensidade (Score)", f"{score}%")
            
            # Interpretação rápida do nível de intensidade
            def interpretar_valor(p):
                try:
                    v = float(str(p).replace('%',''))
                    if v > 85: return "🎯 **Muito Alta**"
                    if v > 60: return "✅ **Alta**"
                    if v > 30: return "⚖️ **Moderada**"
                    return "⚠️ **Baixa**"
                except:
                    return ""
            
            st.write(interpretar_valor(score))

            st.caption("ℹ️ Score indica a intensidade relativa do perfil dominante em relação aos outros perfis. Quanto maior a diferença, maior a certeza do perfil.")


            st.markdown("---")

            

        # 2. INTERPRETAÇÃO DETALHADA (Substitui a Base de Conhecimento e o Parecer)
        textos_disc = {
            "D": {"nome": "Dominante", "estilo": "Resultados e Assertividade", "desc": "Decidido e direto. Busca desafios e rapidez.", "cor": "red", "tarefas": "Tomada de decisão, Gestão de crises, Metas."},
            "I": {"nome": "Influente", "estilo": "Pessoas e Comunicação", "desc": "Entusiasmado e otimista. Busca conexão social.", "cor": "orange", "tarefas": "Apresentações, Networking, Motivação."},
            "S": {"nome": "Estável", "estilo": "Colaboração e Persistência", "desc": "Paciente e leal. Busca harmonia e segurança.", "cor": "green", "tarefas": "Apoio operacional, Suporte, Processos."},
            "C": {"nome": "Conformidade", "estilo": "Precisão e Qualidade", "desc": "Analítico e detalhista. Busca lógica e regras.", "cor": "blue", "tarefas": "Auditoria, Análise de dados, Padronização."}
        }

        info = textos_disc.get(dominante, {"nome": "N/A", "estilo": "", "desc": "", "cor": "gray", "tarefas": ""})

        st.markdown(f"### Análise do Perfil: :{info['cor']}[{info['nome']}]")
        st.write(f"**Foco Principal:** {info['estilo']}")
        
        col_desc, col_tar = st.columns(2)
        with col_desc:
            st.info(info['desc'])
        with col_tar:
            st.warning(f"**Tarefas Sugeridas:**\n{info['tarefas']}")

        # 3. LEGENDA DETALHADA (Final da página)
        with st.expander("🔍 Legenda Geral DISC - Detalhada", expanded=False):
            textos_disc = {
                "D": {
                    "nome": "Dominante",
                    "estilo": "Resultados e Assertividade",
                    "desc": "Decidido e direto. Busca desafios, rapidez e liderança.",
                    "cargos": "Gerente, Líder de Projeto, Coordenador",
                    "tarefas_mais": "Tomada de decisão, Gestão de crises, Definir metas",
                    "tarefas_menos": "Atendimento de rotina, Processos detalhados, Documentação"
                },
                "I": {
                    "nome": "Influente",
                    "estilo": "Pessoas e Comunicação",
                    "desc": "Entusiasmado, sociável e persuasivo. Busca conexão e motivação do grupo.",
                    "cargos": "Marketing, Vendas, Comunicação, Treinamento",
                    "tarefas_mais": "Apresentações, Networking, Reuniões de equipe, Motivação",
                    "tarefas_menos": "Tarefas repetitivas, Processos rígidos, Detalhes técnicos"
                },
                "S": {
                    "nome": "Estável",
                    "estilo": "Colaboração e Persistência",
                    "desc": "Paciente, leal e confiável. Busca harmonia e segurança.",
                    "cargos": "Suporte, Administrativo, RH, Atendimento ao Cliente",
                    "tarefas_mais": "Suporte operacional, Atendimento, Organizar processos",
                    "tarefas_menos": "Mudanças constantes, Pressão por resultados rápidos, Competição intensa"
                },
                "C": {
                    "nome": "Conformidade",
                    "estilo": "Precisão e Qualidade",
                    "desc": "Analítico, detalhista e criterioso. Busca lógica, regras e perfeição.",
                    "cargos": "Auditoria, Contabilidade, TI, Qualidade",
                    "tarefas_mais": "Análise de dados, Relatórios, Controle de qualidade, Padronização",
                    "tarefas_menos": "Decisões rápidas sem dados, Interações sociais constantes, Ambiguidade"
                }
            }

            for key, info in textos_disc.items():
                st.markdown(f"### **{key} - {info['nome']}**")
                st.write(f"**Estilo de trabalho:** {info['estilo']}")
                st.write(f"**Descrição:** {info['desc']}")
                st.write(f"**Cargos mais compatíveis:** {info['cargos']}")
                st.write(f"**Atividades que combinam mais:** {info['tarefas_mais']}")
                st.write(f"**Atividades que combinam menos:** {info['tarefas_menos']}")
                st.markdown("---")

        
                
        # ============================================================
        # COMPATIBILIDADE CARGO × PERFIL DISC (APENAS MENSAGEM)
        # ============================================================

        st.markdown("### 🔹 Compatibilidade Cargo × Perfil DISC")

        cargo_atual = str(form.get("cargo", "")).lower()

        # Mapeamento de cargos por perfil dominante
        compatibilidade = {
            "D": ["gerente", "diretor", "coordenador", "lider", "gestor"],
            "I": ["vendas", "marketing", "comercial", "relacionamento", "comunicação"],
            "S": ["rh", "suporte", "atendimento", "administrativo", "operacional"],
            "C": ["contabilidade", "qualidade", "auditoria", "financeiro", "ti", "analista"]
        }

        cargos_compatíveis = compatibilidade.get(dominante, [])
        match = any(c in cargo_atual for c in cargos_compatíveis)

        # Exibição simplificada em métricas
        colA, colB = st.columns(2)
        colA.metric("Cargo Atual", form.get("cargo","N/A").title())
        colB.metric("Perfil Dominante", dominante if dominante else "N/A")

        # Mensagem direta sem gráfico
        if match:
            st.success(f"**Alta aderência:** O perfil **{dominante}** possui características naturais que favorecem o desempenho em cargos de **{cargo_atual.title()}**.")
        else:
            st.warning(f"**Ponto de Atenção:** O perfil **{dominante}** pode exigir um esforço maior de adaptação para as rotinas típicas de **{cargo_atual.title()}**.")

        # ============================================================
        # PERFIL DISC EXIGIDO PELAS ATIVIDADES
        # ============================================================

        st.markdown("### 🔹 Perfil DISC Exigido pelas Atividades")

        atividades_lista = [
            a.get("Atividade Descrita","")
            for a in form.get("atividades",[])
        ]

        atividades_texto = " ".join(atividades_lista).lower()

        compatibilidade_ativ = {

            "D": [
                "decisão","meta","resultado","liderar","negociar",
                "estratégia","direcionar","definir","priorizar"
            ],

            "I": [
                "apresentar","convencer","comunicar","clientes",
                "reunião","relacionamento","treinamento"
            ],

            "S": [
                "suporte","atender","organizar","rotina",
                "apoio","assistir","acompanhar","colaborar"
            ],

            "C": [
                "analisar","dados","relatório","planilha",
                "controle","auditar","conferir","classificar",
                "registrar","custos","informações","base",
                "indicadores","verificar","validar"
            ]

        }

        scores = {}

        for perfil, palavras in compatibilidade_ativ.items():

            pontos = sum(
                atividades_texto.count(p) for p in palavras
            )

            scores[perfil] = pontos

        perfil_exigido = max(scores, key=scores.get)

        # ============================================================
        # MÉTRICAS
        # ============================================================

        colA, colB, colC = st.columns(3)

        colA.metric("Perfil do Colaborador", dominante if dominante else "N/A")
        colB.metric("Perfil Exigido pelas Atividades", perfil_exigido)

        total_pontos = sum(scores.values())

        if total_pontos > 0:
            compat_percent = int((scores.get(dominante,0) / total_pontos) * 100)
        else:
            compat_percent = 0

        colC.metric("Compatibilidade", f"{compat_percent}%")

        # ============================================================
        # MENSAGEM PRINCIPAL
        # ============================================================

        if perfil_exigido == dominante:

            st.success(
                f"Alta aderência: As atividades indicam um perfil **{perfil_exigido}**, compatível com o perfil do colaborador."
            )

        else:

            st.warning(
                f"As atividades indicam um perfil **{perfil_exigido}**, enquanto o colaborador apresenta perfil **{dominante}**."
            )

        # ============================================================
        # ATIVIDADES QUE EXIGEM ADAPTAÇÃO
        # ============================================================

        atividades_compativeis = compatibilidade_ativ.get(perfil_exigido, [])

        atividades_desvio = []

        for ativ in atividades_lista:

            texto = str(ativ).lower()

            if not any(p in texto for p in atividades_compativeis):
                atividades_desvio.append(ativ)


        ranking_atividades = []

        for ativ in atividades_lista:

            texto = str(ativ).lower()

            if not texto.strip():
                continue

            score = sum(p in texto for p in compatibilidade_ativ.get(dominante, []))

            ranking_atividades.append((score, ativ))


        ranking_atividades.sort(key=lambda x: x[0])


        if ranking_atividades:

            st.markdown("#### ⚠ Lista das principais dificuldades de adaptação")

            limite = min(3, len(ranking_atividades))

            for score, atividade in ranking_atividades[:limite]:
                st.write("•", atividade)


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
import requests
import base64
import json

GITHUB_USER = st.secrets["DB_USERNAME"]
GITHUB_TOKEN = st.secrets["DB_TOKEN"]
REPO = f"{GITHUB_USER}/analise_formularios"
ARQUIVO = "dados/formularios.json"


def salvar_formulario_json(formulario):
    url = f"https://api.github.com/repos/{REPO}/contents/{ARQUIVO}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}

    # 1. Carregar dados existentes
    r = requests.get(url, headers=headers)
    if r.status_code == 200:
        conteudo = r.json()
        sha = conteudo["sha"]
        dados = json.loads(base64.b64decode(conteudo["content"]).decode())
    else:
        sha = None
        dados = []

    # 2. Adicionar formulário
    dados.append(formulario)

    # 3. Converter para base64
    novo_conteudo = base64.b64encode(
        json.dumps(dados, ensure_ascii=False, indent=4).encode()
    ).decode()

    payload = {
        "message": f"Novo formulário {formulario.get('nome','SemNome')}",
        "content": novo_conteudo,
        "branch": "main"
    }

    if sha:
        payload["sha"] = sha

    # 4. Enviar para GitHub
    r_put = requests.put(url, headers=headers, json=payload)
    if r_put.status_code not in [200, 201]:
        st.warning(f"Erro ao enviar para GitHub: {r_put.status_code} {r_put.text}")

    # 5. Atualizar sessão
    st.session_state["formularios"] = dados

    # ============================================================
    # GARANTIA DE PERSISTÊNCIA (CARGA DOS DADOS)
    # ============================================================

    # Recarregamos os dados diretamente do disco/nuvem para garantir persistência total
    st.session_state["formularios"] = carregar_todos_formularios()

import streamlit as st
import pandas as pd
import plotly.express as px

# ============================================================
# 1. FUNÇÕES DE APOIO (CÁLCULOS E TRADUÇÃO)
# ============================================================

MAPA_DISC = {
    "A": "D", "B": "I", "C": "S", "D": "C"
}

def calcular_disc(respostas_disc):
    """Traduz A, B, C, D para D, I, S, C e calcula percentuais."""
    contagem = {"D": 0, "I": 0, "S": 0, "C": 0}
    for r in respostas_disc.values():
        perfil = MAPA_DISC.get(r)
        if perfil in contagem:
            contagem[perfil] += 1
    
    total = sum(contagem.values())
    if total > 0:
        percentuais = {k: round(v/total*100, 1) for k, v in contagem.items()}
        dominante = max(percentuais, key=percentuais.get)
    else:
        percentuais = {"D": 0, "I": 0, "S": 0, "C": 0}
        dominante = None
    return percentuais, dominante

# ============================================================
# 2. CARREGAMENTO E PERSISTÊNCIA
# ============================================================

# Garante que os dados estejam carregados na sessão
formularios = carregar_todos_formularios()
st.session_state["formularios"] = formularios

# ============================================================
# 3. PANORAMA COLETIVO (DENTRO DO EXPANDER)
# ============================================================

# ✅ Executa SÓ se o usuário clicou no menu "Perfil DISC"
if st.session_state.get("pagina") == "disc":  

    if formularios:
        # O 'expanded=False' garante que ele comece FECHADO
        with st.expander("📊 Ver Panorama Coletivo da Equipe", expanded=False):
            st.markdown("## 👥 Gestão Coletiva: Panorama da Equipe")
            
            lista_resultados = []
            atividades_coletivas = []

            # Processamento de todos os formulários carregados
            for f in formularios:
                res_percentual, _ = calcular_disc(f.get("disc", {}))
                lista_resultados.append(res_percentual)

                for a in f.get("atividades", []):
                    desc = a.get("Atividade Descrita", "").strip()
                    if desc:
                        atividades_coletivas.append(desc)

            if lista_resultados:
                # Criando DataFrame com a média de todos os perfis
                df_equipe = pd.DataFrame(lista_resultados).apply(pd.to_numeric, errors='coerce')
                medias = df_equipe.mean()
                
                # VARIÁVEIS DO GRUPO (A média real)
                dominante_grupo = medias.idxmax()
                menor_grupo = medias.idxmin()

                # --- Layout de Colunas ---
                col_txt, col_grf = st.columns([1, 1.5])
                
                with col_txt:
                    st.write("### 🧠 Insight do Grupo")
                    explicacoes = {
                        "D": "🔥 **Dominância:** Foco em metas e execução rápida.",
                        "I": "☀️ **Influência:** Comunicação e criatividade em alta.",
                        "S": "🌱 **Estabilidade:** Time leal, processual e resiliente.",
                        "C": "💎 **Conformidade:** Alta precisão técnica e perfeccionismo."
                    }
                    
                    st.info(f"**Perfil Dominante do Time:** {dominante_grupo}\n\n{explicacoes.get(dominante_grupo)}")
                    st.warning(f"**Menor Presença no Time:** {menor_grupo}")
                    st.caption(f"Análise baseada em {len(formularios)} formulários sincronizados.")

                with col_grf:
                    # Gráfico baseado nos dados agrupados
                    dados_plot = medias.reset_index()
                    dados_plot.columns = ["Tipo", "Media"]
                    
                    fig_eq = px.bar(
                        dados_plot, x="Tipo", y="Media", color="Tipo",
                        text_auto='.1f',
                        color_discrete_map={"D":"#FF4136", "I":"#FF851B", "S":"#2ECC40", "C":"#0074D9"}
                    )
                    fig_eq.update_layout(
                        template="plotly_white", height=280, showlegend=False,
                        yaxis_range=[0, 100], margin=dict(l=10, r=10, t=10, b=10)
                    )
                    st.plotly_chart(fig_eq, use_container_width=True)

                # --- Dificuldades de Adaptação ---
                st.divider()
                st.markdown(f"#### ⚠ Principais desafios de adaptação para o perfil {dominante_grupo}")
                
                # Lógica de ranking: Atividades menos compatíveis com o dominante do grupo
                compatibilidade_ativ = {
                    "D": ["decisão","meta","resultado","liderar","estratégia"],
                    "I": ["apresentar","comunicar","clientes","reunião"],
                    "S": ["suporte","atender","organizar","rotina","apoio"],
                    "C": ["analisar","dados","relatório","planilha","controle"]
                }

                ranking = []
                for ativ in atividades_coletivas:
                    texto = ativ.lower()
                    score = sum(p in texto for p in compatibilidade_ativ.get(dominante_grupo, []))
                    ranking.append((score, ativ))
                
                # Ordena pelo menor score (maior necessidade de adaptação)
                ranking.sort(key=lambda x: x[0])
                
                if ranking:
                    for _, atividade in ranking[:3]:
                        st.write(f"• {atividade}")
                else:
                    st.write("Nenhuma atividade descrita para análise.")

    else:
        st.info("Carregue formulários para habilitar o Panorama Coletivo.")



import streamlit as st
import pandas as pd
import json
import base64
import requests

# ================================
# CONFIG GITHUB
# ================================
USER = st.secrets["DB_USERNAME"]
TOKEN = st.secrets["DB_TOKEN"]
REPO = f"{USER}/analise_formularios"

# ================================
# LISTAS
# ================================
lista_frequencia = ["Diário","Semanal","Mensal","Esporádico"]
lista_horas = [str(i) for i in range(0,13)]
lista_minutos = [str(i) for i in range(0,60,5)]

# ================================
# PERGUNTAS DISC
# ================================
perguntas_disc = [
"Quando surge um problema inesperado: (A) Age rápido | (B) Comunica a todos | (C) Analisa riscos | (D) Segue processo",
"Em situações de pressão: (A) Foca no resultado | (B) Mantém o otimismo | (C) Mantém a calma | (D) Busca precisão",
"Ao receber tarefa difícil: (A) Aceita o desafio | (B) Busca ajuda social | (C) Planeja passos | (D) Estuda as regras",
"No trabalho em equipe: (A) Lidera o grupo | (B) Motiva os colegas | (C) Apoia os outros | (D) Organiza as tarefas",
"Em reuniões: (A) Vai direto ao ponto | (B) Interage e brinca | (C) Escuta mais | (D) Anota detalhes",
"Seu ritmo de trabalho: (A) Rápido/Impaciente | (B) Rápido/Entusiasmado | (C) Calmo/Constante | (D) Metódico/Cauteloso",
"Prefere tarefas: (A) Desafiadoras | (B) Variadas e sociais | (C) Rotineiras e seguras | (D) Técnicas e detalhadas",
"Seu foco principal: (A) Resultados | (B) Relacionamentos | (C) Estabilidade | (D) Qualidade e Processos",
"Seu ponto forte: (A) Coragem | (B) Comunicação | (C) Paciência | (D) Organização",
"Você se considera: (A) Dominante | (B) Influente | (C) Estável | (D) Conforme/Analítico",
"Se motiva por: (A) Poder/Bônus | (B) Reconhecimento | (C) Segurança/Paz | (D) Conhecimento Técnico",
"Ambiente ideal: (A) Competitivo | (B) Amigável | (C) Previsível | (D) Disciplinado"
]

# ================================
# FUNÇÕES GITHUB
# ================================
def carregar(arquivo):

    url = f"https://api.github.com/repos/{REPO}/contents/{arquivo}"
    headers = {"Authorization": f"token {TOKEN}"}

    r = requests.get(url, headers=headers)

    if r.status_code == 200:
        data = r.json()
        conteudo = base64.b64decode(data["content"]).decode()
        return json.loads(conteudo), data["sha"]

    return {}, None


def salvar(dados, arquivo, sha=None):

    url = f"https://api.github.com/repos/{REPO}/contents/{arquivo}"
    headers = {"Authorization": f"token {TOKEN}"}

    conteudo = base64.b64encode(
        json.dumps(dados, indent=4).encode()
    ).decode()

    payload = {
        "message": "Salvar rascunho do formulário",
        "content": conteudo
    }

    if sha:
        payload["sha"] = sha

    requests.put(url, headers=headers, json=payload)


# ================================
# INTERFACE
# ================================
st.title("📋 Rascunho da Análise")

if "acesso_rascunho" not in st.session_state:
    st.session_state.acesso_rascunho = False

if st.button("📝 Iniciar ou Continuar Rascunho"):
    st.session_state.acesso_rascunho = True


if st.session_state.acesso_rascunho:

    usuario = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")

    if usuario and senha:

        arquivo = f"rascunho_{usuario.lower()}_{senha}.json"

        dados, sha = carregar(arquivo)

        # ================================
        # DADOS DE IDENTIFICAÇÃO
        # ================================
        st.subheader("👤 Dados de Identificação")

        col1, col2 = st.columns(2)

        with col1:
            nome = st.text_input("Nome do colaborador", dados.get("nome",""))
            cargo = st.text_input("Cargo", dados.get("cargo",""))
            departamento = st.text_input("Departamento", dados.get("departamento",""))
            escolaridade = st.text_input("Escolaridade", dados.get("escolaridade",""))

        with col2:
            setor = st.text_input("Setor", dados.get("setor",""))
            chefe = st.text_input("Chefe imediato", dados.get("chefe",""))
            empresa = st.text_input("Empresa / Unidade", dados.get("empresa",""))
            devolucao = st.text_input("Devolver preenchido em", dados.get("devolucao",""))

        cursos = st.text_area("Cursos obrigatórios ou diferenciais", dados.get("cursos",""))
        objetivo = st.text_area("Trabalho e principal objetivo", dados.get("objetivo",""))

        # ================================
        # ATIVIDADES
        # ================================
        st.markdown("---")
        st.subheader("🔹 Atividades")

        df_ativ = pd.DataFrame(
            dados.get(
                "atividades",
                [{"Atividade":"","Frequência":"","Horas":"","Minutos":""} for _ in range(20)]
            )
        )

        edit_ativ = st.data_editor(
            df_ativ,
            column_config={
                "Frequência": st.column_config.SelectboxColumn(options=lista_frequencia),
                "Horas": st.column_config.SelectboxColumn(options=lista_horas),
                "Minutos": st.column_config.SelectboxColumn(options=lista_minutos),
            },
            hide_index=True,
            num_rows="fixed",
            use_container_width=True,
            key="rascunho_editor_atividades"
        )

        # ================================
        # DIFICULDADES
        # ================================
        st.markdown("---")
        st.subheader("⚠️ Dificuldades")

        df_dif = pd.DataFrame(
            dados.get(
                "dificuldades",
                [{"Dificuldade":"","Setor":"","Frequência":"","Horas Perdidas":"","Minutos Perdidos":""} for _ in range(20)]
            )
        )

        edit_dif = st.data_editor(
            df_dif,
            column_config={
                "Frequência": st.column_config.SelectboxColumn(options=lista_frequencia),
                "Horas Perdidas": st.column_config.SelectboxColumn(options=lista_horas),
                "Minutos Perdidos": st.column_config.SelectboxColumn(options=lista_minutos),
            },
            hide_index=True,
            num_rows="fixed",
            use_container_width=True,
            key="rascunho_editor_dificuldades"
        )

        # ================================
        # SUGESTÕES
        # ================================
        st.markdown("---")
        st.subheader("💡 Sugestões")

        df_sug = pd.DataFrame(
            dados.get(
                "sugestoes",
                [{"Sugestão":"","Impacto":"","Redução Horas":"","Redução Minutos":"","Frequência Impacto":""} for _ in range(20)]
            )
        )

        edit_sug = st.data_editor(
            df_sug,
            column_config={
                "Redução Horas": st.column_config.SelectboxColumn(options=lista_horas),
                "Redução Minutos": st.column_config.SelectboxColumn(options=lista_minutos),
                "Frequência Impacto": st.column_config.SelectboxColumn(options=lista_frequencia),
            },
            hide_index=True,
            num_rows="fixed",
            use_container_width=True,
            key="rascunho_editor_sugestoes"
        )

        # ================================
        # DISC
        # ================================
        st.markdown("---")
        st.subheader("🧠 Questionário DISC")

        respostas = {}

        for i, pergunta in enumerate(perguntas_disc, 1):

            valor = dados.get(f"disc_{i}")

            respostas[f"disc_{i}"] = st.radio(
                f"{i}. {pergunta}",
                ["A","B","C","D"],
                horizontal=True,
                key=f"rascunho_disc_{i}",
                index=["A","B","C","D"].index(valor) if valor else None
            )

        # ================================
        # SALVAR
        # ================================
        if st.button("💾 Salvar Rascunho"):

            payload = {
                "nome": nome,
                "setor": setor,
                "cargo": cargo,
                "chefe": chefe,
                "departamento": departamento,
                "empresa": empresa,
                "escolaridade": escolaridade,
                "devolucao": devolucao,
                "cursos": cursos,
                "objetivo": objetivo,
                "atividades": edit_ativ.to_dict("records"),
                "dificuldades": edit_dif.to_dict("records"),
                "sugestoes": edit_sug.to_dict("records"),
                **respostas
            }

            salvar(payload, arquivo, sha)

            st.success("Rascunho salvo no GitHub!")



