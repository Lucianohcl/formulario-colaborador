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

# --- LISTA DE PERGUNTAS DISC (GLOBAL) ---
perguntas_disc = [
    "No trabalho, eu prefiro agir com rapidez e focar em resultados?",
    "Eu gosto de convencer as pessoas e trabalhar em equipe?",
    "Eu prefiro manter um ritmo constante e ajudar os colegas?",
    "Eu sou detalhista e prefiro seguir regras e processos?"
    # Adicione aqui TODAS as suas perguntas na ordem exata do formulário
]

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

    import streamlit as st
import pandas as pd
import os
from datetime import datetime

import streamlit as st
import pandas as pd
import os
from datetime import datetime

import streamlit as st
import pandas as pd
import os
from datetime import datetime

import streamlit as st
import pandas as pd
import os
from datetime import datetime

# ============================================================
# 1. TRAVA DE SEGURANÇA
# ============================================================
if 'logado' not in st.session_state:
    st.session_state.logado = False

if not st.session_state.logado:
    st.title("🔑 Acesso ao Sistema")
    user = st.text_input("Usuário")
    password = st.text_input("Senha", type="password")
    
    if st.button("Acessar"):
        if user == "admin" and password == "123": # <--- Ajuste sua senha aqui
            st.session_state.logado = True
            st.session_state.pagina = "home"
            st.rerun()
        else:
            st.error("Credenciais inválidas")
    st.stop() 

# ============================================================
# 2. CONFIGURAÇÕES E SIDEBAR (SÓ RODA SE LOGADO)
# ============================================================
BASE_DIR = "."

if 'pagina' not in st.session_state:
    st.session_state.pagina = "home"

st.sidebar.title("📌 Menu de Navegação")

# 1. Definição dos Botões
btn_home = st.sidebar.button("🏠 Home")
btn_formulario = st.sidebar.button("📝 Formulário do Colaborador")
btn_analise = st.sidebar.button("📊 Análise Inteligente")
btn_comparar = st.sidebar.button("⚖️ Comparar Colaboradores")
btn_disc = st.sidebar.button("🧠 Perfil DISC")
btn_parecer = st.sidebar.button("📄 Parecer Estratégico")
btn_visualizar = st.sidebar.button("👁️ Visualizar Dados")

st.sidebar.markdown("---") 
btn_logout = st.sidebar.button("🚪 Sair / Logout")

# 2. Lógica de Redirecionamento
if btn_home: 
    st.session_state.pagina = "home"
    st.rerun()
elif btn_formulario: 
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
elif btn_logout:
    st.session_state.clear() 
    st.rerun() # O rerun vai voltar pro topo e cair no login automaticamente

# ============================================================
# 3. EXIBIÇÃO DAS PÁGINAS (Área Central)
# ============================================================
# Aqui continua o seu código: if st.session_state.pagina == "home": ...

# ============================================================
# 🖼️ ÁREA DE EXIBIÇÃO DO CONTEÚDO
# ============================================================

if st.session_state.pagina == "home":
    st.title("🏠 Sistema de Análise de Tarefas")
    st.info("Bem-vindo! Use o menu lateral para navegar entre o formulário e as análises.")

