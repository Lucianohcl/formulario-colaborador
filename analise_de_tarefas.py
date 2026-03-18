import streamlit as st
import pandas as pd
import json
import base64
import requests
from datetime import datetime

# ================================
# 1. CONFIGURAÇÕES E LISTAS
# ================================
USER = st.secrets["DB_USERNAME"]
TOKEN = st.secrets["DB_TOKEN"]
REPO = "formulario-colaborador"

lista_frequencia = ["DVD", "D", "S", "Q", "M", "T", "A"]
lista_horas = [f"{i} h" for i in range(25)]
lista_minutos = [f"{i} min" for i in range(0, 60, 5)]

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

# ================================
# 2. FUNÇÕES DE COMUNICAÇÃO
# ================================
def carregar(arquivo):
    url = f"https://api.github.com/repos/{USER}/{REPO}/contents/{arquivo}"
    headers = {"Authorization": f"token {TOKEN}"}
    try:
        r = requests.get(url, headers=headers)
        if r.status_code == 200:
            data = r.json()
            conteudo = base64.b64decode(data["content"]).decode('utf-8')
            return json.loads(conteudo), data["sha"]
    except:
        pass
    return {}, None

def salvar(dados, arquivo, mensagem="Atualização"):
    url = f"https://api.github.com/repos/{USER}/{REPO}/contents/{arquivo}"
    headers = {"Authorization": f"token {TOKEN}"}
    _, sha = carregar(arquivo)
    conteudo_b64 = base64.b64encode(json.dumps(dados, indent=4, ensure_ascii=False).encode('utf-8')).decode('utf-8')
    payload = {"message": mensagem, "content": conteudo_b64, "branch": "main"}
    if sha: payload["sha"] = sha
    r = requests.put(url, headers=headers, json=payload)
    return r.status_code in [200, 201]

# ================================
# 3. INTERFACE E LÓGICA DE ACESSO
# ================================
st.set_page_config(page_title="Formulário DISC Avançado", layout="wide")
st.info("📝 Gerar Rascunho")

nome_usuario = st.text_input("Digite seu **NOME COMPLETO**")
primeira_vez = st.checkbox("É minha primeira vez (Cadastrar)")

