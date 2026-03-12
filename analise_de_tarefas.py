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
            st.rerun()
        else:
            st.error("Usuário ou senha incorretos")
    
    st.stop() # Bloqueia apenas acessos não autorizados

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


        
if st.query_params.get("page") == "formulario":
    st.title("📋 Formulário Completo do Colaborador")

import streamlit as st

# --- FORMULÁRIO MINIMALISTA ---
st.subheader("Formulário Colaborador")

nome = st.text_input("Nome do colaborador", key="nome")
setor = st.text_input("Setor", key="setor")
cargo = st.text_input("Cargo", key="cargo")
cursos = st.text_area("Cursos obrigatórios ou diferenciais", key="cursos")
objetivo = st.text_area("Trabalho e principal objetivo", key="objetivo")


if st.button("🚀 ENVIAR FORMULÁRIO FINAL", key="btn_enviar_final"):

    st.success("Formulário enviado com sucesso!")
    st.write("Nome:", nome)
    st.write("Setor:", setor)
    st.write("Cargo:", cargo)
    st.write("Cursos:", cursos)
    st.write("Objetivo:", objetivo)


import streamlit as st
import pandas as pd

import streamlit as st
import pandas as pd

# --- LISTAS PADRONIZADAS ---
lista_frequencia = ["DVD", "D", "S", "Q", "M", "T", "A"]
lista_horas = [str(h) for h in range(25)]
lista_minutos = [str(m) for m in range(0, 60, 5)]
impacto_esperado = ["Baixo", "Médio", "Alto"]

# --- FORMULÁRIO COMPLETO ---
with st.container():  # substitui o form e evita erro de duplicação
    st.title("📋 Formulário de Atividades, Dificuldades e Sugestões")

    # --- Dados Pessoais ---
    nome = st.text_input("Nome do colaborador")
    setor = st.text_input("Setor")
    cargo = st.text_input("Cargo")
    cursos = st.text_area("Cursos obrigatórios ou diferenciais")
    objetivo = st.text_area("Trabalho e principal objetivo")

    # --- Legenda de Frequência ---
    st.markdown("---")
    st.info("""
    **📋 LEGENDA DE FREQUÊNCIA (O que significa cada letra):**
    * **DVD**: Diário Várias Vezes | **D**: Diário | **S**: Semanal
    * **Q**: Quinzenal | **M**: Mensal | **T**: Trimestral | **A**: Anual
    """)

    # --- Parte 2: Atividades ---
    st.markdown("---")
    st.subheader("🔹 Atividades Executadas")
    atividades = []

    with st.expander("Clique para preencher as Atividades", expanded=True):
        for i in range(20):
            col1, col2, col3, col4 = st.columns([4, 2, 1, 1])
            with col1:
                atv = st.text_input(f"Atividade {i+1}", key=f"ativ_{i}")
            with col2:
                freq = st.selectbox("Frequência", lista_frequencia, key=f"freq_{i}")
            with col3:
                hrs = st.selectbox("Horas", lista_horas, key=f"hrs_{i}")
            with col4:
                mins = st.selectbox("Minutos", lista_minutos, key=f"mins_{i}")
        
            atividades.append({
                "Atividade": atv,
                "Frequência": freq,
                "Horas": hrs,
                "Minutos": mins
            })

    # --- Parte 3: Dificuldades ---
    st.markdown("---")
    st.subheader("⚠️ Dificuldades e Bloqueios")
    dificuldades = []

    with st.expander("Clique para preencher as Dificuldades", expanded=False):
        for i in range(20):
            col1, col2, col3 = st.columns([4, 3, 1])
            with col1:
                dif = st.text_input(f"Dificuldade {i+1}", key=f"dif_{i}")
            with col2:
                setor_parceiro = st.text_input(f"Setor/Parceiro {i+1}", key=f"setor_{i}")
            with col3:
                tempo = st.selectbox("Tempo Perdido (min)", lista_minutos, key=f"tempo_{i}")

            dificuldades.append({
                "Dificuldade": dif,
                "Setor/Parceiro": setor_parceiro,
                "Tempo Perdido": tempo
            })
    # Fim Parte 3 – termina após loop

    # --- Sugestões ---
    st.markdown("---")
    sugestoes = []
    with st.expander("💡 Sugestões de Melhoria", expanded=False):
        for i in range(20):
            col1, col2 = st.columns([4, 2])
            with col1:
                sug = st.text_input(f"Sugestão {i+1}", key=f"sug_{i}")
            with col2:
                impacto = st.selectbox("Impacto Esperado", impacto_esperado, key=f"impacto_{i}")
            sugestoes.append({"Sugestão": sug, "Impacto Esperado": impacto})

    # --- Botão de Envio ---
    enviar = st.button("🚀 ENVIAR FORMULÁRIO FINAL")

    # --- Ações após envio ---
    if enviar:
        # ✅ Validação mínima
        if not nome or not setor or not cargo:
            st.error("⚠️ Erro: Preencha os campos obrigatórios (Nome, Setor e Cargo).")
        else:
            st.success("Formulário enviado com sucesso!")

            st.subheader("Resumo do Colaborador")
            st.write("Nome:", nome)
            st.write("Setor:", setor)
            st.write("Cargo:", cargo)
            st.write("Cursos:", cursos)
            st.write("Objetivo:", objetivo)

            st.subheader("Resumo das Atividades")
            st.dataframe(pd.DataFrame(atividades))

            st.subheader("Resumo das Dificuldades")
            st.dataframe(pd.DataFrame(dificuldades))

            st.subheader("Resumo das Sugestões")
            st.dataframe(pd.DataFrame(sugestoes))

import streamlit as st
import pandas as pd

import streamlit as st
import pandas as pd
import os
import json
import time

# --- LISTAS PADRONIZADAS ---
lista_frequencia = ["DVD", "D", "S", "Q", "M", "T", "A"]
lista_horas = [str(h) for h in range(25)]
lista_minutos = [str(m) for m in range(0, 60, 5)]
impacto_esperado = ["Baixo", "Médio", "Alto"]

