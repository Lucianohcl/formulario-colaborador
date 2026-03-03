import streamlit as st
import pandas as pd
import os
import json
from datetime import datetime
from fpdf import FPDF

# ============================================================
# CONFIGURAÇÃO PÁGINA
# ============================================================
st.set_page_config(page_title="Formulário do Colaborador", page_icon="📊", layout="wide", initial_sidebar_state="collapsed")

# ============================================================
# PASTA DE DADOS (CLOUD READY)
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
    st.success("OpenAI conectado com sucesso ✅")
except Exception as e:
    st.warning("OpenAI não configurado — usando modo fallback ⚠️")
    client = None

# ============================================================
# SESSÃO USUÁRIOS / LOGIN
# ============================================================
if "users" not in st.session_state:
    st.session_state.users = {
        "admin": {"password": "admin", "admin": True},
        "Luciano": {"password": "123", "admin": True}
    }
if "logged_in" not in st.session_state:
    st.session_state.logged_in = True
    st.session_state.current_user = "Teste"

# ============================================================
# CSS TEMA AZUL + BOTÕES LARANJA
# ============================================================
st.markdown("""
<style>
.stApp { background-color: #1E3A8A; color: white; }
section[data-testid="stSidebar"] { background-color: #1E3A8A; }
h1,h2,h3,h4,h5,h6 { color: white; }
div.stButton > button { background-color: #D97706 !important; color: white !important; font-weight: bold !important; }
div.stButton > button:hover { background-color: #B45309 !important; color: white !important; }
form div.stButton > button { background-color: #D97706 !important; color: white !important; font-weight: bold !important; }
form div.stButton > button:hover { background-color: #B45309 !important; color: white !important; }
.css-1cpxqw2 input, .css-1cpxqw2 textarea { height: 28px !important; }
</style>
""", unsafe_allow_html=True)

# ============================================================
# SIDEBAR MENU
# ============================================================
with st.sidebar:
    st.markdown("---")
    st.markdown("<h3 style='color:white;'>Menu</h3>", unsafe_allow_html=True)
    btn_exportar = st.button("📥 Formulário Colaborador")
    btn_analise = st.button("📊 Análise Colaborador")
    btn_comparar = st.button("📈 Comparar Real x Ideal")
    btn_disc = st.button("🧩 Avaliar Perfil DISC")
    btn_parecer = st.button("📝 Parecer Final Inteligente")
    btn_visualizar = st.button("📂 Visualizar Relatórios Existentes")
    btn_admin = st.button("⚙️ Administração")
    btn_logout = st.button("🚪 Logout")

# ============================================================
# LOGOUT
# ============================================================
if btn_logout:
    st.session_state.logged_in = False
    st.session_state.current_user = None
    st.success("✅ Logout efetuado.")
    st.experimental_rerun()

# ============================================================
# FUNÇÕES GERAIS
# ============================================================
def salvar_respostas(nome, entrega, devolucao, empresa, escolaridade,
                     departamento, cargo, inicio, chefe, cursos,
                     resumo, df_atividades, df_dificuldades, respostas_disc):
    pasta = os.path.join(BASE_DIR, "respostas_colaboradores")
    os.makedirs(pasta, exist_ok=True)
    nome_arquivo = f"{nome.replace(' ','_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    caminho = os.path.join(pasta, nome_arquivo)
    with pd.ExcelWriter(caminho, engine="xlsxwriter") as writer:
        df_info = pd.DataFrame({
            "Campo": ["Entrega","Devolução","Empresa","Nome","Escolaridade","Departamento","Cargo","Início","Chefe","Cursos"],
            "Resposta": [entrega,devolucao,empresa,nome,escolaridade,departamento,cargo,inicio,chefe,cursos]
        })
        df_info.to_excel(writer, sheet_name="Identificação", index=False)
        pd.DataFrame({"Resumo":[resumo]}).to_excel(writer, sheet_name="Resumo", index=False)
        df_atividades.to_excel(writer, sheet_name="Atividades", index=False)
        df_dificuldades.to_excel(writer, sheet_name="Dificuldades", index=False)
        pd.DataFrame.from_dict(respostas_disc, orient="index", columns=["Resposta"]).to_excel(writer, sheet_name="DISC", index_label="Pergunta")
    return caminho


def calcular_disc(respostas_disc):
    contagem = {"D":0, "I":0, "S":0, "C":0}
    for r in respostas_disc.values():
        if r in contagem: contagem[r] += 1
    total = sum(contagem.values())
    percentuais = {k: round(v/total*100,1) for k,v in contagem.items()} if total>0 else contagem
    return percentuais


