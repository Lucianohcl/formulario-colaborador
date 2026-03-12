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

# ============================================================

# CONFIGURAÇÃO E INICIALIZAÇÃO ÚNICA

# ============================================================

st.set_page_config(

page_title=&quot;Sistema de Análise de Tarefas&quot;,

page_icon=&quot;  &quot;,

layout=&quot;wide&quot;,

initial_sidebar_state=&quot;expanded&quot;

)

# Inicialização centralizada

if &quot;logged_in&quot; not in st.session_state: st.session_state.logged_in = False

if &quot;pagina&quot; not in st.session_state: st.session_state.pagina = &quot;home&quot;

if &quot;formularios&quot; not in st.session_state: st.session_state[&quot;formularios&quot;] = []

# Leitura da URL (Prioridade total para permitir acesso ao formulário)

query_params = st.query_params

if &quot;page&quot; in query_params:

st.session_state.pagina = query_params[&quot;page&quot;]

# --- DEFINIÇÃO E CARREGAMENTO DO BANCO DE DADOS ---
JSON_MASTER = &quot;formularios.json&quot;
BASE_DIR = &quot;dados&quot;
if not os.path.exists(BASE_DIR): os.makedirs(BASE_DIR)

# Função para garantir que os dados carregados sejam sempre uma lista de dicionários
def carregar_dados_seguro():
caminho = os.path.join(BASE_DIR, JSON_MASTER) if not os.path.exists(JSON_MASTER) else
JSON_MASTER
if os.path.exists(caminho):
try:
with open(caminho, &quot;r&quot;, encoding=&quot;utf-8&quot;) as f:
dados = json.load(f)
# O segredo: Filtra tudo que não for dicionário
return [d for d in dados if isinstance(d, dict)] if isinstance(dados, list) else []
except:
return []
return []

# Inicializa o session_state com os dados já limpos
if &quot;formularios&quot; not in st.session_state:
st.session_state[&quot;formularios&quot;] = carregar_dados_seguro()

# ============================================================
# LOGIN (Com Bypass para o Formulário)
# ============================================================
# Só bloqueia o acesso se NÃO estiver logado E NÃO for a página de formulário
if not st.session_state.logged_in and st.session_state.pagina != &quot;formulario&quot;:
st.title(&quot;   Acesso&quot;)
usuario = st.text_input(&quot;Usuário&quot;)
senha = st.text_input(&quot;Senha&quot;, type=&quot;password&quot;)

if st.button(&quot;Entrar&quot;, key=&quot;login_button&quot;):
if (usuario == &quot;admin&quot; and senha == &quot;admin123&quot;) or (usuario == &quot;Luciano&quot; and senha ==
&quot;123&quot;):
st.session_state.logged_in = True
st.session_state.user_nome = usuario

st.session_state.is_admin = True
st.rerun()
else:
st.error(&quot;Usuário ou senha incorretos&quot;)

st.stop() # Bloqueia apenas acessos não autorizados

# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title(&quot;   Menu de Navegação&quot;)

btn_home = st.sidebar.button(&quot;   Home&quot;)
btn_analise = st.sidebar.button(&quot;   Análise Inteligente&quot;)
btn_comparar = st.sidebar.button(&quot;⚖️ Comparar Colaboradores&quot;)
btn_disc = st.sidebar.button(&quot;   Perfil DISC&quot;)
btn_parecer = st.sidebar.button(&quot;   Parecer Estratégico&quot;)
btn_visualizar = st.sidebar.button(&quot;  ️ Visualizar Dados&quot;)
btn_produtividade = st.sidebar.button(&quot;   Produtividade&quot;)

st.sidebar.markdown(&quot;---&quot;)

btn_logout = st.sidebar.button(&quot;   Logout&quot;)

pagina_anterior = st.session_state.pagina

if btn_home:
st.session_state.pagina = &quot;home&quot;
elif btn_analise:

