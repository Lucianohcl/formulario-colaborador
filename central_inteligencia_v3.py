# ============================================================
# CENTRAL DE INTELIGÊNCIA NETEXAME — VERSÃO FINAL DEFINITIVA
# ============================================================
# INSTALAÇÃO:
# 1. Cole no FINAL do seu app
# 2. Sidebar: btn_central = st.sidebar.button("🧠 Central de Inteligência")
# 3. Roteador: elif btn_central: st.session_state.pagina = "central_inteligencia"
# ============================================================

import streamlit.components.v1 as components

# ============================================================
# FUNÇÕES GLOBAIS — cole junto de salvar_no_github, etc.
# ============================================================

def salvar_master(nome_colaborador, novos_dados):
    try:
        _repo = st.session_state.get("repo_conectado")
        if _repo is None:
            _repo = Github(st.secrets["DB_TOKEN"]).get_repo("lucianohcl/formulario-colaborador")
            st.session_state.repo_conectado = _repo
        nome_limpo = str(nome_colaborador).strip().replace(" ", "_").upper()
        caminho = f"master/{nome_limpo}.json"
        try:
            arq = _repo.get_contents(caminho)
            atual = json.loads(arq.decoded_content.decode())
        except:
            atual = {"colaborador": nome_colaborador, "criado_em": datetime.now().strftime("%d/%m/%Y %H:%M:%S")}
        atual.update(novos_dados)
        atual["ultima_atualizacao"] = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        conteudo = json.dumps(atual, indent=4, ensure_ascii=False)
        try:
            f = _repo.get_contents(caminho)
            _repo.update_file(f.path, f"master update: {nome_colaborador}", conteudo, f.sha)
        except:
            _repo.create_file(caminho, f"master novo: {nome_colaborador}", conteudo)
        return True
    except Exception as e:
        st.toast(f"⚠️ Master não salvo: {e}", icon="⚠️")
        return False

def carregar_master(nome_colaborador):
    try:
        _repo = st.session_state.get("repo_conectado")
        if _repo is None:
            _repo = Github(st.secrets["DB_TOKEN"]).get_repo("lucianohcl/formulario-colaborador")
            st.session_state.repo_conectado = _repo
        nome_limpo = str(nome_colaborador).strip().replace(" ", "_").upper()
        arq = _repo.get_contents(f"master/{nome_limpo}.json")
        return json.loads(arq.decoded_content.decode())
    except:
        return {}

def salvar_master_equipe(novos_dados):
    try:
        _repo = st.session_state.get("repo_conectado")
        if _repo is None:
            _repo = Github(st.secrets["DB_TOKEN"]).get_repo("lucianohcl/formulario-colaborador")
            st.session_state.repo_conectado = _repo
        caminho = "master/_EQUIPE.json"
        try:
            arq = _repo.get_contents(caminho)
            atual = json.loads(arq.decoded_content.decode())
        except:
            atual = {"tipo": "panorama_equipe", "criado_em": datetime.now().strftime("%d/%m/%Y %H:%M:%S")}
        atual.update(novos_dados)
        atual["ultima_atualizacao"] = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        conteudo = json.dumps(atual, indent=4, ensure_ascii=False)
        try:
            f = _repo.get_contents(caminho)
            _repo.update_file(f.path, "equipe master update", conteudo, f.sha)
        except:
            _repo.create_file(caminho, "equipe master novo", conteudo)
        return True
    except Exception as e:
        st.toast(f"⚠️ Master equipe não salvo: {e}", icon="⚠️")
        return False

def carregar_master_equipe():
    try:
        _repo = st.session_state.get("repo_conectado")
        if _repo is None:
            _repo = Github(st.secrets["DB_TOKEN"]).get_repo("lucianohcl/formulario-colaborador")
            st.session_state.repo_conectado = _repo
        arq = _repo.get_contents("master/_EQUIPE.json")
        return json.loads(arq.decoded_content.decode())
    except:
        return {}

def listar_masters_individuais():
    try:
        _repo = st.session_state.get("repo_conectado")
        if _repo is None:
            _repo = Github(st.secrets["DB_TOKEN"]).get_repo("lucianohcl/formulario-colaborador")
            st.session_state.repo_conectado = _repo
        arquivos = _repo.get_contents("master")
        resultado = []
        for a in arquivos:
            if a.name.endswith(".json") and a.name != "_EQUIPE.json":
                try:
                    resultado.append(json.loads(a.decoded_content.decode()))
                except:
                    continue
        return resultado
    except:
        return []


# ============================================================
# FUNÇÕES DE IA
# ============================================================