elif st.session_state.pagina == "formulario":
    st.title("🧾 Levantamento & Diagnóstico do Colaborador")
    st.caption("Preencha com atenção. Este formulário será analisado pela equipe responsável.")
    st.markdown("---")

    # 🔹 IDENTIFICAÇÃO
    st.subheader("🔹 Identificação")
    col1, col2 = st.columns(2)
    with col1:
        entrega = st.text_input("Entregue em (data/hora)")
        empresa = st.text_input("Empresa / Unidade")
        nome = st.text_input("Nome do Colaborador")
        departamento = st.text_input("Departamento")
    with col2:
        devolucao = st.text_input("Devolver preenchido em")
        escolaridade = st.text_input("Escolaridade")
        cargo = st.text_input("Cargo")
        chefe = st.text_input("Chefe Imediato")
    
    cursos = st.text_area("Cursos obrigatórios ou diferenciais", height=68)
    resumo_trabalho = st.text_area("Descreva seu trabalho e principal objetivo:", height=80)

    # 🔹 ATIVIDADES (COM LEGENDA COMPLETA)
    st.markdown("---")
    st.subheader("🔹 Atividades Executadas")
    st.info("""
    **📋 LEGENDA DE FREQUÊNCIA (O que significa cada letra):**
    * **DVD**: Diário Várias Vezes | **D**: Diário | **S**: Semanal 
    * **Q**: Quinzenal | **M**: Mensal | **T**: Trimestral | **A**: Anual
    """)
    
    df_ativ = pd.DataFrame({"N°": list(range(1, 21)), "Descrição da Atividade": [""]*20, "Frequência": [""]*20, "Tempo": [""]*20})
    edit_ativ = st.data_editor(df_ativ, use_container_width=True, num_rows="fixed", key="ativ_final_v1")

    # 🔹 DIFICULDADES (20 LINHAS)
    st.subheader("🔹 Dificuldades na Execução")
    df_dif = pd.DataFrame({"N°": list(range(1, 21)), "Descrição da Dificuldade": [""]*20, "Setor/Parceiro": [""]*20})
    edit_dif = st.data_editor(df_dif, use_container_width=True, num_rows="fixed", key="dif_final_v1")

    # 🔹 SUGESTÕES (20 LINHAS)
    st.subheader("💡 Sugestões de Melhoria")
    df_sug = pd.DataFrame({"N°": list(range(1, 21)), "Descrição da Sugestão": [""]*20, "Impacto Esperado": [""]*20})
    edit_sug = st.data_editor(df_sug, use_container_width=True, num_rows="fixed", key="sug_final_v1")

    # 🔹 DISC (20 PERGUNTAS)
    st.markdown("---")
    st.subheader("🧠 Questionário Comportamental (DISC)")
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
        "Ambiente ideal: (A) Competitivo | (B) Amigável | (C) Previsível | (D) Disciplinado"
    ]
    respostas_disc = {}
    for i, p in enumerate(perguntas_disc, 1):
        respostas_disc[f"Q{i}"] = st.radio(f"{i}. {p}", ["A", "B", "C", "D"], horizontal=True, key=f"d_v1_{i}")

    if st.button("📨 FINALIZAR E ENVIAR QUESTIONÁRIO"):
        if not nome or not empresa:
            st.error("❌ Por favor, preencha ao menos Nome e Empresa.")
        else:
            # Cria o nome do arquivo com data e hora para não sobrescrever
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            nome_arq = f"Colaborador_{nome.replace(' ', '_')}_{timestamp}.xlsx"
            caminho_salvar = os.path.join(BASE_DIR, nome_arq)

            try:
                with pd.ExcelWriter(caminho_salvar, engine="xlsxwriter") as writer:
                    # Aba ID
                    df_id_save = pd.DataFrame({
                        "Campo": ["Empresa", "Nome", "Data", "Departamento", "Cargo"],
                        "Valor": [empresa, nome, datetime.now().strftime("%d/%m/%Y %H:%M"), departamento, cargo]
                    })
                    df_id_save.to_excel(writer, sheet_name="ID", index=False)

                    # Aba Atividades (apenas as preenchidas)
                    df_ativ_save = edit_ativ[edit_ativ["Descrição da Atividade"] != ""]
                    df_ativ_save.to_excel(writer, sheet_name="Atividades", index=False)

                    # Aba Dificuldades
                    df_dif_save = edit_dif[edit_dif["Descrição da Dificuldade"] != ""]
                    df_dif_save.to_excel(writer, sheet_name="Dificuldades", index=False)

                    # Aba Sugestões
                    df_sug_save = edit_sug[edit_sug["Descrição da Sugestão"] != ""]
                    df_sug_save.to_excel(writer, sheet_name="Sugestões", index=False)

                    # Aba DISC (Questão e Resposta)
                    df_disc_save = pd.DataFrame(list(respostas_disc.items()), columns=["Questão", "Resposta"])
                    df_disc_save.to_excel(writer, sheet_name="DISC", index=False)

                st.success(f"✅ Enviado com sucesso! Arquivo: {nome_arq}")
                st.balloons()
            except Exception as e:
                st.error(f"Erro ao salvar arquivo: {e}")

