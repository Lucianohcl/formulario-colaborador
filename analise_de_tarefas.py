import streamlit as st
import pandas as pd
import os
import json
import hashlib
from datetime import datetime
from fpdf import FPDF
from openai import OpenAI

# ============================================================
# CONFIGURAÇÃO DA PÁGINA
# ============================================================
st.set_page_config(
    page_title="Formulário do Colaborador",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============================================================
# PASTA BASE (CLOUD READY)
# ============================================================
BASE_DIR = "dados"
os.makedirs(BASE_DIR, exist_ok=True)

# ============================================================
# OPENAI – CONFIGURAÇÃO SEGURA + FALLBACK
# ============================================================
client = None
try:
    OPENAI_KEY = st.secrets["OPENAI_KEY"]
    client = OpenAI(api_key=OPENAI_KEY)
except Exception:
    client = None

# ============================================================
# FUNÇÃO HASH DE SENHA (SEGURANÇA)
# ============================================================
def hash_senha(senha):
    return hashlib.sha256(senha.encode()).hexdigest()

# ============================================================
# USUÁRIOS (SECRETS OU FALLBACK LOCAL)
# ============================================================

if "users" not in st.session_state:

    # Prioriza usuários via secrets (produção)
    if "USERS" in st.secrets:
        st.session_state.users = json.loads(st.secrets["USERS"])
    else:
        # Fallback local (desenvolvimento)
        st.session_state.users = {
            "admin": {
                "password": hash_senha("admin123"),
                "admin": True
            },
            "Luciano": {
                "password": hash_senha("123"),
                "admin": True
            }
        }

# ============================================================
# SESSÃO LOGIN
# ============================================================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.current_user = None

# ============================================================
# FUNÇÕES GERAIS
# ============================================================

def salvar_respostas(
    nome, entrega, devolucao, empresa, escolaridade,
    departamento, cargo, inicio, chefe, cursos,
    resumo, df_atividades, df_dificuldades,
    df_sugestoes, respostas_disc,
    indicadores=None
):
    """
    Salva todas as informações do colaborador
    Inclui indicadores estratégicos gerados na Parte 2
    """

    pasta = os.path.join(BASE_DIR, "respostas_colaboradores")
    os.makedirs(pasta, exist_ok=True)

    nome_arquivo = f"{nome.replace(' ','_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    caminho = os.path.join(pasta, nome_arquivo)

    with pd.ExcelWriter(caminho, engine="xlsxwriter") as writer:

        # Identificação
        df_info = pd.DataFrame({
            "Campo": [
                "Entrega","Devolução","Empresa","Nome",
                "Escolaridade","Departamento","Cargo",
                "Início","Chefe","Cursos"
            ],
            "Resposta": [
                entrega,devolucao,empresa,nome,
                escolaridade,departamento,cargo,
                inicio,chefe,cursos
            ]
        })
        df_info.to_excel(writer, sheet_name="Identificação", index=False)

        # Resumo
        pd.DataFrame({"Resumo":[resumo]}).to_excel(writer, sheet_name="Resumo", index=False)

        # Dados operacionais
        df_atividades.to_excel(writer, sheet_name="Atividades", index=False)
        df_dificuldades.to_excel(writer, sheet_name="Dificuldades", index=False)
        df_sugestoes.to_excel(writer, sheet_name="Sugestões", index=False)

        # DISC
        pd.DataFrame.from_dict(
            respostas_disc,
            orient="index",
            columns=["Resposta"]
        ).to_excel(writer, sheet_name="DISC", index_label="Pergunta")

        # Indicadores estratégicos (Parte 2)
        if indicadores:
            df_ind = pd.DataFrame.from_dict(indicadores, orient="index", columns=["Valor"])
            df_ind.to_excel(writer, sheet_name="Indicadores Estratégicos")

    return caminho


# ============================================================
# DISC – CÁLCULO PERCENTUAL
# ============================================================
def calcular_disc(respostas_disc):
    contagem = {"D":0, "I":0, "S":0, "C":0}
    for r in respostas_disc.values():
        if r in contagem:
            contagem[r] += 1

    total = sum(contagem.values())

    if total > 0:
        percentuais = {k: round(v/total*100,1) for k,v in contagem.items()}
    else:
        percentuais = contagem

    dominante = max(percentuais, key=percentuais.get) if total > 0 else None

    return percentuais, dominante


# ============================================================
# GERAÇÃO PDF EXECUTIVO
# ============================================================
def gerar_pdf(relatorio, nome_colab):

    pdf = FPDF()
    pdf.add_page()

    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, f"RELATÓRIO EXECUTIVO – {nome_colab}", ln=True, align='C')
    pdf.ln(5)

    pdf.set_font("Arial", '', 11)

    for secao, conteudo in relatorio.items():

        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 8, secao, ln=True)
        pdf.set_font("Arial", '', 11)

        if isinstance(conteudo, list):
            for item in conteudo:
                pdf.multi_cell(0, 6, str(item))
                pdf.ln(1)
        else:
            pdf.multi_cell(0, 6, str(conteudo))
            pdf.ln(2)

    arquivo_pdf = os.path.join(BASE_DIR, f"Parecer_{nome_colab}.pdf")
    pdf.output(arquivo_pdf)

    return arquivo_pdf