@st.cache_data(ttl=1, show_spinner=False)
def gerar_laudo_individual_ia(dados_json_str):
    try:
        client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
        prompt = f"""
Você é um perito auditor sênior da NetExame Auditoria Estratégica.
Gere um LAUDO PERICIAL INDIVIDUAL completo com base no JSON abaixo.
Use markdown. Estruture EXATAMENTE assim:

## 1. IDENTIDADE OPERACIONAL
Nome, cargo, perfil DISC dominante, status de carga horária.

## 2. DIAGNÓSTICO DE ROI AUDITADO
ROI auditado em R$, horas recuperáveis, ganho em dias.
Explique OBRIGATORIAMENTE a metodologia de auditoria pericial:
- O ROI auditado é resultado de perícia técnica sobre as sugestões do colaborador
- Cada sugestão é classificada em 3 categorias com ponderação diferente:
  🤖 Transformação Digital (automação, IA, sistemas, integração) → 85% do potencial
  📈 Otimização de Processo (padronização, POP, checklist, treinamento) → 45% do potencial
  💡 Melhoria Incremental (demais melhorias operacionais) → 20% do potencial
- Base de cálculo: Custo Total de Ocupação de R$ 35,00/hora
- Fórmula: Horas declaradas × Frequência anual × Fator de ponderação × R$ 35,00
- O ROI auditado é MENOR que o bruto porque aplica rigor técnico
Cite as sugestões reais do colaborador e a categoria em que cada uma foi classificada.

## 3. ANÁLISE COMPORTAMENTAL
Perfil DISC, aderência ao cargo, pontos fortes e riscos. Conecte ao cargo e atividades.

## 4. AUDITORIA DE PROCESSOS
Aderência ao POP, nexo causal, desvios. Cite atividades específicas se disponíveis.

## 5. PRODUTIVIDADE E KPIs
Score por KPI, KPI crítico, gaps de conformidade.

## 6. VEREDITO PERICIAL
- **PARAR:** o que parar com justificativa
- **DELEGAR:** para quem, baseado no DISC
- **FOCAR:** onde, maior impacto financeiro

## 7. PLANO DE AÇÃO (3 ações)
Título | Prazo | Impacto R$ | Responsável (perfil DISC)

Linguagem executiva. Números específicos. Só use dados do JSON.
Se campo ausente: "Dados não disponíveis".

JSON:
{dados_json_str}
"""
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Perito auditor sênior. Técnico, direto, quantificado."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=2500,
            temperature=0.2
        )
        return resp.choices[0].message.content
    except Exception as e:
        return f"❌ Erro ao gerar laudo: {e}"


@st.cache_data(ttl=86400, show_spinner=False)
def gerar_parecer_executivo_equipe_ia(dados_json_str):
    try:
        client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
        prompt = f"""
Você é consultor sênior de RH e auditoria estratégica da NetExame.
Gere PARECER EXECUTIVO + PLANO DE AÇÃO com cronograma e resultados financeiros.

## PARECER EXECUTIVO DA EQUIPE

### Resumo Estratégico
2 parágrafos com ROI total, horas recuperáveis e cultura DISC.

### Diagnóstico Coletivo
- Cultura dominante e impacto operacional
- Distribuição DISC e gaps de cobertura
- Sobrecarga vs subutilização
- Alinhamentos e desalinhamentos cargo x perfil

### Riscos Identificados
3 riscos com impacto financeiro estimado em R$.

### Oportunidades Imediatas
3 oportunidades com valor em R$/ano cada.

---

## PLANO DE AÇÃO ESTRATÉGICO

### FASE 1 — AÇÕES IMEDIATAS (0 a 30 dias)
- [ ] Ação | Responsável (perfil DISC) | Impacto R$ | Como medir

### FASE 2 — AÇÕES ESTRUTURAIS (30 a 90 dias)
- [ ] Ação | Responsável | Impacto R$ | Como medir

### FASE 3 — AÇÕES ESTRATÉGICAS (90 a 180 dias)
- [ ] Ação | Responsável | Impacto R$ | Como medir

---

## RESULTADO FINANCEIRO PROJETADO

| Fase | Investimento | Retorno Esperado | ROI |
|------|-------------|-----------------|-----|
| Fase 1 | R$ X | R$ X | X% |
| Fase 2 | R$ X | R$ X | X% |
| Fase 3 | R$ X | R$ X | X% |
| **TOTAL** | R$ X | **R$ X/ano** | **X%** |

**Payback estimado:** X meses

Linguagem de boardroom. Específico com nomes. Só dados fornecidos.

DADOS:
{dados_json_str}
"""
        resp = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Consultor estratégico sênior. Executivo, quantificado, acionável."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=4000,
            temperature=0.2
        )
        return resp.choices[0].message.content
    except Exception as e:
        return f"❌ Erro ao gerar parecer: {e}"


# ============================================================
# HELPERS HTML
# ============================================================

def md_to_html_laudo(texto):
    """Converte markdown do laudo em HTML estilizado dark."""
    import re
    if not texto:
        return ""
    linhas = texto.split("\n")
    html = []
    in_table = False
    in_list = False

    for linha in linhas:
        # Tabela
        if linha.strip().startswith("|"):
            if not in_table:
                html.append("<table style='width:100%;border-collapse:collapse;margin:8px 0;'>")
                in_table = True
            celulas = [c.strip() for c in linha.strip().strip("|").split("|")]
            if all(set(c) <= set("-:| ") for c in celulas):
                continue
            is_header = not any("<td>" in h for h in html[-10:] if "<t" in h)
            tag = "th" if is_header else "td"
            style_th = "style='background:rgba(255,255,255,0.06);padding:7px 10px;text-align:left;font-size:11px;color:#94A3B8;border-bottom:1px solid rgba(255,255,255,0.08);'"
            style_td = "style='padding:7px 10px;font-size:11px;color:#6B7280;border-bottom:1px solid rgba(255,255,255,0.04);'"
            s = style_th if tag == "th" else style_td
            html.append("<tr>" + "".join(f"<{tag} {s}>{c}</{tag}>" for c in celulas) + "</tr>")
            continue
        else:
            if in_table:
                html.append("</table>")
                in_table = False

        l = linha
        # Seção ## → título com barra azul
        if l.startswith("## "):
            txt = l[3:].strip()
            html.append(f"""<div style='background:rgba(96,165,250,0.08);border-left:3px solid #60A5FA;
                padding:8px 12px;border-radius:0 6px 6px 0;margin:14px 0 8px;'>
                <span style='font-size:11px;font-weight:800;letter-spacing:2px;
                text-transform:uppercase;color:#60A5FA;'>{txt}</span></div>""")
            continue
        if l.startswith("### "):
            txt = l[4:].strip()
            html.append(f"<div style='font-size:12px;font-weight:700;color:#94A3B8;margin:10px 0 4px;'>{txt}</div>")
            continue
        # Bold
        l = re.sub(r"\*\*(.+?)\*\*", r"<strong style='color:#E2E8F0'>\1</strong>", l)
        # Checkbox e lista
        l = l.replace("- [ ]", "☐").replace("- [x]", "☑")
        if l.strip().startswith(("- ", "☐", "☑", "• ")):
            html.append(f"<div style='font-size:11px;color:#6B7280;line-height:1.7;padding:2px 0 2px 8px;'>{l.strip()}</div>")
            continue
        # Separador
        if l.strip() in ("---", ""):
            html.append("<div style='height:8px'></div>")
            continue
        # Parágrafo normal
        if l.strip():
            html.append(f"<p style='font-size:11px;color:#6B7280;line-height:1.7;margin:3px 0;'>{l.strip()}</p>")

    if in_table:
        html.append("</table>")
    return "\n".join(html)


