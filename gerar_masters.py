"""
GERADOR DE MASTERS — NETEXAME
Lê todos os JSONs de /dados/ e gera /master/NOME.json para cada colaborador.
Execute na pasta raiz do projeto: python gerar_masters.py
"""

import json
import os

PASTA_DADOS  = "dados"
PASTA_MASTER = "master"

os.makedirs(PASTA_MASTER, exist_ok=True)

# ── Mapeamento de frequência para multiplicador anual ──────────
MULT = {"D": 220, "S": 48, "Q": 24, "M": 12, "T": 4, "A": 1}
# DVD não existe no sistema original — cai no default 12 (Mensal)
DIVISOR_DIA = {"DVD": 1, "D": 1, "S": 5, "Q": 10, "M": 20, "T": 60, "A": 240}
CUSTO_HORA = 35.0

def extrair_num(texto, padrao="h"):
    """Extrai número de strings como '2 h' ou '30 min'."""
    try:
        return float(str(texto).lower()
                     .replace("h", "").replace("min", "")
                     .replace(",", ".").strip() or 0)
    except:
        return 0.0

def calcular_roi(sugestoes):
    """Calcula ROI auditado das sugestões."""
    total_h = 0.0
    total_rs = 0.0
    auditadas = []

    for s in sugestoes:
        texto = str(s.get("Sugestão", "")).lower()
        if not texto or texto in ["nenhuma", "nada", "n/a", ""]:
            continue

        h = extrair_num(s.get("Horas", 0))
        m = extrair_num(s.get("Minutos", 0))
        freq = str(s.get("Frequência", "M")).upper().strip()
        mult = MULT.get(freq, 12)

        if any(w in texto for w in ["sistema", "automacao", "ia", "integrar",
                                     "digitalizar", "api", "robo", "python"]):
            potencial = 0.85
            estrategia = "TRANSFORMACAO DIGITAL"
        elif any(w in texto for w in ["padronizar", "checklist", "treinamento",
                                       "pop", "manual", "procedimento"]):
            potencial = 0.45
            estrategia = "OTIMIZACAO DE PROCESSO"
        else:
            potencial = 0.20
            estrategia = "MELHORIA INCREMENTAL"

        h_ano = ((h + m / 60) * mult) * potencial
        rs = h_ano * CUSTO_HORA
        total_h  += h_ano
        total_rs += rs

        auditadas.append({
            "ESTRATEGIA": estrategia,
            "SUGESTAO ANALISADA": s.get("Sugestão", "")[:120].upper(),
            "ECONOMIA PROJETADA": f"- {h_ano:.1f} h/ano",
            "VALOR RECUPERAVEL": f"R$ {rs:,.2f}"
        })

    return round(total_h, 2), round(total_rs, 2), auditadas

def calcular_carga(tabelas):
    """Calcula horas/dia totais das atividades."""
    total = 0.0
    atividades = []

    for cat in ["alta", "normal", "baixa", "dificuldades"]:
        for item in tabelas.get(cat, []):
            desc = (item.get("Atividade") or item.get("Dificuldade") or "")
            if not str(desc).strip():
                continue
            h = extrair_num(item.get("Horas", 0))
            m = extrair_num(item.get("Minutos", 0))
            freq = str(item.get("Frequência", "D")).upper().strip()
            div = DIVISOR_DIA.get(freq, 1)
            impacto = (h + m / 60) / div
            total += impacto
            atividades.append({
                "Status": "✅",
                "Atividade": str(desc)[:100],
                "Impacto": f"{impacto:.3f} h/dia",
                "Analise Critica": "Aguardando auditoria — dados do formulário"
            })

    return round(total, 2), atividades

def calcular_disc(respostas_raw):
    """Calcula percentuais DISC a partir das respostas brutas."""
    mapa = {"A": "D", "B": "I", "C": "S", "D": "C"}
    contagem = {"D": 0, "I": 0, "S": 0, "C": 0}
    for v in respostas_raw.values():
        letra = mapa.get(str(v).upper(), "")
        if letra in contagem:
            contagem[letra] += 1
    total = sum(contagem.values())
    if total == 0:
        return {"D": 25, "I": 25, "S": 25, "C": 25}, "N/A"
    pct = {k: round((v / total) * 100) for k, v in contagem.items()}
    dominante = max(pct, key=pct.get)
    return pct, dominante

