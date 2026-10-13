#!/usr/bin/env python3
"""Transforma out/candidatas.json em documentos prontos para o banco da página.

Aplica data/ajustes.json (exclusões, mercado de empresas fora da base, edições),
completa campos (região, nota de agregador, status, referência salarial) e grava:

  out/lote/jobs/<id>.json        um arquivo por vaga nova
  out/lote/lote-<n>.json         lista de writes (até 50) para ArtifactData batch
  out/lote/termometro.json       documento meta/termometro (vagas por empresa hoje)
  out/lote/coleta.json           documento meta/coleta (resumo da varredura)
  out/lote/resumo.txt            o que entra, por função e aderência

Uso: python3 scripts/preparar_lote.py [--limite N]
"""
import argparse, datetime as dt, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import coletor as C  # reaproveita regras de referência salarial e datas

OUT = os.path.join(ROOT, "out")
LOTE = os.path.join(OUT, "lote")
TODAY = dt.date.today().isoformat()
AGREG = "Vista em agregador. Confirme no site da empresa antes de se candidatar."

def load(p, d=None):
    p = os.path.join(ROOT, p)
    return json.load(open(p, encoding="utf-8")) if os.path.exists(p) else d

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limite", type=int, default=0, help="máximo de vagas novas (0 = todas)")
    a = ap.parse_args()
    cands = load("out/candidatas.json", [])
    aj = load("data/ajustes.json", {"excluir": {}, "empresas": {}, "editar": {}})
    base = {e["id"]: e for e in load("data/empresas.json", [])}
    os.makedirs(os.path.join(LOTE, "jobs"), exist_ok=True)
    for f in os.listdir(os.path.join(LOTE, "jobs")):
        os.remove(os.path.join(LOTE, "jobs", f))

    docs = []
    for r in cands:
        k = r["key"]
        if k in aj.get("excluir", {}):
            continue
        d = {x: r.get(x, "") for x in ["title", "company", "companyId", "role", "fit", "seniority", "elig", "model", "contract",
                                        "market", "posted", "url", "source", "origin", "salary", "salaryBRL", "status", "key"]}
        d["english"] = r.get("english", "")
        d["note"] = ""
        co = base.get(r.get("companyId") or "")
        if co:
            d["region"] = co.get("markets", [])
            d["market"] = co.get("market", "intl")
        else:
            m = aj.get("empresas", {}).get(r["company"])
            d["region"] = (m or {}).get("markets", [])
            d["market"] = (m or {}).get("market", "intl")
        if r.get("alsoAt"):
            d["alsoAt"] = r["alsoAt"]
        ed = aj.get("editar", {}).get(k, {})
        d.update(ed)
        if d.get("origin") == "agregador" and AGREG not in (d.get("note") or ""):
            d["note"] = ((d.get("note") or "") + " " + AGREG).strip()
        d["bench"] = C.bench_for(d["title"], d["market"])
        if d["market"] == "br":
            d["bench"]["us"] = None
        age = C.days_since(d["posted"]) if d.get("posted") else None
        if "status" not in ed:
            d["status"] = "ativa" if d.get("origin") == "empresa" and (age is None or age <= 30) else "conferir"
        d["checkedAt"] = TODAY
        d["addedAt"] = TODAY
        d = {x: y for x, y in d.items() if y not in ("", None) or x in ("note",)}
        docs.append(("j-" + k, d))
    if a.limite:
        docs = docs[: a.limite]

    writes = []
    for i, d in docs:
        p = os.path.join(LOTE, "jobs", i + ".json")
        json.dump(d, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        writes.append({"op": "set", "collection": "jobs", "doc_id": i, "file_path": p})
    for f in os.listdir(LOTE):
        if f.startswith("lote-"):
            os.remove(os.path.join(LOTE, f))
    for n in range(0, len(writes), 50):
        json.dump(writes[n:n + 50], open(os.path.join(LOTE, f"lote-{n // 50 + 1}.json"), "w"), indent=1)

    termo = load("out/termometro.json", {})
    json.dump({"at": TODAY, "companies": {k: {"brJobs": v.get("brJobs"), "oficial": v.get("oficial"), "himalayas": v.get("himalayas")}
                                          for k, v in termo.items()}},
              open(os.path.join(LOTE, "termometro.json"), "w"), ensure_ascii=False, indent=1)

    by = {}
    for _, d in docs:
        by.setdefault(d["role"], {}).setdefault(d.get("fit", "?"), 0)
        by[d["role"]][d.get("fit", "?")] += 1
    rel = open(os.path.join(OUT, "relatorio.txt"), encoding="utf-8").read() if os.path.exists(os.path.join(OUT, "relatorio.txt")) else ""
    vistas = load("out/vistas.json", [])
    coleta = {"date": TODAY, "novas": len(docs), "vistas": len(vistas),
              "oficial": sum(1 for r in vistas if r.get("origin") == "empresa"),
              "agregador": sum(1 for r in vistas if r.get("origin") == "agregador"),
              "fontes": "Quadros oficiais (Greenhouse, Lever, Ashby, SmartRecruiters, Recruitee, Teamtailor) e Himalayas"}
    json.dump(coleta, open(os.path.join(LOTE, "coleta.json"), "w"), ensure_ascii=False, indent=1)
    lines = [f"Vagas novas prontas para o banco: {len(docs)}", "Por função e aderência: " + json.dumps(by, ensure_ascii=False),
             f"Arquivos de lote: {len(range(0, len(writes), 50))}", rel]
    open(os.path.join(LOTE, "resumo.txt"), "w", encoding="utf-8").write("\n".join(lines))
    print("\n".join(lines))

if __name__ == "__main__":
    main()
