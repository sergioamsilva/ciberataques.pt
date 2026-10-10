"""Cada página partilhada tem de mostrar alguma coisa.

Até outubro de 2026, uma ficha colada no Slack de uma redação ou no X aparecia sem
imagem, e o separador do navegador sem ícone. Este teste garante que nenhuma página
volta a sair sem imagem de pré-visualização, e que a imagem que declara existe — uma
og:image a apontar para um 404 é pior do que nenhuma, porque as plataformas guardam
o erro em cache.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parent.parent
DIST = RAIZ / "site" / "dist"
SITE = "https://ciberataques.pt"

pytestmark = pytest.mark.skipif(
    not DIST.exists(), reason="site por construir: correr atualizar.py --site"
)


def _meta(texto: str, propriedade: str) -> str | None:
    m = re.search(rf'<meta (?:property|name)="{re.escape(propriedade)}" content="([^"]*)"', texto)
    return m.group(1) if m else None


def teste_todas_as_paginas_declaram_uma_imagem_que_existe():
    sem_imagem, partidas = [], []
    for f in DIST.rglob("index.html"):
        texto = f.read_text(encoding="utf-8")
        if 'name="robots" content="noindex' in texto:
            continue
        imagem = _meta(texto, "og:image")
        if not imagem:
            sem_imagem.append(str(f.relative_to(DIST)))
            continue
        assert imagem.startswith(SITE + "/"), f"{f}: og:image tem de ser absoluta"
        if not (DIST / imagem.removeprefix(SITE + "/")).is_file():
            partidas.append(imagem)
    assert not sem_imagem, f"páginas sem og:image: {sem_imagem[:5]}"
    assert not partidas, f"og:image para ficheiros inexistentes: {partidas[:5]}"


def teste_cada_ficha_tem_a_sua_propria_imagem():
    for ficha in (DIST / "incidentes").glob("*/index.html"):
        identificador = ficha.parent.name
        imagem = _meta(ficha.read_text(encoding="utf-8"), "og:image")
        assert imagem == f"{SITE}/og/incidentes/{identificador}.png", identificador


def teste_os_icones_existem():
    for nome in ("favicon.ico", "favicon.svg", "apple-touch-icon.png"):
        assert (DIST / nome).is_file(), nome
    assert (DIST / "favicon.ico").read_bytes()[:4] == b"\x00\x00\x01\x00", "favicon.ico não é um ícone"