# ============================================================
# LOGIN
# ============================================================
if not st.session_state.logged_in:

    st.title("🔐 Login")

    usuario = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")

    if st.button("Login"):

        user = st.session_state.users.get(usuario)

        if user and user["password"] == hash_senha(senha):
            st.session_state.logged_in = True
            st.session_state.current_user = usuario
            st.rerun()
        else:
            st.error("Usuário ou senha incorretos")

else:

    # 🔒 Blindagem contra sessão corrompida
    if (
        not st.session_state.get("current_user")
        or st.session_state["current_user"] not in st.session_state.get("users", {})
    ):
        st.session_state.logged_in = False
        st.session_state.current_user = None
        st.rerun()

    # ============================================================
    # SIDEBAR
    # ============================================================
    with st.sidebar:

        st.markdown("### Menu")

        btn_formulario = st.button("🧾 Formulário Colaborador")
        btn_analise = st.button("📊 Análise Inteligente")
        btn_comparar = st.button("📈 Comparar Real x Ideal")
        btn_disc = st.button("🧩 Avaliação DISC")
        btn_parecer = st.button("📝 Parecer Final Executivo")
        btn_visualizar = st.button("📂 Relatórios Salvos")

        btn_admin = False
        # Verificação segura de admin
        current_user = st.session_state.get("current_user")
        if current_user and st.session_state["users"].get(current_user, {}).get("admin", False):
            btn_admin = st.button("⚙️ Administração")

        btn_logout = st.button("🚪 Logout")

    # ============================================================
    # CONTROLE DE PÁGINA
    # ============================================================
    if "pagina" not in st.session_state:
        st.session_state.pagina = "formulario"  # página inicial real para mostrar sidebar completo 

    if btn_formulario:
        st.session_state.pagina = "formulario"
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

    if btn_logout:
        st.session_state.logged_in = False
        st.session_state.current_user = None
        st.experimental_rerun()

    # ============================================================
    # CONTEÚDO PRINCIPAL
    # ============================================================
    if st.session_state.pagina == "home":
        st.title("Sistema de Análise de Tarefas")
        st.write("Selecione uma opção no menu lateral.")

    elif st.session_state.pagina == "formulario":
        st.title("Formulário Colaborador")

    elif st.session_state.pagina == "analise":
        st.title("Análise Inteligente")

    elif st.session_state.pagina == "comparar":
        st.title("Comparar Real x Ideal")

    elif st.session_state.pagina == "disc":
        st.title("Avaliação DISC")

    elif st.session_state.pagina == "parecer":
        st.title("Parecer Final Executivo")

    elif st.session_state.pagina == "visualizar":
        st.title("Relatórios Salvos")    


# ==========================================================
# 🚀 PARTE 2 – MOTOR CORPORATIVO TOTAL
# ==========================================================

import json
import traceback
from statistics import mean
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch


# ==========================================================
# 1️⃣ GERAR ATIVIDADES IDEAIS (ROBUSTO)
# ==========================================================