st.session_state.pagina = &quot;analise&quot;
elif btn_comparar:
st.session_state.pagina = &quot;comparar&quot;
elif btn_disc:
st.session_state.pagina = &quot;disc&quot;
elif btn_parecer:
st.session_state.pagina = &quot;parecer&quot;
elif btn_visualizar:
st.session_state.pagina = &quot;visualizar&quot;
# O elif abaixo verifica a URL sem precisar de botão
elif st.session_state.pagina == &quot;formulario&quot;:
pass # Este comando é obrigatório para não dar erro de sintaxe
elif btn_logout:
st.session_state.logged_in = False
st.session_state.pagina = &quot;home&quot;

if pagina_anterior != st.session_state.pagina:
st.rerun()

# ============================================================
# FORMULÁRIO COMPLETO PARA COLABORADOR (JSON VERSION)
# ============================================================
import streamlit as st
import pandas as pd
import os
import json

# Configuração da página

st.set_page_config(
page_title=&quot;Formulário do Colaborador&quot;,

page_icon=&quot;  &quot;,
layout=&quot;wide&quot;,
initial_sidebar_state=&quot;collapsed&quot;
)

# --- BLOCO ÚNICO DE CSS PARA OCULTAÇÃO ---
if st.query_params.get(&quot;page&quot;) == &quot;formulario&quot;:
st.markdown(&quot;&quot;&quot;
&lt;style&gt;
/* Esconde a Sidebar inteira */
[data-testid=&quot;stSidebar&quot;] {display: none !important;}

/* Esconde o menu do topo, rodapé e header */
#MainMenu, footer, header {visibility: hidden !important;}
&lt;/style&gt;
&quot;&quot;&quot;, unsafe_allow_html=True)
# ----------------------------------------

# --- LISTA DE PERGUNTAS DISC ---
perguntas_disc = [
&quot;Quando surge um problema inesperado: (A) Age rápido | (B) Comunica a todos | (C) Analisa
riscos | (D) Segue processo&quot;,
&quot;Em situações de pressão: (A) Foca no resultado | (B) Mantém o otimismo | (C) Mantém a
calma | (D) Busca precisão&quot;,
&quot;Ao receber tarefa difícil: (A) Aceita o desafio | (B) Busca ajuda social | (C) Planeja passos |
(D) Estuda as regras&quot;,
&quot;No trabalho em equipe: (A) Lidera o grupo | (B) Motiva os colegas | (C) Apoia os outros |
(D) Organiza as tarefas&quot;,
&quot;Em reuniões: (A) Vai direto ao ponto | (B) Interage e brinca | (C) Escuta mais | (D) Anota
detalhes&quot;,
&quot;Ao lidar com conflitos: (A) Enfrenta direto | (B) Tenta apaziguar | (C) Evita o confronto | (D)
Usa lógica e fatos&quot;,
&quot;Seu ritmo de trabalho: (A) Rápido/Impaciente | (B) Rápido/Entusiasmado | (C)
Calmo/Constante | (D) Metódico/Cauteloso&quot;,

&quot;Prefere tarefas: (A) Desafiadoras | (B) Variadas e sociais | (C) Rotineiras e seguras | (D)
Técnicas e detalhadas&quot;,
&quot;Seu foco principal: (A) Resultados | (B) Relacionamentos | (C) Estabilidade | (D) Qualidade e
Processos&quot;,
&quot;Ao decidir, você é: (A) Decidido e firme | (B) Impulsivo e intuitivo | (C) Cuidadoso e lento |
(D) Lógico e analítico&quot;,
&quot;Confia mais em: (A) Sua intuição | (B) Opinião alheia | (C) Experiência passada | (D) Dados e
provas&quot;,
&quot;Prefere decisões: (A) Independentes | (B) Em grupo | (C) Consensuais | (D) Baseadas em
normas&quot;,
&quot;Estilo de organização: (A) Prático | (B) Criativo/Bagunçado | (C) Tradicional | (D) Muito
organizado&quot;,
&quot;Lida melhor com: (A) Mudanças rápidas | (B) Novas ideias | (C) Rotinas claras | (D) Regras
rígidas&quot;,
&quot;Prefere trabalhar: (A) Sozinho/Comando | (B) Ambiente festivo | (C) Ambiente tranquilo |
(D) Ambiente silencioso&quot;,
&quot;Seu ponto forte: (A) Coragem | (B) Comunicação | (C) Paciência | (D) Organização&quot;,
&quot;Você se considera: (A) Dominante | (B) Influente | (C) Estável | (D) Conforme/Analítico&quot;,
&quot;Se motiva por: (A) Poder/Bônus | (B) Reconhecimento | (C) Segurança/Paz | (D)
Conhecimento Técnico&quot;,
&quot;Reação a cobranças: (A) Mais esforço | (B) Desculpas criativas | (C) Ansiedade | (D)
Argumentos técnicos&quot;,
&quot;Ambiente ideal: (A) Competitivo | (B) Amigável | (C) Previsível | (D) Disciplinado&quot;,
&quot;Ao lidar com feedback: (A) Aceita e ajusta | (B) Comenta e debate | (C) Analisa e planeja |
(D) Segue regras&quot;,
&quot;Como prefere aprender: (A) Fazendo | (B) Interagindo | (C) Observando | (D) Estudando
materiais&quot;,
&quot;Gestão de tempo: (A) Prioriza resultados | (B) Mantém relações | (C) Planeja com cuidado |
(D) Segue processos&quot;,
&quot;Como se comunica: (A) Direto e objetivo | (B) Amigável e motivador | (C) Calmo e
ponderado | (D) Técnico e detalhista&quot;
]

