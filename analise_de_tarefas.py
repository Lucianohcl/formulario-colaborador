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

    # Adicione um usuário padrão para o login funcionar
    st.session_state.users = {"admin": {"password": hash_senha("123"), "admin": True}}

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
# IMPORTS NECESSÁRIOS
# ============================================================
import os
import streamlit as st
from fpdf import FPDF

# ============================================================
# CONFIGURAÇÃO DE DIRETÓRIO BASE
# ============================================================
if "BASE_DIR" not in globals():
    BASE_DIR = os.getcwd()  # usa diretório atual como fallback

   

# ============================================================
# INICIALIZAÇÃO DE SESSÃO
# ============================================================
if "users" not in st.session_state:
    st.session_state.users = {}

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "current_user" not in st.session_state:
    st.session_state.current_user = None

# ============================================================
# LOGIN
# ============================================================
if not st.session_state.logged_in:
    st.title("🔐 Login")
    usuario = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")

    if st.button("Login"):
        user = st.session_state.get("users", {}).get(usuario)
        # Fallback para teste rápido se o banco estiver vazio
        if usuario == "admin" and senha == "admin123":
             st.session_state.logged_in = True
             st.session_state.current_user = usuario
             st.session_state.pagina = "formulario"
             st.rerun()
        elif user and user.get("password") == hash_senha(senha):
            st.session_state.logged_in = True
            st.session_state.current_user = usuario
            st.session_state.pagina = "formulario"
            st.rerun()
        else:
            st.error("Usuário ou senha incorretos")
    
    # O stop fica AQUI (dentro do if not logged_in)
    # Ele impede que qualquer coisa abaixo apareça para quem não logou
    st.stop() 

# ============================================================
# PÓS-LOGIN (Só chega aqui quem está logado)
# ============================================================
if "pagina" not in st.session_state:
    st.session_state.pagina = "formulario"

# ============================================================
# PÓS-LOGIN (Só chega aqui quem passou pelo st.stop())
# ============================================================
if "pagina" not in st.session_state:
    st.session_state.pagina = "formulario"

# ============================================================
# PÁGINA PRINCIPAL (apenas usuários logados)
# ============================================================
else:
    # Verifica apenas se a sessão está ativa
    if not st.session_state.logged_in:
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

        # Admin
        btn_admin = False
        current_user = st.session_state.get("current_user")
        if current_user and st.session_state.get("users", {}).get(current_user, {}).get("admin", False):
            btn_admin = st.button("⚙️ Administração")

        # Logout
        if st.button("🚪 Logout"):
            st.session_state.logged_in = False
            st.session_state.current_user = None
            
            st.rerun()

    
    # ============================================================
    # CONTROLE DE PÁGINA (SUBSTITUIÇÃO CORRIGIDA)
    # ============================================================
    if btn_formulario:
        st.session_state.pagina = "formulario"
        st.rerun()
    elif btn_analise:
        st.session_state.pagina = "analise"
        st.rerun()
    elif btn_comparar:
        st.session_state.pagina = "comparar"
        st.rerun()
    elif btn_disc:
        st.session_state.pagina = "disc"
        st.rerun()
    elif btn_parecer:
        st.session_state.pagina = "parecer"
        st.rerun()
    elif btn_visualizar:
        st.session_state.pagina = "visualizar"
        st.rerun()
    # ============================================================
    # 🖼️ ÁREA DE EXIBIÇÃO DO CONTEÚDO (VERSÃO FINAL)
    # ============================================================
    
    if st.session_state.pagina == "home":
        st.title("🏠 Sistema de Análise de Tarefas")
        st.info("Bem-vindo! Use o menu lateral para navegar.")

    elif st.session_state.pagina == "formulario":
        st.title("📝 Formulário do Colaborador")
        with st.form("meu_formulario"):
            nome = st.text_input("Nome do Colaborador", value=st.session_state.get("current_user", ""))
            atividades = st.text_area("Descreva suas principais atividades:")
            horas = st.number_input("Total de horas semanais", min_value=1, max_value=100, value=44)
            
            enviado = st.form_submit_button("Salvar Dados")
            if enviado:
                st.session_state.dados_salvos = {"Nome": nome, "Atividades": atividades, "Horas": horas}
                st.success("Dados salvos com sucesso!")

    elif st.session_state.pagina == "analise":
        st.title("📊 Análise Inteligente")
        
        # Margem de 50% ajustável [2026-02-27]
        margem = st.slider("Ajustar Margem de Aceitação (%)", 0, 100, 50)
        
        if st.button('📥 BAIXAR EXCEL FINAL'):
            if "dados_salvos" in st.session_state:
                df = pd.DataFrame([st.session_state.dados_salvos])
                df["Margem"] = f"{margem}%"
                
                # Gerando o CSV/Excel para download
                csv = df.to_csv(index=False).encode('utf-8-sig')
                st.download_button(
                    label="Confirmar Download do Arquivo",
                    data=csv,
                    file_name=f"Analise_{st.session_state.current_user}.csv",
                    mime="text/csv"
                )
            else:
                st.warning("Por favor, preencha o formulário primeiro.")

    elif st.session_state.pagina == "comparar":
        st.title("⚖️ Comparativo: Real x Ideal")
        st.write("Visualização das lacunas de performance.")

    elif st.session_state.pagina == "disc":
        st.title("🧠 Perfil Comportamental DISC")
        st.write("Resultado do mapeamento de perfil.")

    elif st.session_state.pagina == "parecer":
        st.title("📋 Parecer Final Executivo")
        # Aqui você chama a sua função gerar_pdf() do ReportLab
        if st.button("Gerar PDF"):
            st.info("Gerando PDF com ReportLab...")

    elif st.session_state.pagina == "visualizar":
        st.title("📂 Histórico de Relatórios")
        st.write("Visualize análises salvas anteriormente.")

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
        # Retorna atividade de exemplo caso o GPT não esteja disponível
        return [
            {
                "nome_atividade": "Atividade de exemplo",
                "descricao": "Descrição de exemplo",
                "frequencia_ideal": "semanal",
                "tempo_medio_minutos": 60,
                "justificativa_tecnica": "Exemplo de justificativa"
            }
        ]

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
        # Em caso de erro na resposta do GPT, retorna atividade de exemplo
        return [
            {
                "nome_atividade": "Atividade de exemplo",
                "descricao": "Descrição de exemplo",
                "frequencia_ideal": "semanal",
                "tempo_medio_minutos": 60,
                "justificativa_tecnica": "Exemplo de justificativa"
            }
        ]

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


def gerar_pdf(parecer, nome):
    nome_arquivo = f"{nome}_parecer.pdf" # Criamos uma variável para o nome
    doc = SimpleDocTemplate(nome_arquivo)
    elements = []
    styles = getSampleStyleSheet()

    elements.append(Paragraph("PARECER ESTRATÉGICO ORGANIZACIONAL", styles["Title"]))
    elements.append(Spacer(1, 0.5 * inch))

    for linha in parecer.split("\n"):
        if linha.strip(): # Evita parágrafos vazios que dão erro
            elements.append(Paragraph(linha, styles["Normal"]))
            elements.append(Spacer(1, 0.2 * inch))

    doc.build(elements)
    return nome_arquivo  # <--- ADICIONE ISSO PARA PODER BAIXAR