import json, os

pasta = "master"
for arquivo in os.listdir(pasta):
    if arquivo.endswith(".json") and arquivo != "_EQUIPE.json":
        caminho = os.path.join(pasta, arquivo)
        with open(caminho, encoding="utf-8") as f:
            d = json.load(f)
        d["laudo_central"] = {"texto": "", "gerado_em": ""}
        with open(caminho, "w", encoding="utf-8") as f:
            json.dump(d, f, ensure_ascii=False, indent=4)
        print(f"✅ {arquivo} — laudo zerado")