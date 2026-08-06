"""Todos os setores da taxonomia têm ícone, e nenhum ícone sobra.

Um setor sem ícone deixa um buraco na listagem que ninguém repara até estar
publicado — o alinhamento mantém-se e a linha fica apenas mais pobre do que as
outras. E um ícone para um setor que já não existe é código morto que ninguém
apaga.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from ingestao.comum import carregar_taxonomia  # noqa: E402

COMPONENTE = RAIZ / "site" / "src" / "components" / "IconeSetor.astro"


def desenhados() -> set[str]:
    texto = COMPONENTE.read_text(encoding="utf-8")
    corpo = texto.split("const D: Record<string, string> = {", 1)[1].split("\n};", 1)[0]
    return set(re.findall(r"^\s{2}([a-z_]+):", corpo, re.M))


def teste_todos_os_setores_tem_icone():
    setores = set(carregar_taxonomia()["setores"])
    em_falta = sorted(setores - desenhados())
    assert not em_falta, f"setores sem ícone em IconeSetor.astro: {em_falta}"


def teste_nao_ha_icones_orfaos():
    setores = set(carregar_taxonomia()["setores"])
    orfaos = sorted(desenhados() - setores)
    assert not orfaos, f"ícones para setores que já não existem na taxonomia: {orfaos}"
