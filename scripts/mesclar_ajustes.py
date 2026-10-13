#!/usr/bin/env python3
"""Junta a curadoria guardada no banco (meta/ajustes) com data/ajustes.json.

A rotina guarda a curadoria nos dois lugares: no repositório (quando o push
funciona) e no banco da página (sempre). Este script une os dois antes da coleta,
para nenhuma exclusão se perder.

Uso: python3 scripts/mesclar_ajustes.py /tmp/banco
     (pasta com o export do ArtifactData; lê /tmp/banco/meta/ajustes.json se existir)
"""
import json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOCAL = os.path.join(ROOT, "data", "ajustes.json")

def main():
    banco = sys.argv[1] if len(sys.argv) > 1 else "/tmp/banco"
    local = json.load(open(LOCAL, encoding="utf-8")) if os.path.exists(LOCAL) else {}
    p = os.path.join(banco, "meta", "ajustes.json")
    remoto = {}
    if os.path.exists(p):
        d = json.load(open(p, encoding="utf-8"))
        remoto = d.get("data", d)
    antes = {k: len(local.get(k, {})) for k in ("excluir", "empresas", "editar")}
    for k in ("excluir", "empresas", "editar"):
        base = dict(remoto.get(k, {}))
        base.update(local.get(k, {}))
        local[k] = base
    local.setdefault("nota", remoto.get("nota", ""))
    json.dump(local, open(LOCAL, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    depois = {k: len(local[k]) for k in ("excluir", "empresas", "editar")}
    print("ajustes antes:", antes, "depois:", depois)

if __name__ == "__main__":
    main()