def gerar_atividades_ideais(cargo, setor):

    if client is None:
        return []

    prompt = f"""
    Gere 12 atividades ideais para:

    Cargo: {cargo}
    Setor: {setor}

    Para cada atividade informe:
    - nome_atividade
    - descricao
    - frequencia_ideal (diaria, semanal, mensal)
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
        return []


# ==========================================================
# 2️⃣ CARGA HORÁRIA + SOBRE/SUBUTILIZAÇÃO
# ==========================================================

def calcular_carga(atividades):

    total_min = 0

    for at in atividades:
        try:
            tempo = float(at.get("tempo_min",0))
        except:
            tempo = 0

        freq = at.get("frequencia","semanal")

        if freq == "diaria":
            total_min += tempo * 5
        elif freq == "mensal":
            total_min += tempo/4
        else:
            total_min += tempo

    horas = total_min/60

    status = "Adequado"
    if horas > 44:
        status = "Sobrecarga"
    elif horas < 30:
        status = "Subutilização"

    return round(horas,2), status


# ==========================================================
# 3️⃣ COMPARAÇÃO SEMÂNTICA COMPLETA
# ==========================================================

def comparar_semanticamente(reais, ideais):

    if client is None:
        return {"score":0,"tempo_gap_medio":0}

    prompt = f"""
    Compare semanticamente:

    Atividades reais:
    {reais}

    Atividades ideais:
    {ideais}

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


# ==========================================================
# 4️⃣ SCORE DISC PONDERADO
# ==========================================================

def score_disc(disc):

    pesos = {"D":1.0,"I":0.9,"S":0.85,"C":0.95}

    total = sum(disc.values())
    if total == 0:
        return 0

    calculo = sum(disc[k]*pesos.get(k,1) for k in disc)
    return round((calculo/total)*100,2)


# ==========================================================
# 5️⃣ CLASSIFICAÇÃO SEMÂNTICA DE DIFICULDADES
# ==========================================================

def classificar_dificuldades_gpt(dificuldades):

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

    Dificuldades:
    {dificuldades}
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


# ==========================================================
# 6️⃣ ÍNDICE GERAL DO CARGO
# ==========================================================

def indice_geral(score_aderencia, score_disc, carga_status):

    fator_carga = 100
    if carga_status == "Sobrecarga":
        fator_carga = 70
    elif carga_status == "Subutilização":
        fator_carga = 75

    return round(mean([score_aderencia, score_disc, fator_carga]),2)


# ==========================================================
# 7️⃣ MOTOR PRINCIPAL COMPLETO
# ==========================================================

def gerar_analise_corporativa(dados):

    ideais = gerar_atividades_ideais(dados["cargo"], dados["setor"])

    comparacao = comparar_semanticamente(dados["atividades"], ideais)

    horas, status_carga = calcular_carga(dados["atividades"])

    disc_score = score_disc(dados["disc"])

    dificuldades_classificadas = classificar_dificuldades_gpt(dados["dificuldades"])

    score_aderencia = comparacao.get("score_aderencia",0)

    indice = indice_geral(score_aderencia, disc_score, status_carga)

    risco = "Baixo"
    if indice < 60:
        risco = "Alto"
    elif indice < 75:
        risco = "Moderado"

    prompt_final = f"""
    Gere parecer estratégico completo considerando:

    Score aderência: {score_aderencia}
    Horas semanais: {horas}
    Status carga: {status_carga}
    Score DISC: {disc_score}
    Dificuldades: {dificuldades_classificadas}
    Índice geral do cargo: {indice}
    Classificação de risco: {risco}

    Inclua:
    - Diagnóstico estrutural
    - Análise de desvios
    - Avaliação comportamental
    - Riscos organizacionais
    - Recomendaação detalhada de redistribuição
    - Atividades corretas para o cargo com tempo e frequência ideais
    - Conclusão executiva
    """

    resposta = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role":"user","content":prompt_final}],
        temperature=0.3
    )

    parecer = resposta.choices[0].message.content

    indicadores = {
        "score_aderencia":score_aderencia,
        "horas_semanais":horas,
        "status_carga":status_carga,
        "score_disc":disc_score,
        "indice_geral":indice,
        "risco":risco
    }

    return parecer, indicadores


# ==========================================================
# 8️⃣ PDF
# ==========================================================

def gerar_pdf(parecer, nome):

    doc = SimpleDocTemplate(f"{nome}_parecer.pdf")
    elements = []
    styles = getSampleStyleSheet()

    elements.append(Paragraph("PARECER ESTRATÉGICO ORGANIZACIONAL", styles["Title"]))
    elements.append(Spacer(1, 0.5 * inch))

    for linha in parecer.split("\n"):
        elements.append(Paragraph(linha, styles["Normal"]))
        elements.append(Spacer(1, 0.2 * inch))

    doc.build(elements)