elif st.session_state.pagina == "analise":
    st.title("📊 Análise Inteligente")
    st.info(f"A inteligência está consolidando os formulários da pasta: {BASE_DIR}")

    # 1. Localiza arquivos dentro da pasta 'dados' (BASE_DIR)
    arquivos = [f for f in os.listdir(BASE_DIR) if f.startswith('Colaborador_') and f.endswith('.xlsx')]

    if not arquivos:
        st.warning("⚠️ Nenhum dado encontrado na pasta 'dados'. Peça aos colaboradores para enviarem os formulários.")
    else:
        lista_atividades = []

        for arq in arquivos:
            try:
                # IMPORTANTE: Construir o caminho completo do arquivo
                caminho_completo = os.path.join(BASE_DIR, arq)
                
                # Lê a aba de Atividades e a de Identificação
                df_ativ = pd.read_excel(caminho_completo, sheet_name="Atividades")
                df_id = pd.read_excel(caminho_completo, sheet_name="ID")
                
                # Pega o nome do colaborador (Coluna 'Valor' onde 'Campo' é 'Nome')
                nome_colab = df_id.loc[df_id['Campo'] == 'Nome', 'Valor'].values[0]
                
                # Adiciona o nome do dono em cada linha de atividade
                df_ativ["Colaborador"] = nome_colab
                
                # Garante que não pegamos linhas vazias
                df_ativ = df_ativ.dropna(subset=["Descrição da Atividade"])
                
                lista_atividades.append(df_ativ)
            except Exception as e:
                # st.error(f"Erro ao ler {arq}: {e}") # Opcional para debug
                continue

        # 2. Se houver atividades, consolida e exibe
        if lista_atividades:
            df_final = pd.concat(lista_atividades, ignore_index=True)

            st.success(f"📈 Análise pronta: {len(arquivos)} colaboradores processados.")
            st.dataframe(df_final, use_container_width=True)

            # --- CONFIGURAÇÕES SOLICITADAS ---
            # O valor para o 50% margin é ajustável
            margem = st.slider("Ajustar Margem de Aceitação (%)", 0, 100, 50)
            
            # Botão de baixar excel final exatamente como solicitado
            nome_saida = "RELATORIO_CONSOLIDADO_FINAL.xlsx"
            df_final.to_excel(nome_saida, index=False)
            
            with open(nome_saida, "rb") as f:
                st.download_button(
                    label="📥 BAIXAR EXCEL FINAL",
                    data=f,
                    file_name=nome_saida,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
        else:
            st.error("⚠️ Nenhum dado válido foi encontrado nos arquivos processados.")

        if lista_atividades:
            # 3. Junta tudo em um Super Excel
            df_final = pd.concat(lista_atividades, ignore_index=True)

            st.success(f"📈 Análise pronta: {len(arquivos)} colaboradores processados.")
            st.dataframe(df_final, use_container_width=True)

            # --- CONFIGURAÇÕES SOLICITADAS ---
            # 1. Slider com valor padrão 50%
            margem = st.slider("Ajustar Margem de Aceitação (%)", 0, 100, 50)
            
            # 2. Botão EXATAMENTE como solicitado: 📥 BAIXAR EXCEL FINAL
            nome_saida = "RELATORIO_CONSOLIDADO_FINAL.xlsx"
            df_final.to_excel(nome_saida, index=False)
            
            with open(nome_saida, "rb") as f:
                st.download_button(
                    label="📥 BAIXAR EXCEL FINAL",
                    data=f,
                    file_name=nome_saida,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
        else:
            st.error("Erro ao processar os arquivos. Verifique se o formato das abas está correto.")
        
elif st.session_state.pagina == "visualizar":
    st.title("👁️ Espelho Fiel de Respostas")
    st.info("Abaixo você vê exatamente o que o colaborador preencheu, campo a campo.")

    # 1. Busca os arquivos na pasta correta
    arquivos = [f for f in os.listdir(BASE_DIR) if f.startswith('Colaborador_') and f.endswith('.xlsx')]

    if not arquivos:
        st.warning("⚠️ Nenhum formulário encontrado no servidor.")
    else:
        for arq in arquivos:
            try:
                # IMPORTANTE: Construir o caminho completo para leitura
                caminho_completo = os.path.join(BASE_DIR, arq)
                
                # Lendo todas as abas do Excel
                df_id = pd.read_excel(caminho_completo, sheet_name="ID")
                df_ativ = pd.read_excel(caminho_completo, sheet_name="Atividades")
                df_dif = pd.read_excel(caminho_completo, sheet_name="Dificuldades")
                df_sug = pd.read_excel(caminho_completo, sheet_name="Sugestões")
                df_disc_salvo = pd.read_excel(caminho_completo, sheet_name="DISC")

                # Pegando dados de identificação
                nome_colab = df_id.loc[df_id['Campo'] == 'Nome', 'Valor'].values[0]
                empresa_colab = df_id.loc[df_id['Campo'] == 'Empresa', 'Valor'].values[0]

                # 2. O EXPANDER com o Nome Completo
                with st.expander(f"👤 FORMULÁRIO DE: {nome_colab.upper()}"):
                    st.write(f"**🏢 Empresa:** {empresa_colab}")
                    st.write(f"**📄 Arquivo original:** `{arq}`")
                    st.markdown("---")

                    # --- SEÇÃO 1: ATIVIDADES ---
                    st.subheader("📝 1. Atividades Executadas")
                    df_ativ_ok = df_ativ.dropna(subset=["Descrição da Atividade"])
                    st.table(df_ativ_ok)

                    # --- SEÇÃO 2: DIFICULDADES E SUGESTÕES ---
                    c1, c2 = st.columns(2)
                    with c1:
                        st.subheader("⚠️ 2. Dificuldades")
                        df_dif_ok = df_dif.dropna(subset=["Descrição da Dificuldade"])
                        st.table(df_dif_ok) if not df_dif_ok.empty else st.write("Nada relatado.")
                    with c2:
                        st.subheader("💡 3. Sugestões")
                        df_sug_ok = df_sug.dropna(subset=["Descrição da Sugestão"])
                        st.table(df_sug_ok) if not df_sug_ok.empty else st.write("Nada relatado.")

                    st.markdown("---")

                    # --- SEÇÃO 3: DISC (ESPELHO FIEL) ---
                    st.subheader("🧠 4. Questionário DISC (Espelho)")
                    
                    # Dicionário de respostas salvas
                    respostas_dict = df_disc_salvo.set_index(df_disc_salvo.columns[0]).to_dict()[df_disc_salvo.columns[1]]
                    lista_espelho_disc = []

                    for i, texto_pergunta in enumerate(perguntas_disc, 1):
                        chave = f"Q{i}"
                        res_letra = respostas_dict.get(chave, "Não respondido")
                        lista_espelho_disc.append({
                            "Nº": i,
                            "Pergunta": texto_pergunta,
                            "Resposta Escolhida": res_letra
                        })
                    
                    st.table(lista_espelho_disc)

                    # Botão para baixar este arquivo específico
                    with open(caminho_completo, "rb") as f:
                        st.download_button(
                            label=f"📥 Baixar Original de {nome_colab}",
                            data=f,
                            file_name=arq,
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            key=f"btn_espelho_{arq}"
                        )
            except Exception as e:
                st.error(f"Erro ao processar o arquivo {arq}: {e}")

        # --- FINAL DA PÁGINA (FORA DO LOOP) ---
        st.markdown("---")
        if st.button("🗑️ LIMPAR TODOS OS REGISTROS"):
            for a in arquivos:
                try:
                    os.remove(os.path.join(BASE_DIR, a))
                except:
                    continue
            st.success("✅ Todos os registros foram excluídos!")
            st.rerun()

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