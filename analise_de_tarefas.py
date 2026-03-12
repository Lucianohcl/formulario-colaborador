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

from docx import Document
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
import io

def gerar_word(form):
    doc = Document()
    doc.add_heading(f"Relatório: {form.get('nome', 'Colaborador')}", 0)
    doc.add_paragraph(f"Data de Envio: {form.get('data_envio', 'N/A')}")
    
    # Identificação
    doc.add_heading("Informações de Identificação", level=1)
    campos = ['setor', 'departamento', 'cargo', 'chefe', 'empresa', 'escolaridade', 
              'cursos_obrigatorios_ou_diferenciais', 'trabalho_e_principal_objetivo']
    for c in campos:
        label = c.replace('_', ' ').capitalize()
        doc.add_paragraph(f"{label}: {form.get(c, 'N/A')}")

    # Tabelas
    secoes = {
        "atividades": ["Atividade Descrita", "Frequência", "Horas", "Minutos"],
        "dificuldades": ["Dificuldade", "Setor/Parceiro Envolvido", "Horas Perdidas", "Minutos Perdidos", "Frequência"],
        "sugestoes": ["Sugestão de Melhoria", "Impacto Esperado"]
    }
    
    for chave, cols in secoes.items():
        doc.add_heading(f"📋 {chave.capitalize()}", level=1)
        dados = form.get(chave, [])
        if isinstance(dados, list) and dados:
            table = doc.add_table(rows=1, cols=len(cols))
            table.style = 'Table Grid'
            for i, col in enumerate(cols): 
                table.rows[0].cells[i].text = col
            
            for item in dados:
                row_cells = table.add_row().cells
                for i, col in enumerate(cols):
                    # --- AQUI ESTÁ A CORREÇÃO ---
                    if isinstance(item, dict):
                        valor = str(item.get(col, ''))
                    else:
                        # Se o item for uma string pura, coloca na primeira coluna e limpa as outras
                        valor = str(item) if i == 0 else ""
                    row_cells[i].text = valor
        else:
            doc.add_paragraph("Sem dados.")

    # DISC
    doc.add_heading("Avaliação DISC", level=1)
    disc_data = form.get('disc', {})
    if isinstance(disc_data, dict) and disc_data:
        for i, pergunta in enumerate(perguntas_disc, 1):
            res = disc_data.get(f"disc_{i}", "N/A")
            doc.add_paragraph(f"{i}. {pergunta}: {res}")

    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