def build_colab_rows_html(masters):
    """Monta as linhas da tabela de colaboradores no estilo do mockup."""
    cores = {
        "D": ("rgba(239,68,68,0.15)", "#F87171"),
        "I": ("rgba(245,158,11,0.15)", "#FCD34D"),
        "S": ("rgba(16,185,129,0.15)", "#34D399"),
        "C": ("rgba(59,130,246,0.15)", "#60A5FA"),
    }
    rows = ""
    for m in masters:
        nome  = m.get("colaborador", "N/A")
        disc  = m.get("disc", {}).get("perfil_dominante", "N/A")
        roi   = m.get("roi",  {}).get("auditado", 0)
        efic  = m.get("produtividade", {}).get("eficiencia_real_pct", 0)
        carga = m.get("nexo_causal",   {}).get("status", "N/A")

        letra = disc[0] if disc and disc != "N/A" else "C"
        bg, cor = cores.get(letra, ("rgba(100,116,139,0.15)", "#94A3B8"))

        if carga == "sobrecarga":
            st_icon = "<span style='color:#F87171'>⚠️</span>"
        elif carga == "subutilizado":
            st_icon = "<span style='color:#FCD34D'>〰️</span>"
        else:
            st_icon = "<span style='color:#34D399'>✅</span>"

        rows += f"""
        <div class='colab-row'>
          <span class='cr-name'>{nome}</span>
          <span class='cr-disc' style='background:{bg};color:{cor};'>{disc}</span>
          <span class='cr-roi'>R$&nbsp;{roi:,.0f}</span>
          <span class='cr-efic'>{efic:.0f}%</span>
          <span class='cr-status'>{st_icon}</span>
        </div>"""
    return rows


def build_mini_metrics_html(master_sel):
    """Monta as 6 mini métricas do colaborador selecionado."""
    roi_i  = master_sel.get("roi",  {}).get("auditado", 0)
    disc_i = master_sel.get("disc", {}).get("perfil_dominante", "N/A")
    efic_i = master_sel.get("produtividade", {}).get("eficiencia_real_pct", 0)
    ader_i = master_sel.get("disc", {}).get("veredito_aderencia", "N/A")
    nc_i   = master_sel.get("nexo_causal", {}).get("status", "N/A")
    carg_i = (master_sel.get("campos") or {}).get("cargo", "N/A")

    nc_cor = "#F87171" if nc_i == "sobrecarga" else "#FCD34D" if nc_i == "subutilizado" else "#34D399"
    ader_cor = "#34D399" if "Alta" in str(ader_i) else "#FCD34D" if "Modera" in str(ader_i) else "#F87171"

    return f"""
    <div class='mini-metrics'>
      <div class='mm'><div class='mm-lbl'>ROI Auditado</div>
        <div class='mm-v' style='color:#34D399'>R$&nbsp;{roi_i:,.0f}</div></div>
      <div class='mm'><div class='mm-lbl'>Perfil DISC</div>
        <div class='mm-v' style='color:#A78BFA'>{disc_i}</div></div>
      <div class='mm'><div class='mm-lbl'>Eficiência</div>
        <div class='mm-v' style='color:#FCD34D'>{efic_i:.0f}%</div></div>
    </div>
    <div class='mini-metrics'>
      <div class='mm'><div class='mm-lbl'>Cargo</div>
        <div class='mm-v' style='color:#94A3B8;font-size:10px'>{carg_i[:18]}</div></div>
      <div class='mm'><div class='mm-lbl'>Aderência</div>
        <div class='mm-v' style='color:{ader_cor};font-size:10px'>{str(ader_i)[:14]}</div></div>
      <div class='mm'><div class='mm-lbl'>Carga</div>
        <div class='mm-v' style='color:{nc_cor};font-size:10px'>{nc_i.capitalize()}</div></div>
    </div>"""