def processar_colaborador(caminho):
    """Processa um JSON de /dados/ e retorna o master."""
    with open(caminho, "r", encoding="utf-8") as f:
        dados = json.load(f)

    nome     = dados.get("colaborador") or dados.get("nome") or "Desconhecido"
    campos   = dados.get("campos", {})
    tabelas  = dados.get("tabelas", {})
    disc_raw = dados.get("disc", {})

    # ── ROI ───────────────────────────────────────────────────
    sugestoes = tabelas.get("sugestoes", [])
    h_rec, rs_aud, sugs_aud = calcular_roi(sugestoes)

    # ROI bruto (sem ponderação)
    rs_bruto = 0.0
    for s in sugestoes:
        h = extrair_num(s.get("Horas", 0))
        m = extrair_num(s.get("Minutos", 0))
        freq = str(s.get("Frequência", "M")).upper().strip()
        mult = MULT.get(freq, 12)
        rs_bruto += (h + m / 60) * mult * CUSTO_HORA

    # ── CARGA HORÁRIA ──────────────────────────────────────────
    h_dia, atividades_audit = calcular_carga(tabelas)
    if h_dia > 9:
        status_carga = "sobrecarga"
    elif h_dia < 5:
        status_carga = "subutilizado"
    else:
        status_carga = "adequado"

    # Score nexo causal
    desvio = abs(h_dia - 8.0)
    score_nexo = max(0, min(100, round(100 - (desvio * 6), 1)))

    # ── DISC ───────────────────────────────────────────────────
    if disc_raw:
        pct_disc, dominante = calcular_disc(disc_raw)
        valores = sorted(pct_disc.values(), reverse=True)
        amplitude = round(valores[0] - valores[-1], 1)
        equilibrado = amplitude <= 12
    else:
        pct_disc   = {"D": 25, "I": 25, "S": 25, "C": 25}
        dominante  = "N/A"
        amplitude  = 0.0
        equilibrado = True

    # ── BENCHMARK E ADERÊNCIA POR CARGO ───────────────────────
    cargo_lower = str(campos.get("cargo", "")).lower()
    benchmarks = {
        "gestor":              {"perfis": "D/I",  "letras": ["D","I"]},
        "vendas":              {"perfis": "I-D",  "letras": ["I","D"]},
        "analista":            {"perfis": "C-S",  "letras": ["C","S"]},
        "auxiliar":            {"perfis": "S-C",  "letras": ["S","C"]},
        "assistente":          {"perfis": "S-C",  "letras": ["S","C"]},
        "coordenador":         {"perfis": "D-C",  "letras": ["D","C"]},
        "supervisor":          {"perfis": "D-S",  "letras": ["D","S"]},
        "rh":                  {"perfis": "S-I",  "letras": ["S","I"]},
        "ti":                  {"perfis": "C-D",  "letras": ["C","D"]},
        "financeiro":          {"perfis": "C-S",  "letras": ["C","S"]},
        "contabil":            {"perfis": "C-S",  "letras": ["C","S"]},
        "dp":                  {"perfis": "C-S",  "letras": ["C","S"]},
        "departamento pessoal":{"perfis": "C-S",  "letras": ["C","S"]},
        "operacional":         {"perfis": "S-D",  "letras": ["S","D"]},
        "comercial":           {"perfis": "D-I",  "letras": ["D","I"]},
        "juridico":            {"perfis": "C-S",  "letras": ["C","S"]},
        "fiscal":              {"perfis": "C-S",  "letras": ["C","S"]},
    }
    benchmark_cargo    = "N/A"
    veredito_aderencia = "Aguardando analise DISC completa"
    score_alinhamento  = 0
    perfil_exigido     = "N/A"
    for chave, bench in benchmarks.items():
        if chave in cargo_lower:
            benchmark_cargo  = bench["perfis"]
            perfil_exigido   = bench["perfis"]
            letras_esperadas = bench["letras"]
            letra_principal  = dominante[0] if dominante and dominante != "N/A" else ""
            if letra_principal in letras_esperadas[:1]:
                veredito_aderencia = "Alta Aderencia"
                score_alinhamento  = 80
            elif letra_principal in letras_esperadas:
                veredito_aderencia = "Aderencia Moderada"
                score_alinhamento  = 55
            else:
                veredito_aderencia = "Baixa Aderencia"
                score_alinhamento  = 30
            break

    # ── GARGALOS ───────────────────────────────────────────────
    gargalos = []
    for d in tabelas.get("dificuldades", []):
        desc = str(d.get("Dificuldade", "")).strip()
        if not desc:
            continue
        h = extrair_num(d.get("Horas", 0))
        m = extrair_num(d.get("Minutos", 0))
        freq = str(d.get("Frequência", "M")).upper().strip()
        div = DIVISOR_DIA.get(freq, 20)
        imp = round((h + m / 60) / div, 3)
        gargalos.append({
            "Status": "✅",
            "Setor": str(d.get("Setor Envolvido", "N/A")).upper(),
            "Dificuldade": desc[:150],
            "Impacto Diario": f"{imp} h/dia",
            "Analise do Perito": "Aguardando auditoria de nexo causal"
        })

    # ── CARREGA MASTER EXISTENTE PARA MERGE ───────────────────
    nome_limpo_tmp = str(nome).upper().strip().replace(" ", "_").replace("/", "_")
    destino_tmp    = os.path.join(PASTA_MASTER, f"{nome_limpo_tmp}.json")
    if os.path.exists(destino_tmp):
        with open(destino_tmp, encoding="utf-8") as f_ex:
            master_existente = json.load(f_ex)
    else:
        master_existente = {}

    # ── MONTA O MASTER ─────────────────────────────────────────
    master = {
        "colaborador": str(nome).upper().strip(),
        "criado_em":   dados.get("timestamp", ""),
        "campos": {
            "cargo":        campos.get("cargo", "N/A"),
            "dep":          campos.get("dep", campos.get("departamento", "N/A")),
            "setor":        campos.get("setor", "N/A"),
            "chefe":        campos.get("chefe", "N/A"),
            "unidade":      campos.get("unidade", "N/A"),
            "escolaridade": campos.get("escolaridade", "N/A"),
            "cursos":       campos.get("cursos", ""),
            "objetivo":     campos.get("objetivo", "")
        },
        "roi": {
            "auditado":           rs_aud,
            "bruto":              round(rs_bruto, 2),
            "horas_recuperaveis": h_rec,
            "ganho_dias":         round(h_rec / 8, 1) if h_rec else 0,
            "custo_hora":         CUSTO_HORA
        },
        "nexo_causal": {
            "score":     score_nexo,
            "horas_dia": h_dia,
            "status":    status_carga
        },
        "disc": {
            "percentuais":            pct_disc,
            "perfil_dominante":       dominante,
            "score_intensidade":      0,
            "amplitude":              amplitude,
            "is_equilibrado":         equilibrado,
            "perfil_exigido_tarefas":  perfil_exigido,
            "compatibilidade_pct":     "N/A",
            "score_alinhamento_cargo": score_alinhamento,
            "benchmark_cargo":         benchmark_cargo,
            "veredito_aderencia":      veredito_aderencia
        },
        "sugestoes_auditadas":   sugs_aud,
        "gargalos":              gargalos,
        "auditoria_atividades":  atividades_audit,
        "parecer":               master_existente.get("parecer", {}),
        "parecer_360":           master_existente.get("parecer_360", {}),
        "kpis_auditados":        master_existente.get("kpis_auditados", {}),
        "produtividade":         master_existente.get("produtividade", {
            "eficiencia_real_pct":  0,
            "kpis_auditados_total": 0,
            "kpi_critico":          "Aguardando auditoria de KPIs",
            "kpi_critico_score":    0
        }),
        "evidencias_kpi":        master_existente.get("evidencias_kpi", {}),
        "comparativo_cargo":     master_existente.get("comparativo_cargo", {}),
        "laudo_central":         master_existente.get("laudo_central", {
            "texto":     "",
            "gerado_em": ""
        }),
        "ultima_atualizacao": ""
    }

    return master, str(nome).upper().strip()