if nome_usuario:
    nome_limpo = nome_usuario.strip().lower().replace(" ", "_")
    arquivo_nome = f"rascunho_{nome_limpo}.json"
    dados, _ = carregar(arquivo_nome)

    # ===========================
    # Carregar dados do rascunho (se existir)
    # ===========================
    if dados:
        ident = dados.get("Identificacao", {})

        nome = ident.get("Nome", "")
        setor = ident.get("Setor", "")
        cargo = ident.get("Cargo", "")
        chefe = ident.get("Chefe", "")
        departamento = ident.get("Departamento", "")
        empresa = ident.get("Empresa", "")
        escolaridade = ident.get("Escolaridade", "")
        devolucao = ident.get("Devolução preenchida em", "")

        cursos = dados.get("Cursos", "")
        objetivo = dados.get("Objetivo", "")
        atividades_alta = pd.DataFrame(dados.get("Atividades", {}).get("Alta", []))
        atividades_normal = pd.DataFrame(dados.get("Atividades", {}).get("Normal", []))
        atividades_baixa = pd.DataFrame(dados.get("Atividades", {}).get("Baixa", []))
    
    if primeira_vez:
        if dados:
            st.warning("⚠️ Usuário já cadastrado. Desmarque a opção acima para entrar.")
        else:
            if st.button("✅ Criar meu Rascunho"):
                if salvar({"nome": nome_usuario, "status": "iniciado"}, arquivo_nome):
                    st.success("Rascunho criado! Agora desmarque a caixa 'É minha primeira vez'.")
    else:
        if not dados:
            st.error("❌ Nome não encontrado. Cadastre-se primeiro.")
            st.stop()

        # --- INÍCIO DO FORMULÁRIO ---
        st.success(f"📋 Rascunho de {nome_usuario} carregado!")

        # --- CAMPOS DE IDENTIFICAÇÃO (VERSÃO COMPLETA) ---
        st.subheader("👤 Dados de Identificação")
        col1, col2 = st.columns(2)
        with col1:
            nome = st.text_input("Nome do colaborador", dados.get("nome", nome_usuario))
            cargo = st.text_input("Cargo", dados.get("cargo", ""))
            departamento = st.text_input("Departamento", dados.get("departamento", ""))
            escolaridade = st.text_input("Escolaridade", dados.get("escolaridade", ""))
        with col2:
            setor = st.text_input("Setor", dados.get("setor", ""))
            chefe = st.text_input("Chefe imediato", dados.get("chefe", ""))
            empresa = st.text_input("Empresa / Unidade", dados.get("empresa", ""))
            devolucao = st.text_input("Devolver preenchido em", dados.get("devolucao", ""))
        
        cursos = st.text_area("Cursos obrigatórios ou diferenciais", dados.get("cursos", ""))
        objetivo = st.text_area("Trabalho e principal objetivo", dados.get("objetivo", ""))

        # Lembre-se de adicionar 'escolaridade', 'devolucao', 'cursos' e 'objetivo' 
        # dentro do dicionário 'payload' no botão SALVAR lá embaixo!

        
    # ===========================
    # Tabela de Alta Complexidade
    # ===========================
    st.subheader("🔹 Atividades de Alta Complexidade")
    atividades_alta = st.data_editor(
        pd.DataFrame({
            "Atividade Descrita": [""] * 20,
            "Frequência": [""] * 20,
            "Horas": [""] * 20,
            "Minutos": [""] * 20
        }).reset_index(drop=True),
        key="form_atividades_alta",
        column_config={
            "Frequência": st.column_config.SelectboxColumn("Frequência", options=lista_frequencia),
            "Horas": st.column_config.SelectboxColumn("Horas", options=lista_horas),
            "Minutos": st.column_config.SelectboxColumn("Minutos", options=lista_minutos),
        },
        hide_index=True,
        num_rows="fixed",
        use_container_width=True
    )

    # ===========================
    # Tabela de Nível Normal
    # ===========================
    st.subheader("🔹 Atividades de Nível Normal")
    atividades_normal = st.data_editor(
        pd.DataFrame({
            "Atividade Descrita": [""] * 20,
            "Frequência": [""] * 20,
            "Horas": [""] * 20,
            "Minutos": [""] * 20
        }).reset_index(drop=True),
        key="form_atividades_normal",
        column_config={
            "Frequência": st.column_config.SelectboxColumn("Frequência", options=lista_frequencia),
            "Horas": st.column_config.SelectboxColumn("Horas", options=lista_horas),
            "Minutos": st.column_config.SelectboxColumn("Minutos", options=lista_minutos),
        },
        hide_index=True,
        num_rows="fixed",
        use_container_width=True
    )

    # ===========================
    # Tabela de Baixa Complexidade
    # ===========================
    st.subheader("🔹 Atividades de Baixa Complexidade")
    atividades_baixa = st.data_editor(
        pd.DataFrame({
            "Atividade Descrita": [""] * 20,
            "Frequência": [""] * 20,
            "Horas": [""] * 20,
            "Minutos": [""] * 20
        }).reset_index(drop=True),
        key="form_atividades_baixa",
        column_config={
            "Frequência": st.column_config.SelectboxColumn("Frequência", options=lista_frequencia),
            "Horas": st.column_config.SelectboxColumn("Horas", options=lista_horas),
            "Minutos": st.column_config.SelectboxColumn("Minutos", options=lista_minutos),
        },
        hide_index=True,
        num_rows="fixed",
        use_container_width=True
    )

    # 3. TABELA DIFICULDADES
    st.markdown("---")
    st.subheader("⚠️ Dificuldades e Bloqueios")
    df_dif_padrao = pd.DataFrame(dados.get("dificuldades", [{"Dificuldade": "", "Setor/Parceiro Envolvido": "", "Frequência": "", "Horas Perdidas": "", "Minutos Perdidos": ""} for _ in range(10)]))
    edit_dif = st.data_editor(df_dif_padrao, column_config={
        "Frequência": st.column_config.SelectboxColumn(options=lista_frequencia),
        "Horas Perdidas": st.column_config.SelectboxColumn(options=lista_horas),
        "Minutos Perdidos": st.column_config.SelectboxColumn(options=lista_minutos),
    }, hide_index=True, use_container_width=True, key="dif_ed")

    # 4. TABELA SUGESTÕES
    st.markdown("---")
    st.subheader("💡 Sugestões de Melhoria")
    df_sug_padrao = pd.DataFrame(dados.get("sugestoes", [{"Sugestão de Melhoria": "", "Impacto Esperado": "", "Redução Horas": "", "Redução Minutos": "", "Frequência do Impacto": ""} for _ in range(10)]))
    edit_sug = st.data_editor(df_sug_padrao, column_config={
        "Redução Horas": st.column_config.SelectboxColumn(options=lista_horas),
        "Redução Minutos": st.column_config.SelectboxColumn(options=lista_minutos),
        "Frequência do Impacto": st.column_config.SelectboxColumn(options=lista_frequencia),
    }, hide_index=True, use_container_width=True, key="sug_ed")

    # 5. QUESTIONÁRIO DISC
    st.markdown("---")
    st.subheader("📊 Questionário")
    respostas_disc = {}
    for i, pergunta in enumerate(perguntas_disc, 1):
        chave = f"disc_{i}"
        respostas_disc[chave] = st.radio(
            f"{i}. {pergunta}", 
            ["A", "B", "C", "D"], 
            index=["A", "B", "C", "D"].index(dados.get(chave)) if dados.get(chave) in ["A", "B", "C", "D"] else None,
            horizontal=True, 
            key=f"radio_{i}"
        )

    # 6. BOTÃO SALVAR
    st.markdown("---")
    if st.button("💾 Salvar Rascunho"):
        payload = {
            "nome": nome, 
            "cargo": cargo, 
            "departamento": depto,
            "setor": setor, 
            "chefe": chefe, 
            "empresa": empresa,
            "atividades": edit_ativ.to_dict("records"),
            "dificuldades": edit_dif.to_dict("records"),
            "sugestoes": edit_sug.to_dict("records"),
            **respostas_disc,
            "ultima_atualizacao": datetime.now().strftime("%d/%m/%Y %H:%M")
        }
        if salvar(payload, arquivo_nome):
            st.success("✅ Rascunho salvo com sucesso no servidor!")
            st.rerun()
        else:
            st.error("❌ Falha ao salvar. Verifique sua conexão.")  