def render_central_html(
    masters, master_equipe,
    roi_total, horas_total, total_colab, cultura, sobrecargas,
    colab_sel_idx,
    laudo_texto, laudo_ts,
    parecer_texto, parecer_ts
):
    """
    Renderiza a página inteira da Central como HTML puro.
    Usa JavaScript para comunicar seleção de colaborador ao Streamlit via query param.
    """
    # Nomes para o select
    nomes = [m.get("colaborador", f"Col {i+1}") for i, m in enumerate(masters)]
    options_html = "".join(
        f"<option value='{i}' {'selected' if i == colab_sel_idx else ''}>{n}</option>"
        for i, n in enumerate(nomes)
    )

    # Mini métricas do colaborador selecionado
    master_sel = masters[colab_sel_idx] if masters else {}
    mini_html  = build_mini_metrics_html(master_sel) if master_sel else ""

    # Linhas da tabela de colaboradores
    colab_rows = build_colab_rows_html(masters)

    # Laudo e parecer em HTML
    laudo_html   = md_to_html_laudo(laudo_texto)   if laudo_texto   else "<p style='color:#475569;font-size:12px;font-style:italic;'>Clique em Gerar Laudo Completo para iniciar.</p>"
    parecer_html = md_to_html_laudo(parecer_texto) if parecer_texto else "<p style='color:#475569;font-size:12px;font-style:italic;'>Clique em Gerar Parecer Executivo + Plano para iniciar.</p>"

    ts_laudo   = f"⏱ Gerado em: {laudo_ts} · cache 24h"   if laudo_ts   else ""
    ts_parecer = f"⏱ Gerado em: {parecer_ts} · GPT-4o · cache 24h" if parecer_ts else ""

    nome_sel = nomes[colab_sel_idx] if nomes else ""

    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{background:#07090F;font-family:'Inter',system-ui,sans-serif;color:#E2E8F0;padding:0;}}

/* TOP METRICS */
.top-metrics{{display:grid;grid-template-columns:repeat(5,1fr);gap:10px;margin-bottom:20px}}
.tm{{background:#1A1D27;border:1px solid rgba(255,255,255,0.07);border-radius:10px;padding:14px;text-align:center}}
.tm-lbl{{font-size:9px;font-weight:700;letter-spacing:2px;text-transform:uppercase;color:#4B5563;margin-bottom:5px}}
.tm-v{{font-size:18px;font-weight:800;color:#F1F5F9}}
.g{{color:#34D399}}.b{{color:#60A5FA}}.r{{color:#F87171}}.p{{color:#A78BFA}}

/* DIVIDER */
.divider{{border:none;border-top:1px solid rgba(255,255,255,0.06);margin:16px 0}}

/* TWO COLUMNS */
.cols{{display:grid;grid-template-columns:1fr 1fr;gap:20px;align-items:start}}

/* COL HEADER */
.col-header{{display:flex;align-items:center;gap:8px;margin-bottom:14px}}
.col-dot{{width:8px;height:8px;border-radius:50%;flex-shrink:0}}
.col-title{{font-size:15px;font-weight:700;color:#F1F5F9}}

/* SELECT */
.sel-label{{font-size:12px;color:#9CA3AF;margin-bottom:6px;display:block}}
select{{width:100%;background:#1A1D27;border:1px solid rgba(255,255,255,0.1);
        border-radius:8px;padding:10px 14px;font-size:13px;color:#E2E8F0;
        margin-bottom:12px;cursor:pointer;outline:none;}}
select:focus{{border-color:rgba(96,165,250,0.4)}}

/* MINI METRICS */
.mini-metrics{{display:grid;grid-template-columns:repeat(3,1fr);gap:8px;margin-bottom:10px}}
.mm{{background:#1A1D27;border:1px solid rgba(255,255,255,0.06);border-radius:8px;padding:10px;text-align:center}}
.mm-lbl{{font-size:9px;font-weight:700;letter-spacing:1px;text-transform:uppercase;color:#4B5563;margin-bottom:4px}}
.mm-v{{font-size:14px;font-weight:800;color:#F1F5F9}}

/* BUTTON */
.btn{{width:100%;padding:11px;border-radius:8px;border:none;font-size:12px;font-weight:700;
      letter-spacing:1px;text-transform:uppercase;cursor:pointer;margin-bottom:10px;transition:all 0.2s}}
.btn-blue{{background:linear-gradient(135deg,#4F46E5,#7C3AED);color:white;
           box-shadow:0 4px 16px rgba(79,70,229,0.3)}}
.btn-blue:hover{{box-shadow:0 6px 24px rgba(79,70,229,0.5)}}
.btn-green{{background:linear-gradient(135deg,#059669,#10B981);color:white;
            box-shadow:0 4px 16px rgba(16,185,129,0.3)}}
.btn-green:hover{{box-shadow:0 6px 24px rgba(16,185,129,0.5)}}
.btn-dl{{width:100%;padding:10px;border-radius:8px;border:1px solid rgba(255,255,255,0.1);
         background:rgba(255,255,255,0.03);font-size:12px;color:#9CA3AF;cursor:pointer;
         text-align:center;margin-top:8px;transition:all 0.2s;text-decoration:none;display:block}}
.btn-dl:hover{{border-color:rgba(255,255,255,0.2);color:#E2E8F0}}

/* CAPTION */
.caption{{font-size:10px;color:#475569;margin-bottom:10px}}

/* EXPANDER */
.expander{{background:#1A1D27;border:1px solid rgba(255,255,255,0.07);
           border-radius:10px;overflow:hidden;margin-bottom:10px}}
.exp-head{{padding:12px 16px;display:flex;justify-content:space-between;
           align-items:center;cursor:pointer;user-select:none}}
.exp-head span{{font-size:13px;color:#E2E8F0;font-weight:500}}
.exp-arrow{{color:#4B5563;font-size:11px;transition:transform 0.2s}}
.exp-body{{padding:16px;border-top:1px solid rgba(255,255,255,0.06);
           max-height:520px;overflow-y:auto}}

/* EQUIPE SUMMARY BOX */
.eq-summary{{background:rgba(27,30,93,0.15);border:1px solid rgba(27,30,93,0.4);
             border-radius:8px;padding:12px;margin-bottom:12px;
             font-size:12px;color:#94A3B8;line-height:1.6}}

/* COLAB TABLE */
.colab-table{{background:#1A1D27;border:1px solid rgba(255,255,255,0.07);
              border-radius:10px;padding:12px 14px;margin-bottom:12px}}
.colab-table-title{{font-size:9px;font-weight:700;letter-spacing:2px;
                    text-transform:uppercase;color:#4B5563;margin-bottom:10px}}
.colab-row{{display:flex;align-items:center;gap:8px;padding:7px 0;
            border-bottom:1px solid rgba(255,255,255,0.04)}}
.colab-row:last-child{{border-bottom:none}}
.cr-name{{font-size:12px;color:#E2E8F0;font-weight:500;flex:2;
          white-space:nowrap;overflow:hidden;text-overflow:ellipsis;max-width:140px}}
.cr-disc{{font-size:10px;font-weight:800;padding:2px 7px;border-radius:5px;flex-shrink:0}}
.cr-roi{{font-size:11px;font-weight:700;color:#34D399;flex:1;text-align:right;white-space:nowrap}}
.cr-efic{{font-size:11px;color:#94A3B8;text-align:right;min-width:32px}}
.cr-status{{font-size:13px;flex-shrink:0;margin-left:4px}}

/* SCROLLBAR */
.exp-body::-webkit-scrollbar{{width:4px}}
.exp-body::-webkit-scrollbar-track{{background:transparent}}
.exp-body::-webkit-scrollbar-thumb{{background:rgba(255,255,255,0.1);border-radius:4px}}
</style>
</head>
<body>

<!-- TOP METRICS -->
<div class="top-metrics">
  <div class="tm"><div class="tm-lbl">👥 Auditados</div><div class="tm-v">{total_colab}</div></div>
  <div class="tm"><div class="tm-lbl">💰 ROI Total</div><div class="tm-v g">R$&nbsp;{roi_total:,.0f}</div></div>
  <div class="tm"><div class="tm-lbl">⚡ Horas Recup.</div><div class="tm-v b">{horas_total:.0f}&nbsp;h/ano</div></div>
  <div class="tm"><div class="tm-lbl">📅 Ganho Cap.</div><div class="tm-v b">{horas_total/8:.0f}&nbsp;dias</div></div>
  <div class="tm"><div class="tm-lbl">🚨 Sobrecarga</div><div class="tm-v r">{sobrecargas}</div></div>
</div>

<hr class="divider">

<!-- TWO COLUMNS -->
<div class="cols">

  <!-- ═══════════════════════ COLUNA ESQUERDA ═══════════════════════ -->
  <div>
    <div class="col-header">
      <div class="col-dot" style="background:#60A5FA;box-shadow:0 0 8px #60A5FA"></div>
      <span class="col-title">👤 Laudo Pericial Individual</span>
    </div>

    <span class="sel-label">Selecione o colaborador:</span>
    <select id="colab-select" onchange="onColabChange(this.value)">
      {options_html}
    </select>

    {mini_html}

    <button class="btn btn-blue" onclick="onGerarLaudo()">🔬 Gerar Laudo Completo</button>
    <div class="caption">{ts_laudo}</div>

    <div class="expander">
      <div class="exp-head" onclick="toggleExp('exp-laudo','arr-laudo')">
        <span>📄 Ver Laudo Completo</span>
        <span class="exp-arrow" id="arr-laudo">▼</span>
      </div>
      <div class="exp-body" id="exp-laudo">
        {laudo_html}
      </div>
    </div>

    <button class="btn-dl" onclick="onDlLaudo()">📥 Baixar Laudo — {nome_sel}</button>
  </div>

  <!-- ═══════════════════════ COLUNA DIREITA ════════════════════════ -->
  <div>
    <div class="col-header">
      <div class="col-dot" style="background:#34D399;box-shadow:0 0 8px #34D399"></div>
      <span class="col-title">🏢 Parecer Executivo da Equipe</span>
    </div>

    <div class="eq-summary">
      <b style="color:#E2E8F0">Base:</b> {total_colab} colaboradores auditados &nbsp;|&nbsp;
      Cultura dominante: <b>{cultura}</b> &nbsp;|&nbsp;
      ROI: <b style="color:#34D399">R$&nbsp;{roi_total:,.0f}</b>
    </div>

    <div class="colab-table">
      <div class="colab-table-title">Equipe Auditada</div>
      {colab_rows}
    </div>

    <button class="btn btn-green" onclick="onGerarParecer()">🚀 Gerar Parecer Executivo + Plano</button>
    <div class="caption">{ts_parecer}</div>

    <div class="expander">
      <div class="exp-head" onclick="toggleExp('exp-parecer','arr-parecer')">
        <span>📊 Ver Parecer + Plano Completo</span>
        <span class="exp-arrow" id="arr-parecer">▼</span>
      </div>
      <div class="exp-body" id="exp-parecer">
        {parecer_html}
      </div>
    </div>

    <button class="btn-dl" onclick="onDlParecer()">📥 Baixar Parecer Executivo — Versão Diretoria</button>
  </div>

</div><!-- /cols -->

<script>
function toggleExp(bodyId, arrowId) {{
  var body  = document.getElementById(bodyId);
  var arrow = document.getElementById(arrowId);
  var open  = body.style.display !== 'none';
  body.style.display  = open ? 'none' : 'block';
  arrow.style.transform = open ? 'rotate(-90deg)' : 'rotate(0deg)';
}}

// Comunica ao Streamlit via postMessage
function sendMsg(type, data) {{
  window.parent.postMessage({{type: type, data: data}}, "*");
}}

function onColabChange(idx)  {{ sendMsg("COLAB_CHANGE",  parseInt(idx)); }}
function onGerarLaudo()      {{ sendMsg("GERAR_LAUDO",   null); }}
function onGerarParecer()    {{ sendMsg("GERAR_PARECER", null); }}
function onDlLaudo()         {{ sendMsg("DL_LAUDO",      null); }}
function onDlParecer()       {{ sendMsg("DL_PARECER",    null); }}
</script>
</body>
</html>"""


def html_export_laudo(master, laudo_texto):
    import re
    nome  = master.get("colaborador", "Colaborador")
    cargo = (master.get("campos") or {}).get("cargo", "N/A")
    roi   = master.get("roi",  {}).get("auditado", 0)
    disc  = master.get("disc", {}).get("perfil_dominante", "N/A")
    efic  = master.get("produtividade", {}).get("eficiencia_real_pct", 0)
    corpo = md_to_html_laudo(laudo_texto)
    data  = datetime.now().strftime("%d/%m/%Y")
    return f"""<!DOCTYPE html><html lang="pt-BR"><head><meta charset="utf-8">
<style>
body{{font-family:'Segoe UI',sans-serif;background:#f4f6f9;padding:40px;color:#2c3e50}}
.page{{background:white;max-width:920px;margin:auto;padding:50px;border-radius:12px;
       box-shadow:0 8px 24px rgba(0,0,0,0.08);border-top:10px solid #1B1E5D}}
.hdr{{text-align:center;padding-bottom:24px;border-bottom:2px solid #ecf0f1;margin-bottom:32px}}
.hdr h1{{color:#1B1E5D;font-size:22px;margin:0 0 6px;text-transform:uppercase;letter-spacing:1px}}
.hdr p{{color:#7f8c8d;margin:0;font-size:12px}}
.metrics{{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin:24px 0}}
.metric{{background:#f8f9fb;border:1px solid #e8ecf0;border-radius:10px;padding:14px;
         text-align:center;border-bottom:4px solid #1B1E5D}}
.metric label{{font-size:9px;text-transform:uppercase;letter-spacing:1px;
               color:#95a5a6;font-weight:700;display:block;margin-bottom:5px}}
.metric span{{font-size:18px;font-weight:800;color:#1B1E5D}}
/* redefine cores do laudo para versão light */
.page p{{color:#34495e!important;font-size:13px!important}}
.page div[style*="rgba(96,165,250"]{{background:#EBF5FB!important;border-left-color:#2980B9!important}}
.page div[style*="rgba(96,165,250"] span{{color:#1B4F72!important}}
.page strong{{color:#2c3e50!important}}
table{{width:100%;border-collapse:collapse;margin:10px 0}}
th{{background:#eef0f4;padding:8px;text-align:left;border-bottom:2px solid #1B1E5D;font-size:11px}}
td{{padding:8px;border-bottom:1px solid #ecf0f1;font-size:12px;color:#34495e}}
.footer{{text-align:center;margin-top:40px;padding-top:20px;
         border-top:1px solid #ecf0f1;font-size:11px;color:#bdc3c7}}
</style></head><body>
<div class="page">
  <div class="hdr">
    <h1>Laudo Pericial Individual</h1>
    <p>NetExame Auditoria Estratégica · {data} · CONFIDENCIAL</p>
  </div>
  <div class="metrics">
    <div class="metric"><label>Colaborador</label><span style="font-size:13px">{nome}</span></div>
    <div class="metric"><label>ROI Auditado</label><span>R$&nbsp;{roi:,.0f}</span></div>
    <div class="metric"><label>Perfil DISC</label><span>{disc}</span></div>
    <div class="metric"><label>Eficiência KPI</label><span>{efic:.0f}%</span></div>
  </div>
  {corpo}
  <div class="footer">NETEXAME AUDITORIA ESTRATÉGICA · 2026 · CONFIDENCIAL</div>
</div></body></html>"""


def html_export_parecer(masters, parecer_texto, roi_total, horas_total, total_colab, cultura):
    from datetime import datetime as _dt
    corpo = md_to_html_laudo(parecer_texto)
    data  = _dt.now().strftime("%d/%m/%Y")
    dias  = horas_total / 8 if horas_total else 0

    linhas = ""
    cores  = {"D":"#F87171","I":"#FCD34D","S":"#34D399","C":"#60A5FA"}
    for m in masters:
        n  = m.get("colaborador","N/A")
        c  = (m.get("campos") or {}).get("cargo","N/A")
        d  = m.get("disc",{}).get("perfil_dominante","N/A")
        r  = m.get("roi",{}).get("auditado",0)
        ef = m.get("produtividade",{}).get("eficiencia_real_pct",0)
        nc = m.get("nexo_causal",{}).get("status","N/A")
        cor = cores.get(d[0] if d and d!="N/A" else "C","#94A3B8")
        linhas += f"<tr><td>{n}</td><td>{c}</td><td style='color:{cor};font-weight:700'>{d}</td><td>{nc}</td><td style='text-align:right'>{ef:.0f}%</td><td style='text-align:right;font-weight:700'>R$&nbsp;{r:,.0f}</td></tr>"

    return f"""<!DOCTYPE html><html lang="pt-BR"><head><meta charset="utf-8">
<style>
body{{font-family:'Segoe UI',sans-serif;background:#f4f6f9;padding:40px;color:#2c3e50}}
.page{{background:white;max-width:960px;margin:auto;padding:50px;border-radius:12px;
       box-shadow:0 8px 24px rgba(0,0,0,0.08);border-top:10px solid #1B1E5D}}
.hdr{{text-align:center;padding-bottom:24px;border-bottom:2px solid #ecf0f1;margin-bottom:32px}}
.hdr h1{{color:#1B1E5D;font-size:22px;margin:0 0 6px;text-transform:uppercase;letter-spacing:1px}}
.hdr p{{color:#7f8c8d;margin:0;font-size:12px}}
.metrics{{display:grid;grid-template-columns:repeat(5,1fr);gap:12px;margin:24px 0}}
.metric{{background:#f8f9fb;border:1px solid #e8ecf0;border-radius:10px;padding:14px;
         text-align:center;border-bottom:4px solid #1B1E5D}}
.metric label{{font-size:9px;text-transform:uppercase;letter-spacing:1px;
               color:#95a5a6;font-weight:700;display:block;margin-bottom:5px}}
.metric span{{font-size:16px;font-weight:800;color:#1B1E5D}}
.page p{{color:#34495e!important;font-size:13px!important}}
.page div[style*="rgba(96,165,250"]{{background:#EBF5FB!important;border-left-color:#2980B9!important}}
.page div[style*="rgba(96,165,250"] span{{color:#1B4F72!important}}
.page strong{{color:#2c3e50!important}}
table{{width:100%;border-collapse:collapse;margin:12px 0}}
th{{background:#eef0f4;padding:8px;text-align:left;border-bottom:2px solid #1B1E5D;
    font-size:11px;text-transform:uppercase;letter-spacing:1px;color:#7f8c8d}}
td{{padding:8px;border-bottom:1px solid #ecf0f1;font-size:12px;color:#34495e}}
.footer{{text-align:center;margin-top:40px;padding-top:20px;
         border-top:1px solid #ecf0f1;font-size:11px;color:#bdc3c7}}
</style></head><body>
<div class="page">
  <div class="hdr">
    <h1>Parecer Executivo da Equipe + Plano de Ação</h1>
    <p>NetExame Auditoria Estratégica · {data} · CONFIDENCIAL DIRETORIA</p>
  </div>
  <div class="metrics">
    <div class="metric"><label>Colaboradores</label><span>{total_colab}</span></div>
    <div class="metric"><label>ROI Total</label><span>R$&nbsp;{roi_total:,.0f}</span></div>
    <div class="metric"><label>Horas Recup.</label><span>{horas_total:.0f}&nbsp;h/ano</span></div>
    <div class="metric"><label>Ganho Cap.</label><span>{dias:.0f}&nbsp;dias</span></div>
    <div class="metric"><label>Cultura</label><span>{cultura}</span></div>
  </div>
  <table><thead><tr>
    <th>Colaborador</th><th>Cargo</th><th>DISC</th>
    <th>Carga</th><th style='text-align:right'>Eficiência</th><th style='text-align:right'>ROI</th>
  </tr></thead><tbody>{linhas}</tbody></table>
  {corpo}
  <div class="footer">NETEXAME AUDITORIA ESTRATÉGICA · 2026 · CONFIDENCIAL DIRETORIA</div>
</div></body></html>"""


# ============================================================
# PÁGINA — CENTRAL DE INTELIGÊNCIA
# ============================================================

if st.session_state.get("pagina") == "central_inteligencia":

    # ── CSS mínimo no Streamlit (apenas para ocultar padding extra) ──
    st.markdown("""
    <style>
    .stApp { background-color: #07090F !important; }
    section[data-testid="stSidebar"] { background-color: #0E1117 !important; }
    .block-container { padding-top: 16px !important; padding-bottom: 0 !important; }
    footer { display: none !important; }
    </style>
    """, unsafe_allow_html=True)

    # ── Header ───────────────────────────────────────────────
    st.markdown("""
    <div style='background:linear-gradient(135deg,#1B1E5D,#2d3a8c);
                padding:22px 28px;border-radius:12px;margin-bottom:16px;'>
      <h1 style='color:white;margin:0;font-size:22px;font-weight:800;
                 font-family:sans-serif;letter-spacing:1px;'>
        🧠 Central de Inteligência
      </h1>
      <p style='color:rgba(255,255,255,0.55);margin:6px 0 0;font-size:13px;'>
        NetExame Auditoria Estratégica · Laudo Pericial + Parecer Executivo da Equipe
      </p>
    </div>
    """, unsafe_allow_html=True)

    # ── Conexão ─────────────────────────────────────────────
    try:
        _repo = st.session_state.get("repo_conectado")
        if _repo is None:
            _repo = Github(st.secrets["DB_TOKEN"]).get_repo("lucianohcl/formulario-colaborador")
            st.session_state.repo_conectado = _repo
    except Exception as e:
        st.error(f"❌ Erro de conexão: {e}")
        st.stop()

    # ── Carrega dados ────────────────────────────────────────
    with st.spinner("🔄 Carregando dados..."):
        masters       = listar_masters_individuais()
        master_equipe = carregar_master_equipe()

    if not masters:
        st.warning("⚠️ Nenhum dado encontrado em /master/")
        st.info("""
**Para popular a Central:**
1. **Análise Inteligente** → selecione colaborador → rode a auditoria
2. **Perfil DISC** → mesmo colaborador → Gerar análise DISC
3. **Parecer Estratégico** → Aba 1 e Aba 3 → rode para o colaborador
4. **Produtividade** → audite os KPIs
5. **Evidências** → gere as evidências
6. Volte aqui — os dados são salvos automaticamente
        """)
        st.stop()

    # ── Estado da seleção ────────────────────────────────────
    if "central_colab_idx" not in st.session_state:
        st.session_state.central_colab_idx = 0

    colab_sel_idx = st.session_state.central_colab_idx
    colab_sel_idx = min(colab_sel_idx, len(masters) - 1)
    master_sel    = masters[colab_sel_idx]
    colab_sel     = master_sel.get("colaborador", "")

    # ── Métricas consolidadas ────────────────────────────────
    roi_total   = sum(m.get("roi", {}).get("auditado", 0)           for m in masters)
    horas_total = sum(m.get("roi", {}).get("horas_recuperaveis", 0) for m in masters)
    total_colab = len(masters)
    cultura     = master_equipe.get("disc_coletivo", {}).get("cultura_dominante", "N/A")
    sobrecargas = sum(1 for m in masters if m.get("nexo_causal", {}).get("status") == "sobrecarga")

    # ── Textos de laudo e parecer ────────────────────────────
    laudo_exibir   = (st.session_state.get(f"laudo_ind_{colab_sel}") or
                      master_sel.get("laudo_central", {}).get("texto", ""))
    laudo_ts       = master_sel.get("laudo_central", {}).get("gerado_em", "")

    parecer_exibir = (st.session_state.get("parecer_eq_central") or
                      master_equipe.get("parecer_executivo", {}).get("texto", ""))
    parecer_ts     = master_equipe.get("parecer_executivo", {}).get("gerado_em", "")

    # ── Renderiza HTML principal ─────────────────────────────
    html_central = render_central_html(
        masters, master_equipe,
        roi_total, horas_total, total_colab, cultura, sobrecargas,
        colab_sel_idx,
        laudo_exibir, laudo_ts,
        parecer_exibir, parecer_ts
    )

    # Altura dinâmica baseada no conteúdo
    altura = max(900, 400 + len(masters) * 40 +
                 (len(laudo_exibir) // 6) + (len(parecer_exibir) // 6))
    altura = min(altura, 2400)

    # ── Recebe eventos do HTML via query_params ──────────────
    # O HTML envia postMessage, mas no Streamlit usamos um workaround
    # com hidden inputs + botões Streamlit reais abaixo do componente

    clicked = components.html(html_central, height=altura, scrolling=False)

    # ── Controles reais do Streamlit (abaixo do visual) ──────
    st.markdown("---")
    st.markdown("<p style='color:#1E293B;font-size:11px;text-align:center;'>Controles da Central</p>",
                unsafe_allow_html=True)

    ctrl1, ctrl2, ctrl3, ctrl4, ctrl5 = st.columns(5)

    with ctrl1:
        nomes_ctrl = [m.get("colaborador", f"Col {i+1}") for i, m in enumerate(masters)]
        sel = st.selectbox("Colaborador", nomes_ctrl,
                           index=colab_sel_idx, key="ctrl_colab_sel",
                           label_visibility="collapsed")
        novo_idx = nomes_ctrl.index(sel)
        if novo_idx != st.session_state.central_colab_idx:
            st.session_state.central_colab_idx = novo_idx
            st.rerun()

    with ctrl2:
        if st.button("🔬 Gerar Laudo", use_container_width=True, key="ctrl_btn_laudo"):
            with st.spinner(f"🧠 Gerando laudo de {colab_sel}... (20-40s)"):
                dados_str = json.dumps(master_sel, indent=2, ensure_ascii=False)
                laudo = gerar_laudo_individual_ia(dados_str)
                salvar_master(colab_sel, {
                    "laudo_central": {"texto": laudo,
                                      "gerado_em": datetime.now().strftime("%d/%m/%Y %H:%M:%S")}
                })
                st.session_state[f"laudo_ind_{colab_sel}"] = laudo
                st.success("✅ Laudo gerado!")
                st.rerun()

    with ctrl3:
        if st.button("🚀 Gerar Parecer", use_container_width=True, key="ctrl_btn_parecer"):
            with st.spinner("🧠 Gerando parecer... (30-60s)"):
                resumo = {
                    "total_colaboradores": total_colab,
                    "roi_total_auditado":  round(roi_total, 2),
                    "horas_recuperaveis":  round(horas_total, 2),
                    "ganho_dias":          round(horas_total / 8, 1),
                    "cultura_dominante":   cultura,
                    "em_sobrecarga":       sobrecargas,
                    "colaboradores": [{
                        "nome":           m.get("colaborador"),
                        "cargo":          (m.get("campos") or {}).get("cargo", "N/A"),
                        "disc":           m.get("disc",  {}).get("perfil_dominante",  "N/A"),
                        "aderencia":      m.get("disc",  {}).get("veredito_aderencia","N/A"),
                        "roi":            m.get("roi",   {}).get("auditado",           0),
                        "horas_recup":    m.get("roi",   {}).get("horas_recuperaveis", 0),
                        "nexo_status":    m.get("nexo_causal",  {}).get("status",      "N/A"),
                        "horas_dia":      m.get("nexo_causal",  {}).get("horas_dia",    0),
                        "eficiencia_pct": m.get("produtividade",{}).get("eficiencia_real_pct", 0),
                        "kpi_critico":    m.get("produtividade",{}).get("kpi_critico", "N/A"),
                        "parecer_360":    m.get("parecer_360",  {}).get("veredito_final",""),
                        "evidencias":     list(m.get("evidencias_kpi", {}).get("documentos_por_kpi", {}).keys()),
                    } for m in masters]
                }
                parecer = gerar_parecer_executivo_equipe_ia(json.dumps(resumo, indent=2, ensure_ascii=False))
                salvar_master_equipe({
                    "parecer_executivo": {"texto": parecer,
                                         "gerado_em": datetime.now().strftime("%d/%m/%Y %H:%M:%S")}
                })
                st.session_state["parecer_eq_central"] = parecer
                st.success("✅ Parecer gerado!")
                st.rerun()

    with ctrl4:
        if laudo_exibir:
            st.download_button(
                "📥 Baixar Laudo",
                data=html_export_laudo(master_sel, laudo_exibir),
                file_name=f"Laudo_{colab_sel.replace(' ','_').upper()}.html",
                mime="text/html",
                use_container_width=True,
                key="ctrl_dl_laudo"
            )

    with ctrl5:
        if parecer_exibir:
            st.download_button(
                "📥 Baixar Parecer",
                data=html_export_parecer(masters, parecer_exibir,
                                         roi_total, horas_total, total_colab, cultura),
                file_name=f"Parecer_Equipe_{datetime.now().strftime('%d%m%Y')}.html",
                mime="text/html",
                use_container_width=True,
                key="ctrl_dl_parecer"
            )
