import json, os

pasta_ev     = "evidencias"
pasta_master = "master"

for arquivo in os.listdir(pasta_ev):
    if not arquivo.endswith(".json"):
        continue

    nome_limpo = arquivo.replace(".json", "")
    nome_colab = nome_limpo.replace("_", " ").upper()

    with open(f"{pasta_ev}/{arquivo}", encoding="utf-8") as f:
        evidencias = json.load(f)

    ev_dict = {e['kpi']: e['evidencias'] for e in evidencias if 'kpi' in e}

    master_path = f"{pasta_master}/{nome_limpo}.json"
    if not os.path.exists(master_path):
        print(f"❌ Master não encontrado: {nome_limpo}")
        continue

    with open(master_path, encoding="utf-8") as f:
        master = json.load(f)

    master["evidencias_kpi"] = {
        "documentos_por_kpi": ev_dict,
        "total_kpis": len(ev_dict),
        "gerado_em": "09/05/2026 18:30:00"
    }

    with open(master_path, "w", encoding="utf-8") as f:
        json.dump(master, f, ensure_ascii=False, indent=4)

    print(f"✅ {nome_colab} — {len(ev_dict)} KPIs")