def gerar_pdf(form):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    elementos = []

    elementos.append(Paragraph(f"Relatório: {form.get('nome', 'Colaborador')}", styles['Title']))
    elementos.append(Paragraph(f"Data: {form.get('data_envio', 'N/A')}", styles['Normal']))
    elementos.append(Spacer(1, 12))

    # Tabelas Dinâmicas
    secoes = {
        "atividades": ["Atividade Descrita", "Frequência", "Horas", "Minutos"],
        "dificuldades": ["Dificuldade", "Setor/Parceiro Envolvido", "Frequência"]
    }
    
    for chave, colunas in secoes.items():
        elementos.append(Paragraph(chave.capitalize(), styles['Heading2']))
        dados = form.get(chave, [])
        if dados:
            data = [colunas]
            for item in dados:
                # CORREÇÃO AQUI: Verifica se é dicionário antes de usar .get()
                if isinstance(item, dict):
                    data.append([str(item.get(c, '')) for c in colunas])
                else:
                    # Se for apenas uma string, coloca na primeira coluna e limpa o resto
                    data.append([str(item)] + [""] * (len(colunas) - 1))
            
            t = Table(data, repeatRows=1)
            t.setStyle(TableStyle([
                ('BACKGROUND',(0,0),(-1,0),colors.lightgrey),
                ('GRID',(0,0),(-1,-1),0.5,colors.black),
                ('FONTSIZE', (0,0), (-1,-1), 10)
            ]))
            elementos.append(t)
        else:
            elementos.append(Paragraph("Sem dados registrados.", styles['Normal']))
        elementos.append(Spacer(1, 12))

    # DISC no PDF
    elementos.append(Paragraph("Avaliação DISC", styles['Heading2']))
    disc_data = form.get('disc', {})
    if isinstance(disc_data, dict):
        for i, pergunta in enumerate(perguntas_disc, 1):
            res = disc_data.get(f"disc_{i}", "N/A")
            elementos.append(Paragraph(f"<b>{i}.</b> {res}", styles['Normal']))
    else:
        elementos.append(Paragraph("Dados DISC não encontrados.", styles['Normal']))

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
    lista_horas = [f"{i} h" for i in range(25)]
    lista_minutos = [f"{i} min" for i in range(0, 60, 5)]
    lista_frequencia = ["DVD", "D", "S", "Q", "M", "T", "A"]

    st.title("📋 Formulário Completo do Colaborador")
    
    # Movendo as tabelas para FORA do form para garantir que os dados fiquem salvos
    # --- SEÇÃO: ATIVIDADES ---
    st.subheader("🔹 Atividades Executadas")
    if 'df_atividades' not in st.session_state:
        st.session_state.df_atividades = pd.DataFrame({"Atividade Descrita": [""] * 20, "Frequência": [""] * 20, "Horas": [""] * 20, "Minutos": [""] * 20, "Origem": [""] * 20})
    
    st.session_state.df_atividades = st.data_editor(st.session_state.df_atividades, column_config={
        "Frequência": st.column_config.SelectboxColumn("Frequência", options=lista_frequencia),
        "Horas": st.column_config.SelectboxColumn("Horas", options=lista_horas),
        "Minutos": st.column_config.SelectboxColumn("Minutos", options=lista_minutos),
        "Origem": st.column_config.TextColumn("Origem (Setor/Parceiro)")
    }, hide_index=True, num_rows="fixed", use_container_width=True, key="ativ_editor")

    # --- SEÇÃO: DIFICULDADES E BLOQUEIOS ---
    st.subheader("⚠️ Dificuldades e Bloqueios")
    if 'df_dificuldades' not in st.session_state:
        st.session_state.df_dificuldades = pd.DataFrame({"Atividade Descrita": [""] * 20, "Frequência": [""] * 20, "Horas": [""] * 20, "Minutos": [""] * 20, "Origem": [""] * 20})
    
    st.session_state.df_dificuldades = st.data_editor(st.session_state.df_dificuldades, column_config={
        "Frequência": st.column_config.SelectboxColumn("Frequência", options=lista_frequencia),
        "Horas": st.column_config.SelectboxColumn("Horas", options=lista_horas),
        "Minutos": st.column_config.SelectboxColumn("Minutos", options=lista_minutos),
        "Origem": st.column_config.TextColumn("Origem (Setor/Parceiro)")
    }, hide_index=True, num_rows="fixed", use_container_width=True, key="dif_editor")

    # --- SEÇÃO: SUGESTÕES E MELHORIAS ---
    st.subheader("💡 Sugestões e Melhorias")
    if 'df_sugestoes' not in st.session_state:
        st.session_state.df_sugestoes = pd.DataFrame({"Atividade Descrita": [""] * 20, "Frequência": [""] * 20, "Horas": [""] * 20, "Minutos": [""] * 20, "Origem": [""] * 20, "Impacto Esperado": [""] * 20})
    
    st.session_state.df_sugestoes = st.data_editor(st.session_state.df_sugestoes, column_config={
        "Frequência": st.column_config.SelectboxColumn("Frequência", options=lista_frequencia),
        "Horas": st.column_config.SelectboxColumn("Horas", options=lista_horas),
        "Minutos": st.column_config.SelectboxColumn("Minutos", options=lista_minutos),
        "Origem": st.column_config.TextColumn("Origem (Setor/Parceiro)"),
        "Impacto Esperado": st.column_config.TextColumn("Impacto Esperado")
    }, hide_index=True, num_rows="fixed", use_container_width=True, key="sug_editor")

    # Agora o formulário apenas para os campos de texto e o DISC
    with st.form("form_envio_final"):
        col1, col2 = st.columns(2)
        nome = col1.text_input("Nome do colaborador", key="f_nome")
        setor = col2.text_input("Setor", key="f_setor")
        cargo = col1.text_input("Cargo", key="f_cargo")
        chefe = col2.text_input("Chefe imediato", key="f_chefe")
        departamento = col1.text_input("Departamento", key="f_dep")
        empresa = col2.text_input("Empresa / Unidade", key="f_emp")
        
        cursos = st.text_area("Cursos obrigatórios", key="f_cursos")
        objetivo = st.text_area("Principal objetivo", key="f_obj")

        st.subheader("📊 Questionário DISC")
        for i, pergunta in enumerate(perguntas_disc, 1):
            st.radio(f"{i}. {pergunta}", ["A", "B", "C", "D"], key=f"disc_{i}", horizontal=True, index=None)

        enviar = st.form_submit_button("🚀 ENVIAR FORMULÁRIO FINAL")

    if enviar:
        import pytz
        from datetime import datetime
        fuso = pytz.timezone('America/Sao_Paulo')
        data_hoje = datetime.now(fuso).strftime('%d/%m/%Y %H:%M:%S')

        # Validação simples
        if not nome or not setor:
            st.error("⚠️ Nome e Setor são obrigatórios!")
        else:
            dados = {
                "nome": nome,
                "data": data_hoje,
                "atividades": st.session_state.df_atividades.to_dict('records'),
                "dificuldades": st.session_state.df_dificuldades.to_dict('records'),
                "sugestoes": st.session_state.df_sugestoes.to_dict('records'),
                "disc": {f"p_{i}": st.session_state.get(f"disc_{i}") for i in range(1, 25)}
            }
            # Aqui você salva o seu JSON
            st.success(f"✅ Enviado com sucesso, {nome}!")


        # -------------------------------------------------
        # VALIDAÇÕES E PROCESSAMENTO
        # -------------------------------------------------
        
        if enviar:
            fuso_brasilia = pytz.timezone('America/Sao_Paulo')
            data_hoje = datetime.now(fuso_brasilia).strftime('%d/%m/%Y %H:%M:%S')
            
            campos_obrigatorios = [nome, setor, cargo, chefe, departamento, empresa, cursos, objetivo]

            # --- VALIDAÇÃO INTELIGENTE DAS TABELAS ---
            tabelas_incompletas = False
            
            for df in [edit_ativ, edit_dif, edit_sug]:
                # Pega apenas as linhas onde a primeira coluna (Descrição/Atividade) foi preenchida
                col_principal = df.columns[0]
                linhas_com_conteudo = df[df[col_principal].astype(str).str.strip() != ""]
                
                # Se houver linhas com texto, verifica se alguma célula nessas linhas está vazia
                if len(linhas_com_conteudo) > 0:
                    if linhas_com_conteudo.isnull().values.any() or (linhas_com_conteudo == "").values.any():
                        tabelas_incompletas = True
                        break
                
                # Se for a tabela de atividades, obriga pelo menos uma linha
                if df is edit_ativ and len(linhas_com_conteudo) == 0:
                    tabelas_incompletas = True
                    st.error("⚠️ A tabela de 'Atividades Principais' não pode estar vazia.")
                    break

           # 1. VALIDAÇÃO DE CAMPOS DE TEXTO
            if any(not str(campo).strip() for campo in campos_obrigatorios):
                st.error("⚠️ Erro: Preencha todos os campos obrigatórios!")
                st.session_state["confirmado"] = False
                st.stop()  # Trava aqui e mantém os dados para correção

            # 2. VALIDAÇÃO DAS TABELAS
            if tabelas_incompletas:
                st.error("⚠️ Erro: Verifique as tabelas! A tabela de atividades não pode estar vazia.")
                st.session_state["confirmado"] = False
                st.stop()

            # 3. VALIDAÇÃO DO DISC
            if any(st.session_state.get(f"disc_{i}") is None for i in range(1, 25)):
                st.error("⚠️ Erro: Responda todas as perguntas do DISC!")
                st.session_state["confirmado"] = False
                st.stop()

            # -------------------------------------------------
            # SE CHEGOU AQUI, PASSOU NAS VALIDAÇÕES
            # -------------------------------------------------
            import os
            import json

            base_dir = os.path.dirname(os.path.abspath(__file__))
            dados_dir = os.path.join(base_dir, "dados")
            os.makedirs(dados_dir, exist_ok=True)

            # 3. EVITAR DUPLICIDADE
            nome_limpo = nome.strip().replace(" ", "_")
            arquivos_existentes = [f for f in os.listdir(dados_dir) if f.startswith(nome_limpo)]

            if arquivos_existentes and not st.session_state.get("confirmado", False):
                st.error(f"⚠️ Já existe um formulário enviado para '{nome}'.")
                st.stop() # Para e obriga a confirmação se quiser sobrescrever
            
            # 4. CONFIRMAÇÃO (O Double-Click de Segurança)
            if not st.session_state.get("confirmado", False):
                st.warning("⚠️ Revise o formulário. Clique novamente no botão para confirmar o envio.")
                st.session_state["confirmado"] = True
                st.stop() # Para aqui e espera o segundo clique
            
            # PROCESSO DE SALVAMENTO (Só acontece após o segundo clique)
            dados = {
                "nome": nome,
                "data_envio": data_hoje,
                "setor": setor,
                "cargo": cargo,
                "chefe": chefe,
                "departamento": departamento,
                "empresa": empresa,
                "escolaridade": escolaridade,
                "devolucao": devolucao,
                "cursos_obrigatorios_ou_diferenciais": cursos,
                "trabalho_e_principal_objetivo": objetivo,
                "atividades": edit_ativ.to_dict('records') if hasattr(edit_ativ, 'to_dict') else edit_ativ,
                "dificuldades": edit_dif.to_dict('records') if hasattr(edit_dif, 'to_dict') else edit_dif,
                "sugestoes": edit_sug.to_dict('records') if hasattr(edit_sug, 'to_dict') else edit_sug,
                "disc": {
                    f"disc_{i}": st.session_state.get(f"disc_{i}")
                    for i in range(1, 25)
                }
            }
            
            caminho = os.path.join(dados_dir, f"{nome_limpo}.json")
            with open(caminho, "w", encoding="utf-8") as f:
                json.dump(dados, f, ensure_ascii=False, indent=4)
            
            st.success("✅ Formulário enviado com sucesso!")
            st.session_state["confirmado"] = False # Reseta para o próximo
                        


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
            nome_exibir = str(form.get('Nome', f'Colaborador {idx}')).upper()
            
            # Primeiro, garantimos que a variável nome_exibir pegue a chave 'nome'
            nome_exibir = form.get('nome', 'Não identificado').upper()
            data_exibir = form.get('data_envio', 'Sem Data')

            with st.expander(f"👤 FORMULÁRIO DE: {nome_exibir} ({data_exibir})"):
                # [Aqui você mantém o seu código de exibição de dados]
                
            
            
            
                # 1. Cabeçalho Completo
                st.subheader("📝 Informações de Identificação")
                col1, col2 = st.columns(2)
                
                # Buscando as chaves minúsculas do seu dicionário 'dados'
                col1.write(f"**Data de Envio:** {form.get('data_envio', 'N/A')}")
                col2.write(f"**Devolver em:** {form.get('devolucao', 'N/A')}")
                
                col_a, col_b = st.columns(2)
                col_a.write(f"**Setor:** {form.get('setor', 'N/A')}")
                col_b.write(f"**Departamento:** {form.get('departamento', 'N/A')}")
                col_a.write(f"**Cargo:** {form.get('cargo', 'N/A')}")
                col_b.write(f"**Chefe Imediato:** {form.get('chefe', 'N/A')}")
                col_a.write(f"**Empresa/Unidade:** {form.get('empresa', 'N/A')}")
                col_b.write(f"**Escolaridade:** {form.get('escolaridade', 'N/A')}")
                
                # Buscando os nomes longos e específicos que definimos
                st.text_area("Cursos obrigatórios ou diferenciais", value=form.get('cursos_obrigatorios_ou_diferenciais', 'N/A'), disabled=True, key=f"cursos_{idx}")
                st.text_area("Trabalho e principal objetivo", value=form.get('trabalho_e_principal_objetivo', 'N/A'), height=150, disabled=True, key=f"obj_{idx}")
                
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
                
                # 3. Questionário DISC
                st.markdown("---")
                st.subheader("📊 Avaliação DISC (Perguntas e Respostas)")
                
                dados_disc = form.get("disc", {}) # Entra na "pasta" disc do JSON
                
                for i, pergunta in enumerate(perguntas_disc, 1):
                    valor_resposta = dados_disc.get(f"disc_{i}", "Não respondido")
                    st.write(f"**{i}. {pergunta}**")
                    st.info(f"Resposta selecionada: **{valor_resposta}**")
                    st.markdown("---")

                # --- BLOCO DE EXPORTAÇÃO (SÓ WORD E PDF) ---
                if st.session_state.get("usuario_logado") == "Luciano 123":
                    st.markdown("---")
                    st.subheader("⚙️ Painel de Exportação")
                    
                    # Usamos 2 colunas para ficar mais harmônico
                    col1, col2 = st.columns(2)
                    
                    # Padronização do nome do arquivo (ajustado para chaves minúsculas)
                    data_raw = form.get('data_envio', '')
                    data_clean = str(data_raw).replace('/', '').replace(' ', '_').replace(':', '')
                    nome_raw = form.get('nome', 'Colaborador')
                    nome_clean = str(nome_raw).replace(' ', '_')
                    nome_arquivo = f"Relatorio_{nome_clean}_{data_clean}"
                    
                    with col1:
                        st.download_button(
                            label="📄 Baixar em Word",
                            data=gerar_word(form),
                            file_name=f"{nome_arquivo}.docx",
                            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                            key=f"word_btn_{idx}"  # Garante ID único no loop
                        )
                    
                    with col2:
                        st.download_button(
                            label="📑 Baixar em PDF",
                            data=gerar_pdf(form),
                            file_name=f"{nome_arquivo}.pdf",
                            mime="application/pdf",
                            key=f"pdf_btn_{idx}"   # Garante ID único no loop
                        )
                # --- FIM DO BLOCO ---



        # Botão de Limpeza
        st.markdown("---")
        if st.button("🗑️ LIMPAR TODOS OS FORMULÁRIOS"):
            for arquivo in os.listdir(dados_dir):
                if arquivo.endswith(".json"): 
                    os.remove(os.path.join(dados_dir, arquivo))
            st.session_state["formularios"] = []
            st.success("✅ Banco de dados limpo!"); st.rerun()

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
        return {
            "atividades": [
                {
                    "nome_atividade": "Atividade de exemplo",
                    "descricao": "Descrição de exemplo",
                    "frequencia_ideal": "Semanal",
                    "tempo_medio_minutos": 60,
                    "justificativa_tecnica": "Exemplo"
                }
            ],
            "dificuldades_bloqueios": [
                {
                    "nome_atividade": "Falta de documentação",
                    "descricao": "Ausência de manuais ou POPs atualizados",
                    "frequencia_ideal": "Diário",
                    "tempo_medio_minutos": 30,
                    "justificativa_tecnica": "Gera retrabalho e inconsistência na execução."
                },
                {
                    "nome_atividade": "Instabilidade de Sistema",
                    "descricao": "Lentidão no software principal",
                    "frequencia_ideal": "Diário",
                    "tempo_medio_minutos": 45,
                    "justificativa_tecnica": "Impede o cumprimento dos prazos estabelecidos."
                }
            ],
            "sugestoes": [
                {
                    "nome_atividade": "Checklist Digital",
                    "descricao": "Implementação de verificações automáticas",
                    "frequencia_ideal": "Semanal",
                    "tempo_medio_minutos": 20,
                    "justificativa_tecnica": "Redução de erros manuais e ganho de tempo."
                }
            ]
        }
    
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
# FUNÇÃO PARA SALVAR FORMULÁRIO EM JSON
# ============================================================
def salvar_formulario_json(formulario):
    """
    Recebe um dicionário do formulário preenchido, salva no arquivo 
    JSON único dentro da pasta 'dados' e atualiza a sessão para 
    espelhamento imediato na interface.
    """
    # 1. Tenta carregar os dados existentes ou cria uma lista vazia
    try:
        with open(json_master, "r", encoding="utf-8") as f:
            dados_existentes = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        # Se o arquivo não existir ou estiver vazio/inválido, inicia como lista vazia
        dados_existentes = []

    # 2. Adiciona o novo formulário à lista
    dados_existentes.append(formulario)

    # 3. Salva a lista completa de volta no arquivo
    with open(json_master, "w", encoding="utf-8") as f:
        json.dump(dados_existentes, f, ensure_ascii=False, indent=4)

    # 4. Atualiza o estado da sessão do Streamlit para refletir a mudança instantaneamente
    st.session_state["formularios"] = dados_existentes