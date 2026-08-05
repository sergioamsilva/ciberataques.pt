#!/usr/bin/env python3
"""Lista os incidentes marcados como em desenvolvimento e o que falta saber de cada um.

Serve de ponto de partida para a reverificação periódica: um incidente recente é
sempre um registo incompleto, e o valor do arquivo depende de ele ser atualizado
enquanto o caso decorre, não meses depois.

    python scripts/em_desenvolvimento.py            # legível
    python scripts/em_desenvolvimento.py --json     # para outro programa consumir
"""

from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from ingestao.comum import DIR_INCIDENTES, carregar_entidades, ler_json  # noqa: E402

ETIQUETA = "em-desenvolvimento"


def lacunas(incidente: dict) -> list[str]:
    """O que continua por saber. É isto que orienta a próxima pesquisa."""
    faltas: list[str] = []
    impacto = incidente.get("impacto") or {}
    dados = incidente.get("dados_pessoais") or {}

    if incidente["data"]["precisao"] in ("desconhecida", "semana"):
        faltas.append("data exata da ocorrência")
    if dados.get("afetados") is None:
        faltas.append("se houve dados pessoais comprometidos")
    if not incidente.get("ator", {}).get("grupo"):
        faltas.append("atribuição do ataque")
    if impacto.get("resgate_pago") is None and not impacto.get("resgate_pedido_nota"):
        faltas.append("existência de pedido de resgate")
    if not any(e["tipo"] == "reposicao" for e in incidente.get("cronologia", [])):
        faltas.append("conclusão da reposição dos serviços")
    if impacto.get("custo_declarado_eur") is None:
        faltas.append("custo declarado")
    return faltas


def recolher() -> list[dict]:
    nomes = {e["id"]: e.get("nome_curto") or e["nome"] for e in carregar_entidades()}
    saida = []
    for caminho in sorted(DIR_INCIDENTES.glob("*.json")):
        incidente = ler_json(caminho)
        if ETIQUETA not in (incidente.get("etiquetas") or []):
            continue
        revisto = date.fromisoformat(incidente["revisao"]["data"])
        saida.append(
            {
                "id": incidente["id"],
                "titulo": incidente["titulo"],
                "entidades": [nomes.get(e, e) for e in incidente["entidades_afetadas"]],
                "data": incidente["data"]["inicio"],
                "versao": incidente["revisao"]["versao"],
                "revisto_em": incidente["revisao"]["data"],
                "dias_desde_revisao": (date.today() - revisto).days,
                "n_fontes": len(incidente["fontes"]),
                "ultima_fonte": max(f["data"] for f in incidente["fontes"]),
                "lacunas": lacunas(incidente),
                "url": f"https://ciberataques.pt/incidentes/{incidente['id']}/",
            }
        )
    saida.sort(key=lambda i: i["dias_desde_revisao"], reverse=True)
    return saida


def main() -> None:
    itens = recolher()

    if "--json" in sys.argv:
        print(json.dumps(itens, ensure_ascii=False, indent=2))
        return

    if not itens:
        print("Nenhum incidente marcado como em desenvolvimento.")
        return

    print(f"{len(itens)} incidentes em desenvolvimento:\n")
    for i in itens:
        print(f"\033[1m{i['titulo']}\033[0m")
        print(f"  {i['id']}  ·  v{i['versao']}  ·  revisto há {i['dias_desde_revisao']} dias")
        print(f"  entidades: {', '.join(i['entidades'])}")
        print(f"  {i['n_fontes']} fontes, a mais recente de {i['ultima_fonte']}")
        if i["lacunas"]:
            print(f"  \033[33mpor saber:\033[0m {'; '.join(i['lacunas'])}")
        print()


if __name__ == "__main__":
    main()