# --- FORMULÁRIO COMPLETO ---
with st.container():  # substitui o form e evita erro de duplicação
    st.title("📋 Formulário Completo do Colaborador")

    # --- Dados Pessoais ---
    nome = st.text_input("Nome do colaborador")
    setor = st.text_input("Setor")
    cargo = st.text_input("Cargo")
    cursos = st.text_area("Cursos obrigatórios ou diferenciais")
    objetivo = st.text_area("Trabalho e principal objetivo")

    # --- Legenda de Frequência ---
    st.markdown("---")
    st.info("""
    **📋 LEGENDA DE FREQUÊNCIA (O que significa cada letra):**
    * **DVD**: Diário Várias Vezes | **D**: Diário | **S**: Semanal
    * **Q**: Quinzenal | **M**: Mensal | **T**: Trimestral | **A**: Anual
    """)

    # --- Atividades ---
    st.markdown("---")
    atividades = []
    with st.expander("🔹 Atividades Executadas", expanded=True):
        for i in range(20):
            col1, col2, col3, col4 = st.columns([4,2,1,1])
            with col1:
                atv = st.text_input(f"Atividade {i+1}", key=f"ativ_{i}")
            with col2:
                freq = st.selectbox("Frequência", lista_frequencia, key=f"freq_{i}")
            with col3:
                hrs = st.selectbox("Horas", lista_horas, key=f"hrs_{i}")
            with col4:
                mins = st.selectbox("Minutos", lista_minutos, key=f"mins_{i}")
            atividades.append({"Atividade": atv, "Frequência": freq, "Horas": hrs, "Minutos": mins})

    # --- Dificuldades ---
    st.markdown("---")
    dificuldades = []
    with st.expander("⚠️ Dificuldades e Bloqueios", expanded=False):
        for i in range(20):
            col1, col2, col3 = st.columns([4,3,1])
            with col1:
                dif = st.text_input(f"Dificuldade {i+1}", key=f"dif_{i}")
            with col2:
                setor_parceiro = st.text_input(f"Setor/Parceiro {i+1}", key=f"setor_{i}")
            with col3:
                tempo = st.selectbox("Tempo Perdido (min)", lista_minutos, key=f"tempo_{i}")
            dificuldades.append({"Dificuldade": dif, "Setor/Parceiro": setor_parceiro, "Tempo Perdido": tempo})

    # --- Sugestões ---
    st.markdown("---")
    sugestoes = []
    with st.expander("💡 Sugestões de Melhoria", expanded=False):
        for i in range(20):
            col1, col2 = st.columns([4,2])
            with col1:
                sug = st.text_input(f"Sugestão {i+1}", key=f"sug_{i}")
            with col2:
                impacto = st.selectbox("Impacto Esperado", impacto_esperado, key=f"impacto_{i}")
            sugestoes.append({"Sugestão": sug, "Impacto Esperado": impacto})

    # --- Botão de envio ---
<<<<<<< HEAD
    enviar = st.button("🚀 ENVIAR FORMULÁRIO FINAL")
=======
    enviar = st.button("🚀 ENVIAR FORMULÁRIO FINAL", key="btn_enviar_final") 