# Detectar modo formulário
modo_formulario = st.query_params.get(&quot;page&quot;) == &quot;formulario&quot;

if modo_formulario:
st.title(&quot;   Formulário Completo do Colaborador&quot;)

# --- IDENTIFICAÇÃO ---
nome = st.text_input(&quot;Nome do colaborador&quot;)
setor = st.text_input(&quot;Setor&quot;)
cargo = st.text_input(&quot;Cargo&quot;)
chefe = st.text_input(&quot;Chefe imediato&quot;)
departamento = st.text_input(&quot;Departamento&quot;)
empresa = st.text_input(&quot;Empresa / Unidade&quot;)
escolaridade = st.text_input(&quot;Escolaridade&quot;)
devolucao = st.text_input(&quot;Devolver preenchido em&quot;)
cursos = st.text_area(&quot;Cursos obrigatórios ou diferenciais&quot;)
objetivo = st.text_area(&quot;Trabalho e principal objetivo&quot;)

# --- AQUI É O LUGAR EXATO DA LEGENDA ---
st.info(&quot;&quot;&quot;
**   LEGENDA DE FREQUÊNCIA (O que significa cada letra):**
* **DVD**: Diário (Várias Vezes ao dia) | **D**: Diário | **S**: Semanal
* **Q**: Quinzenal | **M**: Mensal | **T**: Trimestral | **A**: Anual
&quot;&quot;&quot;)

# --- TABELAS ---
st.subheader(&quot;   Atividades Principais&quot;)
edit_ativ = st.data_editor(
pd.DataFrame({&quot;Descrição&quot;: [&quot;&quot;]*20, &quot;Frequência&quot;: [&quot;&quot;]*20, &quot;Tempo&quot;: [&quot;&quot;]*20}),
num_rows=&quot;fixed&quot;,
use_container_width=True,
key=&quot;editor_ativ&quot;
)

st.markdown(&quot;---&quot;)

st.subheader(&quot;   Dificuldades na Execução&quot;)
edit_dif = st.data_editor(
pd.DataFrame({&quot;Dificuldade&quot;: [&quot;&quot;]*20, &quot;Setor/Parceiro&quot;: [&quot;&quot;]*20, &quot;Tempo&quot;: [&quot;&quot;]*20}),
num_rows=&quot;fixed&quot;,
use_container_width=True,
key=&quot;editor_dif&quot;
)

st.markdown(&quot;---&quot;)

st.subheader(&quot;   Sugestões de Melhoria&quot;)
edit_sug = st.data_editor(
pd.DataFrame({&quot;Sugestão&quot;: [&quot;&quot;]*20, &quot;Impacto&quot;: [&quot;&quot;]*20}),
num_rows=&quot;fixed&quot;,
use_container_width=True,
key=&quot;editor_sug&quot;
)

