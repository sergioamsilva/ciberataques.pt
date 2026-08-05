"""Verificações de integridade que travam a publicação.

Complementa os testes: estes correm sempre, inclusive no guião de publicação, e o
código de saída decide se o site vai ou não para o ar.

A regra é simples: se alguma destas condições falhar, o registo não é publicável.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ingestao.comum import (  # noqa: E402
    DIR_INCIDENTES,
    MAX_EXCERTO,
    carregar_entidades,
    carregar_taxonomia,
    ler_json,
)
from ingestao.construir import estado_maximo_sustentavel  # noqa: E402


def verificar() -> list[str]:
    problemas: list[str] = []
    taxonomia = carregar_taxonomia()
    entidades = {e["id"] for e in carregar_entidades()}
    pesos = taxonomia["estados_confirmacao"]
    ids = {c.stem for c in DIR_INCIDENTES.glob("*.json")}

    for caminho in sorted(DIR_INCIDENTES.glob("*.json")):
        incidente = ler_json(caminho)
        eid = incidente["id"]

        if eid != caminho.stem:
            problemas.append(f"{caminho.name}: o campo id ({eid}) não corresponde ao ficheiro")

        if not incidente.get("fontes"):
            problemas.append(f"{eid}: sem fontes; um incidente sem fontes não é publicável")

        total = len(incidente.get("fontes", []))
        for i, evento in enumerate(incidente.get("cronologia", [])):
            if not 0 <= evento["fonte"] < total:
                problemas.append(f"{eid}: cronologia[{i}] cita uma fonte inexistente")

        for i, fonte in enumerate(incidente.get("fontes", [])):
            excerto = fonte.get("excerto")
            if excerto and len(excerto) > MAX_EXCERTO:
                problemas.append(
                    f"{eid}: fontes[{i}] tem excerto de {len(excerto)} caracteres "
                    f"(máximo {MAX_EXCERTO}, imposto pelo direito de citação)"
                )
            if ".onion" in fonte.get("url", ""):
                problemas.append(f"{eid}: fontes[{i}] liga a um endereço .onion")

        declarado = incidente["estado_confirmacao"]
        if declarado != "desmentido":
            maximo = estado_maximo_sustentavel(incidente, taxonomia)
            if pesos[declarado]["peso"] < pesos[maximo]["peso"]:
                problemas.append(
                    f"{eid}: declara '{declarado}' mas as fontes só sustentam '{maximo}'"
                )

        desconhecidas = (
            set(incidente["entidades_afetadas"])
            | set(incidente.get("entidades_afetadas_em_cascata", []))
        ) - entidades
        if desconhecidas:
            problemas.append(
                f"{eid}: entidades ausentes de entidades.yaml: {sorted(desconhecidas)}"
            )

        for outro in incidente.get("relacionados", []):
            if outro not in ids:
                problemas.append(f"{eid}: relacionado inexistente '{outro}'")

    return problemas


if __name__ == "__main__":
    problemas = verificar()
    if problemas:
        print(f"\033[31m{len(problemas)} problemas impedem a publicação:\033[0m")
        for p in problemas:
            print(f"  {p}")
        sys.exit(1)
    print("  registo íntegro")