>>>>>>> 701e479 (Atualização: formulário completo, motor de análise e PDF)
    if enviar:
        if not nome or not setor or not cargo:
            st.error("⚠️ Preencha Nome, Setor e Cargo!")
        else:
            # Salvar dados em JSON
            base_dir = os.path.dirname(os.path.abspath(__file__))
            dados_dir = os.path.join(base_dir, "dados")
            os.makedirs(dados_dir, exist_ok=True)

            dados = {
                "Nome": nome,
                "Setor": setor,
                "Cargo": cargo,
                "Cursos": cursos,
                "Objetivo": objetivo,
                "Atividades": atividades,
                "Dificuldades": dificuldades,
                "Sugestoes": sugestoes,
                "DataEnvio": pd.Timestamp.now().strftime("%d/%m/%Y %H:%M")
            }

            nome_limpo = nome.strip().replace(" ", "_") if nome else "sem_nome"
            caminho = os.path.join(dados_dir, f"{nome_limpo}_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.json")

            with open(caminho, "w", encoding="utf-8") as f:
                json.dump(dados, f, ensure_ascii=False, indent=4)

            st.success("✅ Formulário enviado e salvo com sucesso!")
            
      


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
            
            with st.expander(f"👤 FORMULÁRIO DE: {nome_exibir} ({form.get('DataEnvio', 'Sem Data')})"):
                # [Aqui você mantém o seu código de exibição de dados]
                
            
            
            
                # 1. Cabeçalho Completo
                st.subheader("📝 Informações de Identificação")
                col1, col2 = st.columns(2)
                col1.write(f"**Data de Envio:** {form.get('DataEnvio', 'N/A')}")
                col2.write(f"**Devolver em:** {form.get('Devolver', 'N/A')}")
                
                col_a, col_b = st.columns(2)
                col_a.write(f"**Setor:** {form.get('Setor', 'N/A')}")
                col_b.write(f"**Departamento:** {form.get('Departamento', 'N/A')}")
                col_a.write(f"**Cargo:** {form.get('Cargo', 'N/A')}")
                col_b.write(f"**Chefe Imediato:** {form.get('Chefe', 'N/A')}")
                col_a.write(f"**Empresa/Unidade:** {form.get('Empresa', 'N/A')}")
                col_b.write(f"**Escolaridade:** {form.get('Escolaridade', 'N/A')}")
                
                st.write(f"**Cursos:** {form.get('Cursos', 'N/A')}")
                st.info(f"**Objetivo Principal:**\n\n{form.get('Objetivo', 'N/A')}")
                
                # 2. Tabelas Dinâmicas
                secoes = {
                    "Atividades": "📋 Atividades Executadas",
                    "Dificuldades": "⚠️ Dificuldades e Bloqueios",
                    "Sugestoes": "💡 Sugestões de Melhoria"
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
                    valor_resposta = form.get(f"Q{i}", "Não respondido")
                    st.write(f"**{i}. {pergunta}**")
                    st.info(f"Resposta selecionada: **{valor_resposta}**")
                    st.markdown("---")

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
# PARTE 1: CONFIGURAÇÃO E INICIALIZAÇÃO
# ============================================================

import streamlit as st

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


# Configuração da página
st.set_page_config(
    page_title="Sistema de Análise de Tarefas",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inicialização do session_state
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "pagina" not in st.session_state:
    st.session_state.pagina = "home"
if "formularios" not in st.session_state:
    st.session_state["formularios"] = []

# Leitura da URL
query_params = st.query_params
if "page" in query_params:
    st.session_state.pagina = query_params["page"]

# Diretório de dados
if getattr(sys, 'frozen', False):
    base_dir = os.path.dirname(sys.executable)
else:
    base_dir = os.path.dirname(os.path.abspath(__file__))

dados_dir = os.path.join(base_dir, "dados")
os.makedirs(dados_dir, exist_ok=True)

# ============================================================
# PARTE 2: LOGIN E SIDEBAR
# ============================================================

# --- LOGIN COM BYPASS PARA FORMULÁRIO ---
if not st.session_state.logged_in and st.session_state.pagina != "formulario":
    st.title("🔐 Acesso")
    usuario = st.text_input("Usuário", key="login_usuario")
    senha = st.text_input("Senha", type="password", key="login_senha")

    if st.button("Entrar", key="login_button"):
        if (usuario == "admin" and senha == "admin123") or (usuario == "Luciano" and senha == "123"):
            st.session_state.logged_in = True
            st.session_state.user_nome = usuario
            st.session_state.is_admin = True
            st.rerun()
        else:
            st.error("Usuário ou senha incorretos")
    st.stop()  # Bloqueia acessos não autorizados

# --- SIDEBAR ---
st.sidebar.title("📌 Menu de Navegação")
btn_home = st.sidebar.button("🏠 Home", key="btn_home")
btn_analise = st.sidebar.button("📊 Análise Inteligente", key="btn_analise")
btn_comparar = st.sidebar.button("⚖️ Comparar Colaboradores", key="btn_comparar")
btn_disc = st.sidebar.button("🧠 Perfil DISC", key="btn_disc")
btn_parecer = st.sidebar.button("📄 Parecer Estratégico", key="btn_parecer")
btn_visualizar = st.sidebar.button("👁️ Visualizar Dados", key="btn_visualizar")
btn_produtividade = st.sidebar.button("🚀 Produtividade", key="btn_produtividade")
st.sidebar.markdown("---")
btn_logout = st.sidebar.button("🚪 Logout", key="btn_logout")

# Atualiza página
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
elif st.session_state.pagina == "formulario":
    pass
elif btn_logout:
    st.session_state.logged_in = False
    st.session_state.pagina = "home"

# Rerun se a página mudou
if pagina_anterior != st.session_state.pagina:
    st.rerun()

# ============================================================
# PARTE 3: FORMULÁRIO COMPLETO DO COLABORADOR
# ============================================================

# Listas padronizadas
lista_frequencia = ["DVD", "D", "S", "Q", "M", "T", "A"]
lista_horas = [str(h) for h in range(25)]
lista_minutos = [str(m) for m in range(0, 60, 5)]
impacto_esperado = ["Baixo", "Médio", "Alto"]

# Perguntas DISC
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

# ============================================================
# FORMULÁRIO STREAMLIT
# ============================================================
with st.form("formulario_colaborador", clear_on_submit=False):
    st.title("📋 Formulário Completo do Colaborador")

    # --- Dados Pessoais ---
    nome = st.text_input("Nome do colaborador", key="nome_colaborador")
    setor = st.text_input("Setor", key="setor_colaborador")
    cargo = st.text_input("Cargo", key="cargo_colaborador")
    cursos = st.text_area("Cursos obrigatórios ou diferenciais", key="cursos_colaborador")
    objetivo = st.text_area("Trabalho e principal objetivo", key="objetivo_colaborador")

    # --- Legenda de Frequência ---
    st.markdown("---")
    st.info("""
    **📋 LEGENDA DE FREQUÊNCIA (O que significa cada letra):**
    * **DVD**: Diário Várias Vezes | **D**: Diário | **S**: Semanal
    * **Q**: Quinzenal | **M**: Mensal | **T**: Trimestral | **A**: Anual
    """)

    # --- Atividades ---
    st.markdown("---")
    atividades = []
    with st.expander("🔹 Atividades Executadas", expanded=True):
        for i in range(20):
            col1, col2, col3, col4 = st.columns([4,2,1,1])
            with col1:
                atv = st.text_input(f"Atividade {i+1}", key=f"ativ_{i}")
            with col2:
                freq = st.selectbox("Frequência", lista_frequencia, key=f"freq_{i}")
            with col3:
                hrs = st.selectbox("Horas", lista_horas, key=f"hrs_{i}")
            with col4:
                mins = st.selectbox("Minutos", lista_minutos, key=f"mins_{i}")
            atividades.append({"Atividade": atv, "Frequência": freq, "Horas": hrs, "Minutos": mins})

    # --- Dificuldades ---
    st.markdown("---")
    dificuldades = []
    with st.expander("⚠️ Dificuldades e Bloqueios", expanded=False):
        for i in range(20):
            col1, col2, col3 = st.columns([4,3,1])
            with col1:
                dif = st.text_input(f"Dificuldade {i+1}", key=f"dif_{i}")
            with col2:
                setor_parceiro = st.text_input(f"Setor/Parceiro {i+1}", key=f"setor_parceiro_{i}")
            with col3:
                tempo = st.selectbox("Tempo Perdido (min)", lista_minutos, key=f"tempo_{i}")
            dificuldades.append({"Dificuldade": dif, "Setor/Parceiro": setor_parceiro, "Tempo Perdido": tempo})

    # --- Sugestões ---
    st.markdown("---")
    sugestoes = []
    with st.expander("💡 Sugestões de Melhoria", expanded=False):
        for i in range(20):
            col1, col2 = st.columns([4,2])
            with col1:
                sug = st.text_input(f"Sugestão {i+1}", key=f"sug_{i}")
            with col2:
                impacto = st.selectbox("Impacto Esperado", impacto_esperado, key=f"impacto_{i}")
            sugestoes.append({"Sugestão": sug, "Impacto Esperado": impacto})

    # --- Botão de envio ---
    enviar = st.form_submit_button("🚀 ENVIAR FORMULÁRIO FINAL", key="btn_enviar_form")
    if enviar:
        if not nome or not setor or not cargo:
            st.error("⚠️ Preencha Nome, Setor e Cargo!")
        else:
            # Salvar dados em JSON
            os.makedirs(dados_dir, exist_ok=True)
            dados = {
                "Nome": nome,
                "Setor": setor,
                "Cargo": cargo,
                "Cursos": cursos,
                "Objetivo": objetivo,
                "Atividades": atividades,
                "Dificuldades": dificuldades,
                "Sugestoes": sugestoes,
                "DataEnvio": pd.Timestamp.now().strftime("%d/%m/%Y %H:%M")
            }
            nome_limpo = nome.strip().replace(" ", "_") if nome else "sem_nome"
            caminho = os.path.join(dados_dir, f"{nome_limpo}_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.json")
            with open(caminho, "w", encoding="utf-8") as f:
                json.dump(dados, f, ensure_ascii=False, indent=4)
            st.success("✅ Formulário enviado e salvo com sucesso!")

# ============================================================
# PARTE 4: VISUALIZAÇÃO DE FORMULÁRIOS E DISC
# ============================================================

import pandas as pd
import streamlit as st
import os
import json

# Define a pasta de dados
dados_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dados")

# Função para carregar todos os formulários JSON
def carregar_todos_formularios():
    lista_formularios = []
    if os.path.exists(dados_dir):
        for arquivo in os.listdir(dados_dir):
            if arquivo.endswith(".json"):
                caminho = os.path.join(dados_dir, arquivo)
                try:
                    with open(caminho, "r", encoding="utf-8") as f:
                        dados = json.load(f)
                        if isinstance(dados, dict):
                            lista_formularios.append(dados)
                except Exception:
                    continue
    return lista_formularios

# ============================================================
# VISUALIZAÇÃO
# ============================================================

if st.session_state.get("pagina") == "visualizar":
    st.title("👁️ Visualização de Formulários")

    # 1️⃣ Carrega formulários do disco
    lista_formularios = carregar_todos_formularios()

    if not lista_formularios:
        st.warning("⚠️ Nenhum formulário encontrado.")
    else:
        st.success(f"Foram encontrados {len(lista_formularios)} formulários.")

        # 2️⃣ Exibição individual
        for idx, form in enumerate(lista_formularios, 1):
            nome_exibir = str(form.get("Nome", f"Colaborador {idx}")).upper()
            data_envio = form.get("DataEnvio", "Sem Data")

            with st.expander(f"👤 {nome_exibir} — {data_envio}", expanded=False):
                # Informações básicas
                st.subheader("📝 Informações do Colaborador")
                col1, col2 = st.columns(2)
                col1.write(f"**Setor:** {form.get('Setor', 'N/A')}")
                col2.write(f"**Cargo:** {form.get('Cargo', 'N/A')}")
                st.write(f"**Cursos:** {form.get('Cursos', 'N/A')}")
                st.info(f"**Objetivo:** {form.get('Objetivo', 'N/A')}")

                # Atividades
                st.markdown("---")
                st.subheader("📋 Atividades Executadas")
                df_ativ = pd.DataFrame(form.get("Atividades", []))
                if not df_ativ.empty:
                    st.table(df_ativ)
                else:
                    st.write("Nenhuma atividade preenchida.")

                # Dificuldades
                st.markdown("---")
                st.subheader("⚠️ Dificuldades e Bloqueios")
                df_dif = pd.DataFrame(form.get("Dificuldades", []))
                if not df_dif.empty:
                    st.table(df_dif)
                else:
                    st.write("Nenhuma dificuldade registrada.")

                # Sugestões
                st.markdown("---")
                st.subheader("💡 Sugestões de Melhoria")
                df_sug = pd.DataFrame(form.get("Sugestoes", []))
                if not df_sug.empty:
                    st.table(df_sug)
                else:
                    st.write("Nenhuma sugestão registrada.")

                # Questionário DISC
                st.markdown("---")
                st.subheader("📊 Avaliação DISC")
                respostas_disc = form.get("disc", {})
                if respostas_disc:
                    for i, pergunta in enumerate(perguntas_disc, 1):
                        resposta = respostas_disc.get(f"Q{i}", "Não respondido")
                        st.write(f"**{i}. {pergunta}**")
                        st.info(f"Resposta: {resposta}")
                else:
                    st.write("Questionário DISC não preenchido.")

        # ============================================================
        # BOTÃO DE LIMPEZA
        # ============================================================
        st.markdown("---")
        if st.button("🗑️ LIMPAR TODOS OS FORMULÁRIOS", key="limpar_formularios"):
            for arquivo in os.listdir(dados_dir):
                if arquivo.endswith(".json"):
                    os.remove(os.path.join(dados_dir, arquivo))
            st.success("✅ Todos os formulários foram removidos!")
            st.session_state["formularios"] = []
            st.experimental_rerun()

# ============================================================
# PARTE 5: MENU DE NAVEGAÇÃO E CONTROLE DE PÁGINAS
# ============================================================

import streamlit as st

# Inicializa estado da sessão se não existir
if "pagina" not in st.session_state:
    st.session_state["pagina"] = "home"
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "formularios" not in st.session_state:
    st.session_state["formularios"] = []

# ============================================================
# SIDEBAR DE NAVEGAÇÃO
# ============================================================

st.sidebar.title("📌 Menu de Navegação")

if st.session_state.logged_in:
    if st.sidebar.button("🏠 Home", key="btn_home"):
        st.session_state["pagina"] = "home"
    if st.sidebar.button("📋 Formulário", key="btn_formulario"):
        st.session_state["pagina"] = "formulario"
    if st.sidebar.button("👁️ Visualizar", key="btn_visualizar"):
        st.session_state["pagina"] = "visualizar"
    if st.sidebar.button("📊 Análise Inteligente", key="btn_analise"):
        st.session_state["pagina"] = "analise"
    if st.sidebar.button("🚪 Logout", key="btn_logout"):
        st.session_state["logged_in"] = False
        st.session_state["pagina"] = "home"

# ============================================================
# REDIRECIONAMENTO DE PÁGINAS
# ============================================================

pagina = st.session_state.get("pagina", "home")

if not st.session_state.logged_in:
    st.title("🔐 Acesso Restrito")
    usuario = st.text_input("Usuário", key="login_usuario")
    senha = st.text_input("Senha", key="login_senha", type="password")
    if st.button("Entrar", key="login_entrar"):
        # Senhas de exemplo
        if (usuario == "admin" and senha == "admin123") or (usuario == "Luciano" and senha == "123"):
            st.session_state.logged_in = True
            st.success(f"✅ Bem-vindo, {usuario}!")
            st.experimental_rerun()
        else:
            st.error("❌ Usuário ou senha incorretos")
    st.stop()  # Bloqueia acesso até login

# ============================================================
# PÁGINAS PRINCIPAIS
# ============================================================

if pagina == "home":
    st.title("🏠 Home")
    st.write("Bem-vindo ao Sistema de Análise de Tarefas.")

elif pagina == "formulario":
    # Aqui você deve importar ou chamar a Parte 3 (formulário completo)
    # Exemplo: importar formulario_parte3
    st.title("📋 Formulário do Colaborador")
    # Chama função/formulário da Parte 3
    # formulario_completo()  # Função que você colocou na Parte 3

elif pagina == "visualizar":
    # Chama função de visualização (Parte 4)
    st.title("👁️ Visualizar Formulários")
    # visualizar_formularios()  # Função da Parte 4

elif pagina == "analise":
    st.title("📊 Análise Inteligente")
    st.write("Aqui serão exibidas análises corporativas, scores e pareceres estratégicos.")
    # Você pode chamar a função gerar_analise_corporativa() da Parte 3/Parte 2

# ============================================================
# PARTE 6: ANÁLISE CORPORATIVA E PARECER ESTRATÉGICO
# ============================================================

import streamlit as st
import pandas as pd
import json
import os

# Chama a função gerar_analise_corporativa() da Parte 3
# Essa função retorna o parecer (texto) e indicadores (dict)

if st.session_state.get("pagina") == "analise":
    st.title("📊 Análise Inteligente do Colaborador")

    # Seleção de colaborador para análise
    lista_formularios = carregar_todos_formularios()
    if not lista_formularios:
        st.warning("⚠️ Nenhum formulário encontrado para análise.")
    else:
        nomes_colaboradores = [f.get("Nome", f"Colaborador {i+1}") for i, f in enumerate(lista_formularios)]
        colaborador_selecionado = st.selectbox("Selecione o colaborador para análise", nomes_colaboradores, key="analise_colab")

        # Buscar dados completos do colaborador selecionado
        dados_colab = next((f for f in lista_formularios if f.get("Nome") == colaborador_selecionado), None)

        if dados_colab:
            st.subheader(f"📋 Dados do colaborador: {colaborador_selecionado}")

            # Mostra resumo rápido
            st.write("Setor:", dados_colab.get("Setor","N/A"))
            st.write("Cargo:", dados_colab.get("Cargo","N/A"))

            # Gera análise completa (Parecer + Indicadores)
            parecer, indicadores = gerar_analise_corporativa(dados_colab)

            st.markdown("---")
            st.subheader("📑 Parecer Estratégico")
            st.text_area("Parecer completo", parecer, height=300, key="parecer_text")

            st.markdown("---")
            st.subheader("📊 Indicadores")
            for chave, valor in indicadores.items():
                st.write(f"**{chave.replace('_',' ').title()}:** {valor}")

            # Botão para gerar PDF do parecer
            if st.button("📄 Gerar PDF do Parecer", key="btn_pdf_parecer"):
                nome_colab_limpo = colaborador_selecionado.replace(" ", "_")
                arquivo_pdf = gerar_pdf(parecer, nome_colab_limpo)
                st.success(f"✅ PDF gerado: {arquivo_pdf}")
                st.markdown(f"[⬇️ Baixar PDF]({arquivo_pdf})")

        else:
            st.error("❌ Não foi possível encontrar os dados do colaborador selecionado.")

# ============================================================
# PARTE 7: FUNÇÕES DE APOIO FINAL
# ============================================================

import json
from statistics import mean

# ============================================================
# CALCULAR DISC PERCENTUAL E DOMINANTE
# ============================================================

def calcular_disc(respostas_disc):
    """
    Calcula percentuais e dominante a partir das respostas DISC.
    respostas_disc: dict {pergunta: resposta ("D"/"I"/"S"/"C")}
    """
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
    """
    Recebe dicionário com contagem DISC e retorna score ponderado.
    """
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
    """
    Recebe lista de atividades (dict) e calcula carga horária semanal.
    """
    total_min = 0
    for at in atividades:
        try:
            tempo = float(at.get("Minutos",0)) + float(at.get("Horas",0))*60
        except:
            tempo = 0
        freq = at.get("Frequência","D").upper()
        # Ajuste simplificado: multiplicador por frequência
        if freq in ["D","DVD"]:
            total_min += tempo*5
        elif freq == "M":
            total_min += tempo/4
        else:
            total_min += tempo
    horas = total_min/60
    status = "Adequado"
    if horas > 44: status = "Sobrecarga"
    elif horas < 30: status = "Subutilização"
    return round(horas,2), status

# ============================================================
# GERAR ATIVIDADES IDEAIS (SIMULADAS OU GPT)
# ============================================================

def gerar_atividades_ideais(cargo, setor, client=None):
    """
    Retorna lista de 12 atividades ideais para cargo/setor.
    Se client=None, retorna atividades de exemplo.
    """
    if client is None:
        return [{
            "nome_atividade":"Atividade de exemplo",
            "descricao":"Descrição de exemplo",
            "frequencia_ideal":"semanal",
            "tempo_medio_minutos":60,
            "justificativa_tecnica":"Exemplo"
        }]*12

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
    Retorne SOMENTE JSON válido.
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
            "nome_atividade":"Atividade de exemplo",
            "descricao":"Descrição de exemplo",
            "frequencia_ideal":"semanal",
            "tempo_medio_minutos":60,
            "justificativa_tecnica":"Exemplo"
        }]*12

