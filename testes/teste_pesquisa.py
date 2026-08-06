"""O índice de pesquisa tem de existir e cobrir o registo inteiro.

A pesquisa é requisito do produto, não um extra: um arquivo que não se pesquisa não
serve jornalistas nem académicos. E falha em silêncio — o Astro constrói, as páginas
servem-se, e só quem escrever na caixa descobre que não há índice nenhum, porque o
`astro build` limpa o dist e o Pagefind corre num passo à parte.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parent.parent
PAGEFIND = RAIZ / "site" / "dist" / "pagefind"

pytestmark = pytest.mark.skipif(
    not PAGEFIND.exists(),
    reason="índice por construir: correr atualizar.py --site",
)


def entrada() -> dict:
    return json.loads((PAGEFIND / "pagefind-entry.json").read_text(encoding="utf-8"))


def teste_o_indice_existe_e_esta_em_portugues():
    linguas = entrada()["languages"]
    assert "pt-pt" in linguas, f"o índice não está em pt-PT: {list(linguas)}"


def teste_indexa_todos_os_incidentes_com_ficha():
    """O número de páginas indexadas tem de bater com as fichas construídas."""
    fichas = len(list((RAIZ / "site" / "dist" / "incidentes").glob("*/index.html")))
    indexadas = entrada()["languages"]["pt-pt"]["page_count"]
    assert indexadas >= fichas, (
        f"o índice tem {indexadas} páginas e há {fichas} fichas de incidente. "
        "Alguma coisa deixou de ter data-pagefind-body."
    )


def teste_os_ficheiros_que_a_pagina_de_pesquisa_pede_existem():
    """Sem estes a caixa de pesquisa não faz nada, e não dá erro visível."""
    pesquisa = (RAIZ / "site" / "src" / "pages" / "pesquisa.astro").read_text(encoding="utf-8")
    import re

    pedidos = set(re.findall(r'"/pagefind/([^"]+)"', pesquisa))
    assert pedidos, "a página de pesquisa não referencia nenhum ficheiro do Pagefind"
    em_falta = [f for f in pedidos if not (PAGEFIND / f).exists()]
    assert not em_falta, f"a página de pesquisa pede ficheiros que o Pagefind não gera: {em_falta}"


def teste_os_filtros_facetados_foram_gerados():
    """Cinco facetas: ano, setor, tipo, confirmação e ator."""
    filtros = list((PAGEFIND / "filter").glob("*.pf_filter"))
    assert len(filtros) >= 5, f"só foram gerados {len(filtros)} filtros facetados"