# --- DISC ---
st.subheader(&quot;   Questionário DISC&quot;)
for i, pergunta in enumerate(perguntas_disc, 1):
st.radio(label=f&quot;{i}. {pergunta}&quot;, options=[&quot;A&quot;, &quot;B&quot;, &quot;C&quot;, &quot;D&quot;], key=f&quot;disc_{i}&quot;, index=None,
horizontal=True)

# --- BOTÃO DE ENVIO MINIMALISTA ---
if st.button(&quot;   ENVIAR FORMULÁRIO FINAL&quot;):
# 1. Monta o dicionário
dados = {

&quot;Nome&quot;: nome, &quot;Setor&quot;: setor, &quot;Cargo&quot;: cargo, &quot;Chefe&quot;: chefe,
&quot;Departamento&quot;: departamento, &quot;Empresa&quot;: empresa, &quot;Escolaridade&quot;: escolaridade,
&quot;Devolver&quot;: devolucao, &quot;Cursos&quot;: cursos, &quot;Objetivo&quot;: objetivo,
&quot;Atividades&quot;: edit_ativ.to_dict(orient=&quot;records&quot;) if hasattr(edit_ativ, &#39;to_dict&#39;) else [],
&quot;Dificuldades&quot;: edit_dif.to_dict(orient=&quot;records&quot;) if hasattr(edit_dif, &#39;to_dict&#39;) else [],
&quot;Sugestoes&quot;: edit_sug.to_dict(orient=&quot;records&quot;) if hasattr(edit_sug, &#39;to_dict&#39;) else []
}
for i in range(1, 25):
dados[f&quot;Q{i}&quot;] = st.session_state.get(f&quot;disc_{i}&quot;, &quot;Não respondido&quot;)
dados[&quot;DataEnvio&quot;] = pd.Timestamp.now().strftime(&quot;%d/%m/%Y %H:%M&quot;)

# 2. Salvamento Direto
try:
nome_arquivo = f&quot;{nome.strip().replace(&#39; &#39;,
&#39;_&#39;)}_{pd.Timestamp.now().strftime(&#39;%Y%m%d_%H%M%S&#39;)}.json&quot;
with open(os.path.join(&quot;dados&quot;, nome_arquivo), &quot;w&quot;, encoding=&quot;utf-8&quot;) as f:
json.dump(dados, f, ensure_ascii=False, indent=4)
st.success(&quot;✅ Enviado com sucesso!&quot;)
st.balloons()
st.rerun()
except Exception as e:
st.error(f&quot;Erro no salvamento: {e}&quot;)

# ===========================
# PÁGINA DE VISUALIZAÇÃO (ESPELHO FIEL)
# ===========================
if st.session_state.pagina == &quot;visualizar&quot;:
st.title(&quot;  ️ Espelho Fiel de Respostas&quot;)

# Pasta onde os JSONs individuais são salvos
BASE_DIR = &quot;dados&quot;

if not os.path.exists(BASE_DIR):
st.warning(&quot;⚠️ A pasta de dados ainda não existe.&quot;)
else:
arquivos = [f for f in os.listdir(BASE_DIR) if f.endswith(&quot;.json&quot;)]
arquivos.sort(reverse=True) # Exibe os mais recentes primeiro

if not arquivos:
st.warning(&quot;⚠️ Nenhum formulário preenchido ainda.&quot;)
else:
for arq in arquivos:
caminho = os.path.join(BASE_DIR, arq)
with open(caminho, &quot;r&quot;, encoding=&quot;utf-8&quot;) as f:
form = json.load(f)

nome_colaborador = form.get(&quot;Nome&quot;, &quot;Sem Nome&quot;).upper()
data_envio = form.get(&quot;DataEnvio&quot;, &quot;Data não registrada&quot;)

with st.expander(f&quot;   {nome_colaborador} | {data_envio}&quot;):
# --- Identificação ---
st.subheader(&quot;   Identificação&quot;)
col1, col2 = st.columns(2)
with col1:
st.write(f&quot;**Nome:** {form.get(&#39;Nome&#39;)}&quot;)
st.write(f&quot;**Cargo:** {form.get(&#39;Cargo&#39;)}&quot;)
st.write(f&quot;**Setor:** {form.get(&#39;Setor&#39;)}&quot;)
with col2:
st.write(f&quot;**Departamento:** {form.get(&#39;Departamento&#39;)}&quot;)
st.write(f&quot;**Empresa:** {form.get(&#39;Empresa&#39;)}&quot;)

st.write(f&quot;**Objetivo:** {form.get(&#39;Objetivo&#39;)}&quot;)

# --- Tabelas (Fiel ao preenchimento) ---
st.subheader(&quot;   Atividades Executadas&quot;)
st.table(pd.DataFrame(form.get(&quot;Atividades&quot;, [])))

st.subheader(&quot;   Dificuldades&quot;)
st.table(pd.DataFrame(form.get(&quot;Dificuldades&quot;, [])))

st.subheader(&quot;   Sugestões&quot;)
st.table(pd.DataFrame(form.get(&quot;Sugestoes&quot;, [])))

# --- DISC (Espelho Fiel das perguntas e respostas) ---
st.subheader(&quot;   Questionário DISC&quot;)
lista_exibicao = []
for i, pergunta_completa in enumerate(perguntas_disc, 1):
letra = form.get(f&quot;Q{i}&quot;, &quot;-&quot;)

# Extrai a descrição da opção selecionada
descricao = letra
if letra != &quot;-&quot; and &quot;|&quot; in pergunta_completa:
for p in pergunta_completa.split(&quot;|&quot;):
if f&quot;({letra})&quot; in p:
descricao = p.split(&quot;)&quot;)[-1].strip()
break

lista_exibicao.append({
&quot;Nº&quot;: i,
&quot;Pergunta&quot;: pergunta_completa.split(&quot;:&quot;)[0],
&quot;Resposta&quot;: f&quot;{letra} - {descricao}&quot;
})

st.table(pd.DataFrame(lista_exibicao))

# --- BOTÃO DE LIMPEZA ---
if st.button(&quot;  ️ LIMPAR TODOS OS FORMULÁRIOS&quot;, key=&quot;limpar_tudo&quot;):
for arq in arquivos:
os.remove(os.path.join(BASE_DIR, arq))
st.rerun()

# ============================================================
# CALCULAR DISC PERCENTUAL E DOMINANTE
# ============================================================

def calcular_disc(respostas_disc):
contagem = {&quot;D&quot;:0, &quot;I&quot;:0, &quot;S&quot;:0, &quot;C&quot;:0}
for r in respostas_disc.values():
if r in contagem:
contagem[r] += 1
total = sum(contagem.values())
if total &gt; 0:
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

pesos = {&quot;D&quot;:1.0,&quot;I&quot;:0.9,&quot;S&quot;:0.85,&quot;C&quot;:0.95}
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
tempo = float(at.get(&quot;tempo&quot;,&quot;0&quot;))
except:
tempo = 0
freq = at.get(&quot;frequencia&quot;,&quot;semanal&quot;).lower()
if freq == &quot;diaria&quot;:
total_min += tempo * 5
elif freq == &quot;mensal&quot;:
total_min += tempo / 4
else:
total_min += tempo
horas = total_min / 60
status = &quot;Adequado&quot;
if horas &gt; 44: status = &quot;Sobrecarga&quot;
elif horas &lt; 30: status = &quot;Subutilização&quot;
return round(horas,2), status

# ============================================================
# GERAR ATIVIDADES IDEAIS (GPT)
# ============================================================

def gerar_atividades_ideais(cargo, setor, client=None):
if client is None:
return [{
&quot;nome_atividade&quot;: &quot;Atividade de exemplo&quot;,
&quot;descricao&quot;: &quot;Descrição de exemplo&quot;,
&quot;frequencia_ideal&quot;: &quot;semanal&quot;,
&quot;tempo_medio_minutos&quot;: 60,
&quot;justificativa_tecnica&quot;: &quot;Exemplo&quot;
}]

prompt = f&quot;&quot;&quot;
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
&quot;&quot;&quot;
try:
response = client.chat.completions.create(
model=&quot;gpt-4o-mini&quot;,
messages=[{&quot;role&quot;:&quot;user&quot;,&quot;content&quot;:prompt}],
temperature=0.3

)
return json.loads(response.choices[0].message.content)
except:
return [{
&quot;nome_atividade&quot;: &quot;Atividade de exemplo&quot;,
&quot;descricao&quot;: &quot;Descrição de exemplo&quot;,
&quot;frequencia_ideal&quot;: &quot;semanal&quot;,
&quot;tempo_medio_minutos&quot;: 60,
&quot;justificativa_tecnica&quot;: &quot;Exemplo&quot;
}]

# ============================================================
# COMPARAÇÃO SEMÂNTICA
# ============================================================

def comparar_semanticamente(reais, ideais, client=None):
if client is None:
return {&quot;score_aderencia&quot;:0,&quot;tempo_gap_medio_percentual&quot;:0,&quot;atividades_desvio&quot;:[]}

prompt = f&quot;&quot;&quot;
Compare semanticamente:
Atividades reais: {reais}
Atividades ideais: {ideais}
Retorne JSON com:
- score_aderencia (0-100)
- tempo_gap_medio_percentual
- atividades_desvio
&quot;&quot;&quot;
try:
r = client.chat.completions.create(
model=&quot;gpt-4o-mini&quot;,

messages=[{&quot;role&quot;:&quot;user&quot;,&quot;content&quot;:prompt}],
temperature=0.2
)
return json.loads(r.choices[0].message.content)
except:
return {&quot;score_aderencia&quot;:0,&quot;tempo_gap_medio_percentual&quot;:0,&quot;atividades_desvio&quot;:[]}

# ============================================================
# CLASSIFICAR DIFICULDADES
# ============================================================

def classificar_dificuldades_gpt(dificuldades, client=None):
if client is None:
return {}

prompt = f&quot;&quot;&quot;
Classifique semanticamente as dificuldades abaixo em:
- Processo
- Tempo
- Comunicação
- Estrutura
- Liderança
- Sistema
Retorne JSON com contagem por categoria.
Dificuldades: {dificuldades}
&quot;&quot;&quot;
try:
r = client.chat.completions.create(
model=&quot;gpt-4o-mini&quot;,
messages=[{&quot;role&quot;:&quot;user&quot;,&quot;content&quot;:prompt}],
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
if status_carga == &quot;Sobrecarga&quot;: fator_carga = 70
elif status_carga == &quot;Subutilização&quot;: fator_carga = 75
return round(mean([score_aderencia, score_disc, fator_carga]),2)

# ============================================================
# MOTOR PRINCIPAL COMPLETO – ANÁLISE CORPORATIVA
# ============================================================

def gerar_analise_corporativa(dados, client=None):
&quot;&quot;&quot;
Gera análise completa de um colaborador com base em:
- Atividades reais
- Perfil DISC
- Dificuldades
Retorna:
- parecer (texto)
- indicadores (dict)
&quot;&quot;&quot;
# 1️⃣ Atividades ideais
ideais = gerar_atividades_ideais(dados[&quot;cargo&quot;], dados[&quot;setor&quot;], client)

# 2️⃣ Comparação semântica (reais x ideais)
comparacao = comparar_semanticamente(dados[&quot;atividades&quot;], ideais, client)

# 3️⃣ Carga horária
horas, status_carga = calcular_carga(dados[&quot;atividades&quot;])

# 4️⃣ Score DISC
disc_score = score_disc(dados[&quot;disc&quot;])

# 5️⃣ Classificação de dificuldades
dificuldades_classificadas = classificar_dificuldades_gpt(dados[&quot;dificuldades&quot;], client)

# 6️⃣ Score de aderência
score_aderencia = comparacao.get(&quot;score_aderencia&quot;,0)

# 7️⃣ Índice geral
indice = indice_geral(score_aderencia, disc_score, status_carga)

# 8️⃣ Classificação de risco
risco = &quot;Baixo&quot; if indice &lt; 60 else &quot;Moderado&quot; if indice &lt; 75 else &quot;Alto&quot;

# 9️⃣ Prompt final para parecer estratégico
prompt_final = f&quot;&quot;&quot;
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
&quot;&quot;&quot;

# 10️⃣ Obter parecer do GPT
parecer = &quot;&quot;
try:
if client:
resposta = client.chat.completions.create(
model=&quot;gpt-4o-mini&quot;,
messages=[{&quot;role&quot;:&quot;user&quot;,&quot;content&quot;:prompt_final}],
temperature=0.3
)
parecer = resposta.choices[0].message.content
else:
parecer = &quot;GPT não disponível. Retorno padrão: análise resumida.&quot;
except:
parecer = &quot;Erro ao gerar parecer com GPT.&quot;

# 11️⃣ Indicadores
indicadores = {
&quot;score_aderencia&quot;: score_aderencia,
&quot;horas_semanais&quot;: horas,

&quot;status_carga&quot;: status_carga,
&quot;score_disc&quot;: disc_score,
&quot;indice_geral&quot;: indice,
&quot;risco&quot;: risco
}

return parecer, indicadores

# ============================================================
# GERAR PDF DO PARECER
# ============================================================

def gerar_pdf(parecer, nome):
&quot;&quot;&quot;
Recebe:
- parecer (texto)
- nome do colaborador
Cria arquivo PDF pronto para download
&quot;&quot;&quot;
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch

nome_arquivo = f&quot;{nome}_parecer.pdf&quot;
doc = SimpleDocTemplate(nome_arquivo)
elements = []
styles = getSampleStyleSheet()

# Título
elements.append(Paragraph(&quot;PARECER ESTRATÉGICO ORGANIZACIONAL&quot;, styles[&quot;Title&quot;]))
elements.append(Spacer(1, 0.5*inch))

# Conteúdo linha a linha
for linha in parecer.split(&quot;\n&quot;):
if linha.strip(): # evita parágrafos vazios
elements.append(Paragraph(linha, styles[&quot;Normal&quot;]))
elements.append(Spacer(1, 0.2*inch))

doc.build(elements)
return nome_arquivo

# ============================================================
# PASTA BASE PARA FORMULÁRIOS (JSON)
os.makedirs(BASE_DIR, exist_ok=True)
JSON_MASTER = os.path.join(BASE_DIR, &quot;formularios.json&quot;)

# Inicializa arquivo JSON se não existir
if not os.path.exists(JSON_MASTER):
with open(JSON_MASTER, &quot;w&quot;, encoding=&quot;utf-8&quot;) as f:
json.dump([], f, ensure_ascii=False, indent=4)

# ============================================================
# FUNÇÃO PARA SALVAR FORMULÁRIO EM JSON
# ============================================================

def salvar_formulario_json(formulario):
&quot;&quot;&quot;
Recebe um dicionário do formulário preenchido
Salva em arquivo JSON e atualiza a sessão para espelho
&quot;&quot;&quot;
# Carrega dados existentes
with open(JSON_MASTER, &quot;r&quot;, encoding=&quot;utf-8&quot;) as f:

dados_existentes = json.load(f)

# Adiciona novo formulário
dados_existentes.append(formulario)

# Salva novamente
with open(JSON_MASTER, &quot;w&quot;, encoding=&quot;utf-8&quot;) as f:
json.dump(dados_existentes, f, ensure_ascii=False, indent=4)

# Atualiza sessão do Streamlit para espelho imediato
st.session_state[&quot;formularios&quot;] = dados_existentes

# ============================================================
# PÁGINA VISUALIZAÇÃO – ESPELHO FIEL (TRECHO FINAL COMPLETO)
# ============================================================

if st.session_state.get(&quot;pagina&quot;) == &quot;visualizar&quot;:
st.title(&quot;  ️ Visualização de Registros&quot;)

# 1. Carregamento seguro do arquivo JSON
if os.path.exists(JSON_MASTER):
try:
with open(JSON_MASTER, &quot;r&quot;, encoding=&quot;utf-8&quot;) as f:
dados_carregados = json.load(f)
# Filtra apenas o que é dicionário (remove lixo do arquivo)
st.session_state[&quot;formularios&quot;] = [item for item in dados_carregados if
isinstance(item, dict)]
except:
st.session_state[&quot;formularios&quot;] = []

formularios = st.session_state.get(&quot;formularios&quot;, [])

if not formularios:
st.warning(&quot;⚠️ Nenhum formulário válido encontrado.&quot;)
else:
for idx, form in enumerate(formularios, 1):

# --- BLINDAGEM CONTRA O ERRO ---
# Se não for um dicionário, pula o item imediatamente
if not isinstance(form, dict):
continue

# Agora o .get() e o .upper() estão protegidos
nome_exibicao = str(form.get(&quot;Nome&quot;, f&quot;Colaborador {idx}&quot;)).upper()

with st.expander(f&quot;   FORMULÁRIO DE: {nome_exibicao}&quot;):
# IDENTIFICAÇÃO
st.subheader(&quot;   Identificação&quot;)
c1, c2 = st.columns(2)
with c1:
st.write(f&quot;**Nome:** {form.get(&#39;Nome&#39;, &#39;Não informado&#39;)}&quot;)
st.write(f&quot;**Cargo:** {form.get(&#39;Cargo&#39;, &#39;Não informado&#39;)}&quot;)
st.write(f&quot;**Setor:** {form.get(&#39;Setor&#39;, &#39;Não informado&#39;)}&quot;)
st.write(f&quot;**Chefe:** {form.get(&#39;Chefe&#39;, &#39;Não informado&#39;)}&quot;)
with c2:
st.write(f&quot;**Departamento:** {form.get(&#39;Departamento&#39;, &#39;Não informado&#39;)}&quot;)
st.write(f&quot;**Empresa / Unidade:** {form.get(&#39;Empresa&#39;, &#39;Não informado&#39;)}&quot;)
st.write(f&quot;**Escolaridade:** {form.get(&#39;Escolaridade&#39;, &#39;Não informado&#39;)}&quot;)

st.info(f&quot;**Objetivo:** {form.get(&#39;Objetivo&#39;, &#39;Não informado&#39;)}&quot;)

# ATIVIDADES
st.markdown(&quot;---&quot;)
st.subheader(&quot;   Atividades Executadas&quot;)
df_ativ = pd.DataFrame(form.get(&quot;Atividades&quot;, []))
st.table(df_ativ) if not df_ativ.empty else st.write(&quot;Nenhuma atividade.&quot;)

# DIFICULDADES E SUGESTÕES
st.subheader(&quot;   Dificuldades e Sugestões&quot;)
df_dif = pd.DataFrame(form.get(&quot;Dificuldades&quot;, []))
st.table(df_dif) if not df_dif.empty else st.write(&quot;Nenhuma dificuldade.&quot;)

df_sug = pd.DataFrame(form.get(&quot;Sugestoes&quot;, []))
st.table(df_sug) if not df_sug.empty else st.write(&quot;Nenhuma sugestão.&quot;)

# DISC
st.subheader(&quot;   Questionário DISC&quot;)
respostas_disc = {k: v for k, v in form.items() if str(k).startswith(&quot;Q&quot;)}
lista_disc = []
for i in range(1, 25): # Loop fixo de 24 questões
letra = respostas_disc.get(f&quot;Q{i}&quot;, &quot;-&quot;)
lista_disc.append({&quot;Nº&quot;: i, &quot;Resposta&quot;: letra})
st.table(pd.DataFrame(lista_disc))

# BOTÃO DE LIMPEZA GERAL
if st.button(&quot;  ️ LIMPAR TODOS OS FORMULÁRIOS&quot;, key=&quot;limpar_tudo&quot;):
st.session_state[&quot;formularios&quot;] = []
if os.path.exists(JSON_MASTER):
with open(JSON_MASTER, &quot;w&quot;, encoding=&quot;utf-8&quot;) as f:
json.dump([], f)
st.success(&quot;✅ Banco de dados limpo com sucesso!&quot;)

st.rerun()