# ============================================================
# COMPARAÇÃO SEMÂNTICA
# ============================================================

def comparar_semanticamente(reais, ideais, client=None):
    """
    Retorna score de aderência, gap percentual médio e atividades com desvio.
    """
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
    """
    Classifica semanticamente dificuldades em categorias.
    """
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
    """
    Calcula índice final considerando aderência, DISC e carga horária.
    """
    fator_carga = 100
    if status_carga == "Sobrecarga": fator_carga = 70
    elif status_carga == "Subutilização": fator_carga = 75
    return round(mean([score_aderencia, score_disc, fator_carga]),2)

# ============================================================
# PARTE 8: FUNÇÃO MESTRE DE ANÁLISE E INTEGRAÇÃO
# ============================================================

import os
import json
import pandas as pd
import streamlit as st

def processar_formulario_completo(formulario, client=None, salvar_pdf=True):
    """
    Recebe um formulário preenchido e executa todo o fluxo:
    1. Calcula DISC e identifica dominante
    2. Calcula carga horária
    3. Gera atividades ideais
    4. Compara semanticamente
    5. Classifica dificuldades
    6. Gera índice geral e classificação de risco
    7. Gera parecer estratégico (texto e PDF)
    8. Atualiza session_state e salva JSON
    """

    # ============================================================
    # 1️⃣ DISC
    respostas_disc = formulario.get("disc", {})
    percentuais_disc, dominante = calcular_disc(respostas_disc)
    score_disc_valor = score_disc(percentuais_disc)

    # ============================================================
    # 2️⃣ Carga Horária
    atividades = formulario.get("Atividades", [])
    horas_semanais, status_carga = calcular_carga(atividades)

    # ============================================================
    # 3️⃣ Atividades Ideais
    cargo = formulario.get("Cargo","N/A")
    setor = formulario.get("Setor","N/A")
    atividades_ideais = gerar_atividades_ideais(cargo, setor, client)

    # ============================================================
    # 4️⃣ Comparação Semântica
    comparacao = comparar_semanticamente(atividades, atividades_ideais, client)
    score_aderencia = comparacao.get("score_aderencia",0)

    # ============================================================
    # 5️⃣ Classificação Dificuldades
    dificuldades = formulario.get("Dificuldades",[])
    dificuldades_classificadas = classificar_dificuldades_gpt(dificuldades, client)

    # ============================================================
    # 6️⃣ Índice Geral e Risco
    indice = indice_geral(score_aderencia, score_disc_valor, status_carga)
    risco = "Baixo" if indice < 60 else "Moderado" if indice < 75 else "Alto"

    # ============================================================
    # 7️⃣ Parecer Estratégico (Texto)
    parecer = ""
    try:
        if client:
            prompt_final = f"""
            Gere parecer estratégico completo considerando:
            - Score aderência: {score_aderencia}
            - Horas semanais: {horas_semanais}
            - Status carga: {status_carga}
            - Score DISC: {score_disc_valor}
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

    # ============================================================
    # 8️⃣ Salvar JSON atualizado
    salvar_formulario_json(formulario)

    # ============================================================
    # 9️⃣ Gerar PDF se solicitado
    arquivo_pdf = None
    if salvar_pdf:
        nome_colab = formulario.get("Nome","Colaborador")
        arquivo_pdf = gerar_pdf(parecer, nome_colab)

    # ============================================================
    #  🔟 Atualizar indicadores no session_state
    indicadores = {
        "score_aderencia": score_aderencia,
        "horas_semanais": horas_semanais,
        "status_carga": status_carga,
        "score_disc": score_disc_valor,
        "percentuais_disc": percentuais_disc,
        "dominante_disc": dominante,
        "indice_geral": indice,
        "risco": risco,
        "arquivo_pdf": arquivo_pdf
    }
    st.session_state["ultimo_indicador"] = indicadores

    return parecer, indicadores, arquivo_pdf

# ============================================================
# PARTE 9: INTERFACE STREAMLIT PARA PROCESSAR E VISUALIZAR FORMULÁRIOS
# ============================================================

import streamlit as st
import pandas as pd
import os

st.title("📋 Sistema de Análise de Colaboradores")

# 1️⃣ Se estiver na página de formulário
if st.session_state.get("pagina") == "formulario":

    st.subheader("Formulário Colaborador")

    # Dados Pessoais
    nome = st.text_input("Nome do colaborador")
    setor = st.text_input("Setor")
    cargo = st.text_input("Cargo")
    cursos = st.text_area("Cursos obrigatórios ou diferenciais")
    objetivo = st.text_area("Trabalho e principal objetivo")

    # Botão para processar
    if st.button("🚀 Processar e Gerar Análise"):

        # Validação mínima
        if not nome or not setor or not cargo:
            st.error("⚠️ Preencha Nome, Setor e Cargo!")
        else:
            # Monta o dicionário do formulário
            formulario = {
                "Nome": nome,
                "Setor": setor,
                "Cargo": cargo,
                "Cursos": cursos,
                "Objetivo": objetivo,
                "Atividades": st.session_state.get("atividades", []),
                "Dificuldades": st.session_state.get("dificuldades", []),
                "Sugestoes": st.session_state.get("sugestoes", []),
                "disc": st.session_state.get("disc", {}),
                "DataEnvio": pd.Timestamp.now().strftime("%d/%m/%Y %H:%M")
            }

            # Chama função mestre
            parecer, indicadores, arquivo_pdf = processar_formulario_completo(formulario, client=None)

            st.success("✅ Formulário processado com sucesso!")

            # Exibe indicadores
            st.subheader("📊 Indicadores do Colaborador")
            st.write(f"**Score Aderência:** {indicadores['score_aderencia']}")
            st.write(f"**Horas Semanais:** {indicadores['horas_semanais']}h")
            st.write(f"**Status Carga:** {indicadores['status_carga']}")
            st.write(f"**Score DISC:** {indicadores['score_disc']}")
            st.write(f"**Dominante DISC:** {indicadores['dominante_disc']}")
            st.write(f"**Índice Geral:** {indicadores['indice_geral']}")
            st.write(f"**Classificação de Risco:** {indicadores['risco']}")

            # Exibe parecer
            st.subheader("📝 Parecer Estratégico")
            st.text_area("Parecer Completo", parecer, height=400)

            # Botão para download PDF
            if arquivo_pdf and os.path.exists(arquivo_pdf):
                with open(arquivo_pdf, "rb") as f:
                    st.download_button(
                        label="📄 Baixar Parecer em PDF",
                        data=f,
                        file_name=os.path.basename(arquivo_pdf),
                        mime="application/pdf"
                    )

# 2️⃣ Se estiver na página de visualização
elif st.session_state.get("pagina") == "visualizar":
    st.title("👁️ Visualização de Formulários Registrados")

    lista_formularios = carregar_todos_formularios()

    if not lista_formularios:
        st.warning("⚠️ Nenhum formulário encontrado.")
    else:
        st.success(f"Foram encontrados {len(lista_formularios)} formulários.")

        for idx, form in enumerate(lista_formularios, 1):
            nome_exibir = form.get("Nome", f"Colaborador {idx}")
            with st.expander(f"👤 {nome_exibir} ({form.get('DataEnvio','Sem Data')})"):

                # Dados pessoais
                st.subheader("📝 Informações Pessoais")
                st.write(f"Setor: {form.get('Setor','N/A')}")
                st.write(f"Cargo: {form.get('Cargo','N/A')}")
                st.write(f"Cursos: {form.get('Cursos','N/A')}")
                st.write(f"Objetivo: {form.get('Objetivo','N/A')}")

                # Seções dinâmicas
                for chave, titulo in [("Atividades","📋 Atividades"), ("Dificuldades","⚠️ Dificuldades"), ("Sugestoes","💡 Sugestões")]:
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

                # Parecer DISC se disponível
                st.markdown("---")
                st.subheader("📊 Avaliação DISC")
                disc = form.get("disc", {})
                percentuais, dominante = calcular_disc(disc)
                st.write(f"Percentuais DISC: {percentuais}")
                st.write(f"Dominante DISC: {dominante}")

# ============================================================
# PARTE 10: FORMULÁRIO DETALHADO COM EXPANDERS
# ============================================================

if st.session_state.get("pagina") == "formulario":
    st.title("📋 Formulário Completo do Colaborador")

    # --- Dados Pessoais ---
    nome = st.text_input("Nome do colaborador", key="nome")
    setor = st.text_input("Setor", key="setor")
    cargo = st.text_input("Cargo", key="cargo")
    cursos = st.text_area("Cursos obrigatórios ou diferenciais", key="cursos")
    objetivo = st.text_area("Trabalho e principal objetivo", key="objetivo")

    # --- Legenda de Frequência ---
    st.markdown("---")
    st.info("""
    **📋 LEGENDA DE FREQUÊNCIA (O que significa cada letra):**
    * **DVD**: Diário Várias Vezes | **D**: Diário | **S**: Semanal
    * **Q**: Quinzenal | **M**: Mensal | **T**: Trimestral | **A**: Anual
    """)

    # --- Atividades Executadas ---
    st.markdown("---")
    atividades = []
    with st.expander("🔹 Atividades Executadas", expanded=True):
        for i in range(20):
            col1, col2, col3, col4 = st.columns([4,2,1,1])
            with col1:
                atv = st.text_input(f"Atividade {i+1}", key=f"ativ_{i}")
            with col2:
                freq = st.selectbox("Frequência", lista_frequencia, key=f"freq_{i}")
            with col3:
                hrs = st.selectbox("Horas", lista_horas, key=f"hrs_{i}")
            with col4:
                mins = st.selectbox("Minutos", lista_minutos, key=f"mins_{i}")
            atividades.append({"Atividade": atv, "Frequência": freq, "Horas": hrs, "Minutos": mins})
    st.session_state["atividades"] = atividades

    # --- Dificuldades e Bloqueios ---
    st.markdown("---")
    dificuldades = []
    with st.expander("⚠️ Dificuldades e Bloqueios", expanded=False):
        for i in range(20):
            col1, col2, col3 = st.columns([4,3,1])
            with col1:
                dif = st.text_input(f"Dificuldade {i+1}", key=f"dif_{i}")
            with col2:
                setor_parceiro = st.text_input(f"Setor/Parceiro {i+1}", key=f"setor_{i}")
            with col3:
                tempo = st.selectbox("Tempo Perdido (min)", lista_minutos, key=f"tempo_{i}")
            dificuldades.append({"Dificuldade": dif, "Setor/Parceiro": setor_parceiro, "Tempo Perdido": tempo})
    st.session_state["dificuldades"] = dificuldades

    # --- Sugestões de Melhoria ---
    st.markdown("---")
    sugestoes = []
    with st.expander("💡 Sugestões de Melhoria", expanded=False):
        for i in range(20):
            col1, col2 = st.columns([4,2])
            with col1:
                sug = st.text_input(f"Sugestão {i+1}", key=f"sug_{i}")
            with col2:
                impacto = st.selectbox("Impacto Esperado", impacto_esperado, key=f"impacto_{i}")
            sugestoes.append({"Sugestão": sug, "Impacto Esperado": impacto})
    st.session_state["sugestoes"] = sugestoes

    # --- Botão de envio do formulário ---
    st.markdown("---")
    if st.button("🚀 ENVIAR FORMULÁRIO FINAL", key="btn_enviar_final"):
        if not nome or not setor or not cargo:
            st.error("⚠️ Preencha Nome, Setor e Cargo!")
        else:
            formulario = {
                "Nome": nome,
                "Setor": setor,
                "Cargo": cargo,
                "Cursos": cursos,
                "Objetivo": objetivo,
                "Atividades": st.session_state.get("atividades", []),
                "Dificuldades": st.session_state.get("dificuldades", []),
                "Sugestoes": st.session_state.get("sugestoes", []),
                "disc": st.session_state.get("disc", {}),
                "DataEnvio": pd.Timestamp.now().strftime("%d/%m/%Y %H:%M")
            }
            salvar_formulario_json(formulario)
            st.success("✅ Formulário enviado e salvo com sucesso!")

# ============================================================
# PARTE 11: VISUALIZAÇÃO COMPLETA E DOWNLOAD
# ============================================================
<<<<<<< HEAD

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
=======
>>>>>>> 701e479 (Atualização: formulário completo, motor de análise e PDF)

if st.session_state.get("pagina") == "visualizar":
    st.title("👁️ Visualização de Registros de Colaboradores")

    # 1️⃣ Carrega formulários mais recentes do disco
    lista_de_arquivos = carregar_todos_formularios()

    if not lista_de_arquivos:
        st.warning("⚠️ Nenhum formulário encontrado.")
    else:
        st.success(f"Foram encontrados {len(lista_de_arquivos)} formulários.")

        for idx, form in enumerate(lista_de_arquivos, 1):
            nome_exibir = str(form.get('Nome', f'Colaborador {idx}')).upper()
            with st.expander(f"👤 FORMULÁRIO DE: {nome_exibir} ({form.get('DataEnvio', 'Sem Data')})"):

                # --- Informações de Identificação ---
                st.subheader("📝 Informações de Identificação")
                col1, col2 = st.columns(2)
                col1.write(f"**Nome:** {form.get('Nome','N/A')}")
                col2.write(f"**Setor:** {form.get('Setor','N/A')}")
                col1.write(f"**Cargo:** {form.get('Cargo','N/A')}")
                col2.write(f"**Cursos:** {form.get('Cursos','N/A')}")
                st.info(f"**Objetivo Principal:**\n{form.get('Objetivo','N/A')}")

                # --- Atividades, Dificuldades e Sugestões ---
                secoes = {
                    "Atividades": "📋 Atividades Executadas",
                    "Dificuldades": "⚠️ Dificuldades e Bloqueios",
                    "Sugestoes": "💡 Sugestões de Melhoria"
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

                # --- Indicadores DISC, carga e análise ---
                st.markdown("---")
                st.subheader("📊 Indicadores e Análise")

                disc_percentual, disc_dominante = calcular_disc(form.get("disc", {}))
                st.write(f"**DISC Percentual:** {disc_percentual}")
                st.write(f"**Dominante:** {disc_dominante}")

                horas, status_carga = calcular_carga(form.get("Atividades", []))
                st.write(f"**Carga Horária Semanal:** {horas} h | Status: {status_carga}")

                score_disc_val = score_disc(form.get("disc", {}))
                st.write(f"**Score DISC Ponderado:** {score_disc_val}")

                # --- Botão de gerar parecer PDF ---
                st.markdown("---")
                if st.button(f"📄 Gerar PDF do Parecer - {nome_exibir}", key=f"pdf_{idx}"):
                    parecer_texto, indicadores = gerar_analise_corporativa(form)
                    arquivo_pdf = gerar_pdf(parecer_texto, nome_exibir.replace(" ", "_"))
                    st.success(f"✅ PDF gerado: {arquivo_pdf}")
                    st.download_button(
                        label="⬇️ Baixar PDF",
                        data=open(arquivo_pdf, "rb").read(),
                        file_name=arquivo_pdf,
                        mime="application/pdf"
                    )

# ============================================================
# PARTE 12: LIMPEZA, RESET E TRATAMENTO FINAL
# ============================================================

# Botão global de limpeza do banco de dados
st.sidebar.markdown("---")
if st.session_state.get("pagina") == "visualizar":
    if st.sidebar.button("🗑️ LIMPAR TODOS OS FORMULÁRIOS"):
        # Remove todos os arquivos JSON individuais
        for arquivo in os.listdir(dados_dir):
            if arquivo.endswith(".json"):
                os.remove(os.path.join(dados_dir, arquivo))
        # Limpa o JSON mestre
        if os.path.exists(json_master):
            with open(json_master, "w", encoding="utf-8") as f:
                json.dump([], f, ensure_ascii=False, indent=4)

        # Resetar session_state
        st.session_state["formularios"] = []
        st.success("✅ Banco de dados limpo com sucesso!")
        st.experimental_rerun()  # Reinicia o app para atualizar interface

# ------------------------------------------------------------
# Botão de logout
# ------------------------------------------------------------
if st.sidebar.button("🚪 Logout"):
    st.session_state.logged_in = False
    st.session_state.pagina = "home"
    st.experimental_rerun()

# ------------------------------------------------------------
# Prevenção de duplicação de widgets
# ------------------------------------------------------------
# Streamlit lança StreamlitDuplicateElementId quando há widgets
# com mesmas keys em formulários ou expanders múltiplos.
# Para evitar:
# - Sempre use keys únicas (ex.: f"ativ_{i}", f"dif_{i}", f"sug_{i}")
# - Evite múltiplos st.form_submit_button com mesma key
# - Use st.container() para agrupar e evitar conflito

# ------------------------------------------------------------
# Mensagem final de controle
# ------------------------------------------------------------
if st.session_state.get("pagina") == "home":
    st.title("🏠 Bem-vindo ao Sistema de Análise de Tarefas")
    st.write("Use o menu lateral para navegar entre Formulários, Análise e Visualização.")

<<<<<<< HEAD
    # 4. Atualiza o estado da sessão do Streamlit para refletir a mudança instantaneamente
    st.session_state["formularios"] = dados_existentes


=======
>>>>>>> 701e479 (Atualização: formulário completo, motor de análise e PDF)