def gerar_parecer_final(df_atividades, df_dificuldades, disc_percent):
    parecer = {}
    atividades_feedback = []
    for idx,row in df_atividades.iterrows():
        if row["Descrição da Atividade"].strip():
            atividades_feedback.append({"Atividade": row["Descrição da Atividade"], "Status":"OK", "Sugestão":f"Verificar frequência {row['Frequência']} e tempo {row['Tempo']}"})
    dificuldades_feedback = []
    for idx,row in df_dificuldades.iterrows():
        if row["Descrição da Dificuldade"].strip():
            dificuldades_feedback.append({"Dificuldade": row["Descrição da Dificuldade"], "Sugestão":"Investigar causas e possíveis treinamentos"})
    parecer["DISC"] = disc_percent
    parecer["Atividades"] = atividades_feedback
    parecer["Dificuldades"] = dificuldades_feedback
    parecer["Observações"] = "Parecer gerado automaticamente. Revise caso necessário."
    return parecer


def gerar_pdf(relatorio, nome_colab):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.set_text_color(0,0,0)
    pdf.cell(0,10,f"Relatório de {nome_colab}", ln=True, align='C')
    pdf.ln(5)
    for k,v in relatorio.items():
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0,6,f"{k}:", ln=True)
        pdf.set_font("Arial", '', 12)
        if isinstance(v,list):
            for item in v:
                linha = ", ".join([f"{kk}: {vv}" for kk,vv in item.items()])
                pdf.multi_cell(0,5,linha)
            pdf.ln(2)
        else:
            pdf.multi_cell(0,5,str(v))
            pdf.ln(2)
    arquivo_pdf = os.path.join(BASE_DIR, f"Parecer_{nome_colab}.pdf")
    pdf.output(arquivo_pdf)
    return arquivo_pdf

# ============================================================
# FORMULÁRIO COLABORADOR
# ============================================================

if btn_exportar:

    st.title("🧾 Levantamento & Diagnóstico do Colaborador")
    st.markdown("---")

    # 🔹 Inicialização segura do session_state
    if "nome_colab" not in st.session_state:
        st.session_state.nome_colab = ""
    if "cargo" not in st.session_state:
        st.session_state.cargo = ""
    if "departamento" not in st.session_state:
        st.session_state.departamento = ""

    # ============================================================
    # Campos de identificação
    # ============================================================

    col1, col2 = st.columns(2)

    with col1:
        entrega = st.text_input("Entregue em (data/hora)")
        empresa = st.text_input("Empresa / Unidade")
        nome = st.text_input("Nome do Colaborador", value=st.session_state.nome_colab)
        departamento = st.text_input("Departamento", value=st.session_state.departamento)
        inicio = st.text_input("Início no Cargo")

    with col2:
        devolucao = st.text_input("Devolver preenchido em (data/hora)")
        escolaridade = st.text_input("Escolaridade")
        cargo = st.text_input("Cargo", value=st.session_state.cargo)
        chefe = st.text_input("Chefe Imediato")

    cursos = st.text_area("Cursos obrigatórios ou diferenciais", height=80)

    st.markdown("---")

    # ============================================================
    # Resumo
    # ============================================================

    resumo = st.text_area("Descreva seu trabalho e principal objetivo:", height=150)

    st.markdown("---")

    # ============================================================
    # Atividades
    # ============================================================

    st.subheader("🔹 Atividades Executadas")

    df_atividades = pd.DataFrame({
        "N°": list(range(1, 21)),
        "Descrição da Atividade": ["" for _ in range(20)],
        "Frequência": ["" for _ in range(20)],
        "Tempo": ["" for _ in range(20)]
    })

    df_atividades = st.data_editor(df_atividades, use_container_width=True, num_rows="fixed")

    st.markdown("---")

    # ============================================================
    # Dificuldades
    # ============================================================

    st.subheader("🔹 Dificuldades na Execução")

    df_dificuldades = pd.DataFrame({
        "Descrição da Dificuldade": ["" for _ in range(20)],
        "Frequência": ["" for _ in range(20)],
        "Tempo": ["" for _ in range(20)],
        "Setor / Parceiro": ["" for _ in range(20)]
    })

    df_dificuldades = st.data_editor(df_dificuldades, use_container_width=True, num_rows="fixed")

    st.markdown("---")

    # ============================================================
    # DISC
    # ============================================================

    st.subheader("🔹 Questionário Comportamental (DISC)")

    perguntas_disc = [f"Pergunta {i}" for i in range(1, 21)]
    respostas_disc = {}

    for i, pergunta in enumerate(perguntas_disc, start=1):
        respostas_disc[f"Q{i}"] = st.radio(
            f"{i}. {pergunta}",
            ["A", "B", "C", "D"],
            horizontal=True,
            key=f"disc_{i}"
        )

    st.markdown("---")

    # ============================================================
    # Envio
    # ============================================================

    if st.button("📨 Finalizar e Enviar Questionário"):

        if not nome or not empresa:
            st.error("❗ Preencha pelo menos Nome e Empresa.")
        else:

            arquivo = salvar_respostas(
                nome, entrega, devolucao, empresa, escolaridade,
                departamento, cargo, inicio, chefe, cursos,
                resumo, df_atividades, df_dificuldades, respostas_disc
            )

            # 🔹 Salva no session_state de forma segura
            st.session_state.df_atividades = df_atividades
            st.session_state.df_dificuldades = df_dificuldades
            st.session_state.respostas_disc = respostas_disc
            st.session_state.nome_colab = nome
            st.session_state.cargo = cargo
            st.session_state.departamento = departamento

            st.success(f"✅ Formulário enviado! Arquivo: {arquivo}")

