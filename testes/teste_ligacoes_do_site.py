"""Nenhuma página construída pode ligar para uma página que não existe.

Este teste nasce de uma alteração legítima que partiu 28 ligações em silêncio: ao
retirar as fichas individuais das alegações não confirmadas, cinco páginas
continuaram a produzir cartões que apontavam para elas. O site construía sem erro,
os testes passavam, e o leitor encontrava 404.

Um arquivo cuja credibilidade assenta em ligações não pode descobrir isto por
alguém tropeçar.
"""

from __future__ import annotations

import os
import re
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parent.parent
DIST = RAIZ / "site" / "dist"


def paginas_construidas() -> set[str]:
    paginas = {"/"}
    for f in DIST.rglob("index.html"):
        rel = "/" + str(f.relative_to(DIST)).replace("index.html", "")
        paginas.add(rel if rel.endswith("/") else rel + "/")
    return paginas


@pytest.mark.skipif(not DIST.exists(), reason="site por construir: correr atualizar.py --site")
def teste_nenhuma_ligacao_interna_aponta_para_o_vazio():
    paginas = paginas_construidas()
    partidas: dict[str, set[str]] = {}
    for f in DIST.rglob("*.html"):
        texto = f.read_text(encoding="utf-8")
        for href in set(re.findall(r'href="(/[^"#?]*)"', texto)):
            alvo = href if href.endswith("/") else href + "/"
            if alvo in paginas:
                continue
            # Ficheiros servidos diretamente: .json, .csv, .xml.
            if (DIST / href.lstrip("/")).exists():
                continue
            # /pagefind/ é escrito num passo posterior ao do Astro, que limpa o dist.
            # Consoante o momento em que este teste corra, a pasta existe ou não, e a
            # sua ausência não é uma ligação partida — é uma ordem de construção.
            # Quem garante que o índice existe é teste_pesquisa.py.
            if href.startswith("/pagefind/"):
                continue
            partidas.setdefault(href, set()).add(str(f.relative_to(DIST)))

    assert not partidas, "ligações internas para páginas inexistentes:\n  " + "\n  ".join(
        f"{href} ← {', '.join(sorted(onde)[:3])}" for href, onde in sorted(partidas.items())[:20]
    )


# --------------------------------------------------- ligações dentro do código

def _exportacoes(caminho: Path) -> set[str]:
    texto = caminho.read_text()
    nomes = set(re.findall(r"^export\s+(?:async\s+)?function\s+(\w+)", texto, re.M))
    nomes |= set(re.findall(r"^export\s+(?:const|let|type|interface)\s+(\w+)", texto, re.M))
    return nomes


def teste_nenhuma_pagina_importa_o_que_ja_nao_existe():
    """Um import de um nome inexistente não faz o build de Astro falhar.

    Descoberto ao retirar as alegações: `incidentes/index.astro` continuou a importar
    `documentados` e `alegacoes` depois de as duas desaparecerem de `dados.ts`. O
    site construiu sem uma queixa, porque o nome fica apenas `undefined` — e só
    rebentaria no dia em que alguém voltasse a chamá-lo.

    Sem verificação de tipos instalada, é isto que apanha o resíduo de uma remoção.
    """
    origem = RAIZ / "site" / "src"
    modulos = {c.stem: _exportacoes(c) for c in (origem / "lib").glob("*.ts")}
    problemas = []
    for ficheiro in list(origem.rglob("*.astro")) + list(origem.rglob("*.ts")):
        for nomes, modulo in re.findall(
            r'import\s*\{([^}]+)\}\s*from\s*"([^"]+)"', ficheiro.read_text()
        ):
            alvo = modulo.rsplit("/", 1)[-1]
            if alvo not in modulos:
                continue
            for nome in nomes.split(","):
                nome = nome.strip().removeprefix("type ").split(" as ")[0].strip()
                if nome and nome not in modulos[alvo]:
                    problemas.append(
                        f"{ficheiro.relative_to(origem)} importa '{nome}' de {alvo}, "
                        "que não o exporta"
                    )
    assert not problemas, "\n".join(problemas)