# ── MAIN ───────────────────────────────────────────────────────
arquivos = [f for f in os.listdir(PASTA_DADOS) if f.endswith(".json")]
print(f"\n🔄 Processando {len(arquivos)} colaboradores...\n")

gerados = []
erros   = []

for arquivo in arquivos:
    caminho = os.path.join(PASTA_DADOS, arquivo)
    try:
        master, nome = processar_colaborador(caminho)
        nome_limpo   = nome.replace(" ", "_").replace("/", "_")
        destino      = os.path.join(PASTA_MASTER, f"{nome_limpo}.json")

        with open(destino, "w", encoding="utf-8") as f:
            json.dump(master, f, ensure_ascii=False, indent=4)

        roi = master["roi"]["auditado"]
        h   = master["nexo_causal"]["horas_dia"]
        st  = master["nexo_causal"]["status"]
        disc = master["disc"]["perfil_dominante"]

        print(f"  ✅ {nome:<35} | ROI: R$ {roi:>8,.2f} | {h:.1f}h/dia | {st:<12} | DISC: {disc}")
        gerados.append(nome)

    except Exception as e:
        print(f"  ❌ {arquivo} — Erro: {e}")
        erros.append(arquivo)

print(f"\n{'─'*70}")
print(f"✅ {len(gerados)} masters gerados em /master/")
if erros:
    print(f"❌ {len(erros)} erros: {erros}")
print(f"\nPróximo passo:")
print(f"  git add master/ && git commit -m 'feat: masters gerados para todos os colaboradores' && git push")
