import json,os
for f in os.listdir("master"):
    if f.endswith(".json") and f!="_EQUIPE.json":
        p=f"master/{f}"
        d=json.load(open(p,encoding="utf-8"))
        d["laudo_central"]={"texto":"","gerado_em":""}
        json.dump(d,open(p,"w",encoding="utf-8"),ensure_ascii=False,indent=4)
        print("OK",f)
