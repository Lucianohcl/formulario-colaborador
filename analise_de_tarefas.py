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

# ============================================================
# CONFIGURAÇÃO DA PÁGINA
# ============================================================

st.set_page_config(
    page_title="Sistema de Análise de Tarefas",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# SESSION STATE (Inicialização Obrigatória Antes do Uso)
# ============================================================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "pagina" not in st.session_state:
    st.session_state.pagina = "home"

if "formularios" not in st.session_state:
    st.session_state["formularios"] = []

# ============================================================
# LEITURA DE URL (Query Params)
# ============================================================

# Lemos a URL apenas se estivermos na home, permitindo o acesso direto
params = st.query_params
if "page" in params and st.session_state.pagina == "home":
    # O valor passado em ?page=valor no link deve corresponder a um dos seus estados de página
    st.session_state.pagina = params["page"]


# ============================================================
# DIRETÓRIO BASE
# ============================================================

BASE_DIR = "dados"

if not os.path.exists(BASE_DIR):
    os.makedirs(BASE_DIR)

# ============================================================
# SESSION STATE
# ============================================================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "pagina" not in st.session_state:
    st.session_state.pagina = "home"

if "formularios" not in st.session_state:
    st.session_state["formularios"] = []

# ============================================================
# LOGIN
# ============================================================

if not st.session_state.logged_in:

    st.title("🔐 Acesso")

    usuario = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")

    if st.button("Entrar", key="login_button"):

        if (usuario == "admin" and senha == "admin123") or (usuario == "Luciano" and senha == "123"):

            st.session_state.logged_in = True
            st.session_state.user_nome = usuario
            st.session_state.is_admin = True

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

elif btn_logout:
    st.session_state.logged_in = False
    st.session_state.pagina = "home"

if pagina_anterior != st.session_state.pagina:
    st.rerun()

# ============================================================
# FUNÇÃO SALVAR FORMULÁRIO JSON
# ============================================================

def salvar_formulario_json(dados):

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    nome = dados.get("Nome","colaborador").replace(" ","_")

    arquivo = f"{BASE_DIR}/formulario_{nome}_{timestamp}.json"

    with open(arquivo,"w",encoding="utf-8") as f:
        json.dump(dados,f,ensure_ascii=False,indent=4)

    return arquivo

# if st.button("📨 FINALIZAR E ENVIAR QUESTIONÁRIO", key="finalizar_disc"):

    if not nome or not empresa:

        st.error("Preencha Nome e Empresa")

    else:

        dados = {

            "Nome": nome,
            "Empresa": empresa,
            "Departamento": departamento,
            "Cargo": cargo,
            "Chefe": chefe,
            "Escolaridade": escolaridade,
            "Cursos": cursos,
            "Objetivo": objetivo,

            "Atividades": edit_ativ.to_dict("records"),
            "Dificuldades": edit_dif.to_dict("records"),
            "Sugestoes": edit_sug.to_dict("records"),

            "DISC": respostas_disc,

            "DataEnvio": datetime.now().strftime("%d/%m/%Y %H:%M")

        }

        caminho = salvar_formulario_json(dados)

        st.success("✅ Formulário enviado com sucesso!")
        st.info(f"Arquivo salvo: {caminho}")

        st.balloons()



# ===========================
# PÁGINA DE VISUALIZAÇÃO
# ===========================
if st.session_state.pagina == "visualizar":    
    
    st.title("👁️ Espelho Fiel de Respostas")
    st.info("Veja exatamente o que cada colaborador preencheu, campo a campo.")

    arquivos = [f for f in os.listdir(BASE_DIR) if f.endswith(".json")]

    if not arquivos:
        st.warning("⚠️ Nenhum formulário enviado ainda.")
    else:
        for arq in arquivos:
            caminho = os.path.join(BASE_DIR, arq)
            with open(caminho, encoding="utf-8") as f:
                form = json.load(f)

            nome_exibicao = form.get("Nome", "Colaborador")
            with st.expander(f"👤 FORMULÁRIO DE: {nome_exibicao.upper()}"):
                # --- IDENTIFICAÇÃO ---
                st.subheader("🔹 Identificação")
                c1, c2 = st.columns(2)
                with c1:
                    st.write(f"**Nome:** {form.get('Nome','Não informado')}")
                    st.write(f"**Cargo:** {form.get('Cargo','Não informado')}")
                    st.write(f"**Setor:** {form.get('Setor','Não informado')}")
                    st.write(f"**Chefe:** {form.get('Chefe','Não informado')}")
                with c2:
                    st.write(f"**Departamento:** {form.get('Departamento','Não informado')}")
                    st.write(f"**Empresa / Unidade:** {form.get('Empresa','Não informado')}")
                    st.write(f"**Escolaridade:** {form.get('Escolaridade','Não informado')}")
                    st.write(f"**Devolver preenchido em:** {form.get('Devolver','Não informado')}")
                    st.write("**Cursos obrigatórios ou diferenciais:**")
                    st.info(form.get("Cursos","Não informado"))
                    st.write("**Trabalho e principal objetivo:**")
                    st.info(form.get("Objetivo","Não informado"))

                # --- ATIVIDADES ---
                st.markdown("---")
                st.subheader("🔹 Atividades Executadas")
                st.table(pd.DataFrame(form.get("Atividades", [])))

                # --- DIFICULDADES ---
                st.subheader("🔹 Dificuldades na Execução")
                st.table(pd.DataFrame(form.get("Dificuldades", [])))

                # --- SUGESTÕES ---
                st.subheader("💡 Sugestões de Melhoria")
                st.table(pd.DataFrame(form.get("Sugestoes", [])))

                # --- DISC ---
                st.markdown("---")
                st.subheader("🧠 Questionário DISC")
                respostas_disc = {k:v for k,v in form.items() if k.startswith("Q")}
                lista_disc = []
                for i, pergunta in enumerate(perguntas_disc, 1):
                    letra = respostas_disc.get(f"Q{i}", "-")
                    sig = ""
                    if letra != "-" and "|" in pergunta:
                        for p in pergunta.split("|"):
                            if f"({letra})" in p:
                                sig = p.split(")")[-1].strip()
                    lista_disc.append({
                        "Nº": i,
                        "Pergunta": pergunta.split(":")[0],
                        "Resposta": f"{letra} - {sig}" if sig else letra
                    })
                st.table(lista_disc)

        # BOTÃO LIMPAR TODOS OS FORMULÁRIOS
        if st.button("🗑️ LIMPAR TODOS OS FORMULÁRIOS", key="limpar_formularios"):
            for arq in arquivos:
                os.remove(os.path.join(BASE_DIR, arq))
            st.success("✅ Todos os formulários foram removidos da memória!")
            st.experimental_rerun()

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
os.makedirs(BASE_DIR, exist_ok=True)
JSON_MASTER = os.path.join(BASE_DIR, "formularios.json")

# Inicializa arquivo JSON se não existir
if not os.path.exists(JSON_MASTER):
    with open(JSON_MASTER, "w", encoding="utf-8") as f:
        json.dump([], f, ensure_ascii=False, indent=4)

# ============================================================
# FUNÇÃO PARA SALVAR FORMULÁRIO EM JSON
# ============================================================

def salvar_formulario_json(formulario):
    """
    Recebe um dicionário do formulário preenchido
    Salva em arquivo JSON e atualiza a sessão para espelho
    """
    # Carrega dados existentes
    with open(JSON_MASTER, "r", encoding="utf-8") as f:
        dados_existentes = json.load(f)

    # Adiciona novo formulário
    dados_existentes.append(formulario)

    # Salva novamente
    with open(JSON_MASTER, "w", encoding="utf-8") as f:
        json.dump(dados_existentes, f, ensure_ascii=False, indent=4)

    # Atualiza sessão do Streamlit para espelho imediato
    st.session_state["formularios"] = dados_existentes



# ============================================================
# PÁGINA VISUALIZAÇÃO – ESPALHO FIEL
# ============================================================

if st.session_state.get("pagina") == "visualizar":
    

    # Carrega formulários da sessão
    if not st.session_state.get("formularios"):
        st.warning("⚠️ Nenhum formulário preenchido ainda.")
    else:
        for idx, form in enumerate(st.session_state["formularios"], 1):
            nome_exibicao = form.get("Nome", f"Colaborador {idx}")
            with st.expander(f"👤 FORMULÁRIO DE: {nome_exibicao.upper()}"):
                # IDENTIFICAÇÃO
                st.subheader("🔹 Identificação")
                c1, c2 = st.columns(2)
                with c1:
                    st.write(f"**Nome:** {form.get('Nome','Não informado')}")
                    st.write(f"**Cargo:** {form.get('Cargo','Não informado')}")
                    st.write(f"**Setor:** {form.get('Setor','Não informado')}")
                    st.write(f"**Chefe:** {form.get('Chefe','Não informado')}")
                with c2:
                    st.write(f"**Departamento:** {form.get('Departamento','Não informado')}")
                    st.write(f"**Empresa / Unidade:** {form.get('Empresa','Não informado')}")
                    st.write(f"**Escolaridade:** {form.get('Escolaridade','Não informado')}")
                    st.write(f"**Devolver preenchido em:** {form.get('Devolver','Não informado')}")
                    st.write("**Cursos obrigatórios ou diferenciais:**")
                    st.info(form.get("Cursos","Não informado"))
                    st.write("**Trabalho e principal objetivo:**")
                    st.info(form.get("Objetivo","Não informado"))

                # ATIVIDADES
                st.markdown("---")
                st.subheader("🔹 Atividades Executadas")
                df_ativ = pd.DataFrame(form.get("Atividades", []))
                st.table(df_ativ)

                # DIFICULDADES
                st.subheader("🔹 Dificuldades na Execução")
                df_dif = pd.DataFrame(form.get("Dificuldades", []))
                st.table(df_dif)

                # SUGESTÕES
                st.subheader("💡 Sugestões de Melhoria")
                df_sug = pd.DataFrame(form.get("Sugestoes", []))
                st.table(df_sug)

                # DISC
                st.markdown("---")
                st.subheader("🧠 Questionário DISC")
                respostas_disc = {k:v for k,v in form.items() if k.startswith("Q")}
                lista_disc = []
                for i, pergunta in enumerate(perguntas_disc, 1):
                    letra = respostas_disc.get(f"Q{i}", "-")
                    sig = ""
                    if letra != "-" and "|" in pergunta:
                        for p in pergunta.split("|"):
                            if f"({letra})" in p:
                                sig = p.split(")")[-1].strip()
                    lista_disc.append({
                        "Nº": i,
                        "Pergunta": pergunta.split(":")[0],
                        "Resposta": f"{letra} - {sig}" if sig else letra
                    })
                st.table(lista_disc)

        # BOTÃO LIMPAR TODOS FORMULÁRIOS – correto
        if st.button("🗑️ LIMPAR TODOS OS FORMULÁRIOS", key="limpar_formularios"):
            st.session_state["formularios"] = []
            st.success("✅ Todos os formulários foram removidos da memória!")
            st.experimental_rerun()