# ============================================================
# Adicionar novo usuário
# ============================================================
st.markdown("### ➕ Adicionar Novo Usuário")
novo_user = st.text_input("Nome do usuário")
nova_senha = st.text_input("Senha", type="password")
admin_checkbox = st.checkbox("Dar permissão de admin")
if st.button("Adicionar usuário"):
    if novo_user in st.session_state.users:
        st.warning("❗ Usuário já existe.")
    else:
        st.session_state.users[novo_user] = {"password": nova_senha, "admin": admin_checkbox}
        st.success(f"✅ Usuário {novo_user} adicionado com sucesso!")
        st.experimental_rerun()

# Salvar infos do colaborador na sessão para Parecer Premium
st.session_state.nome_colab = nome
st.session_state.cargo = cargo
st.session_state.departamento = departamento

# ============================================================
# PARECER FINAL PREMIUM (Admin) – GPT / Fallback
# ============================================================
if st.session_state.current_user in ["admin","Luciano"] and btn_parecer:
    st.title("📝 Parecer Final Premium (Admin)")

    # Verifica se existem respostas
    keys_necessarias = ["respostas_disc","df_atividades","df_dificuldades","nome_colab","cargo","departamento"]
    if all(k in st.session_state for k in keys_necessarias):
        
        df_atividades = st.session_state.df_atividades
        df_dificuldades = st.session_state.df_dificuldades
        respostas_disc = st.session_state.respostas_disc
        nome_colab = st.session_state.nome_colab
        cargo = st.session_state.cargo
        departamento = st.session_state.departamento

        # 1️⃣ Cálculo DISC
        percentuais_disc = calcular_disc(respostas_disc)

        # 2️⃣ Análise de atividades (GPT ou fallback)
        analise_atividades = []
        if client:
            try:
                prompt_atividades = f"""
Você é especialista em RH. Analise atividades do colaborador {nome_colab} ({cargo}, {departamento}).
Retorne JSON com campos: Atividade, Status (OK/Irregular), Feedback.
Atividades:
{df_atividades.to_csv(index=False)}
"""
                resp_ativ = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role":"user","content":prompt_atividades}],
                    temperature=0.2
                )
                analise_atividades = json.loads(resp_ativ.choices[0].message.content)
            except:
                analise_atividades = [{"Atividade":"Erro GPT","Status":"Erro","Feedback":""}]
        else:
            # fallback local
            for idx,row in df_atividades.iterrows():
                if row["Descrição da Atividade"].strip():
                    analise_atividades.append({
                        "Atividade": row["Descrição da Atividade"],
                        "Status":"OK",
                        "Feedback":"Verificar frequência e tempo"
                    })

        # 3️⃣ Análise de dificuldades (GPT ou fallback)
        analise_dificuldades = []
        if client:
            try:
                prompt_dificuldades = f"""
Você é especialista em RH. Analise dificuldades do colaborador {nome_colab}.
Retorne JSON com campos: Dificuldade, Sugestão.
Dificuldades:
{df_dificuldades.to_csv(index=False)}
"""
                resp_diff = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role":"user","content":prompt_dificuldades}],
                    temperature=0.2
                )
                analise_dificuldades = json.loads(resp_diff.choices[0].message.content)
            except:
                analise_dificuldades = [{"Dificuldade":"Erro GPT","Sugestão":""}]
        else:
            # fallback local
            for idx,row in df_dificuldades.iterrows():
                if row["Descrição da Dificuldade"].strip():
                    analise_dificuldades.append({
                        "Dificuldade": row["Descrição da Dificuldade"],
                        "Sugestão":"Investigar causas e possíveis treinamentos"
                    })

        # 4️⃣ Parecer consolidado
        parecer_final_premium = {
            "Colaborador": nome_colab,
            "Cargo": cargo,
            "Departamento": departamento,
            "DISC": percentuais_disc,
            "Atividades": analise_atividades,
            "Dificuldades": analise_dificuldades,
            "Observações": "Parecer gerado automaticamente via GPT. Revise antes de compartilhar."
        }

        st.subheader("📄 Parecer Final Consolidado")
        st.json(parecer_final_premium)

        # 5️⃣ Gera PDF premium
        arquivo_pdf = gerar_pdf(parecer_final_premium, nome_colab)
        st.success(f"✅ PDF gerado: {arquivo_pdf}")

    else:
        st.info("❗ Nenhum dado de colaborador encontrado para gerar parecer final.")