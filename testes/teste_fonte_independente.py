"""Nenhum incidente publicado assenta apenas na palavra de quem diz ter atacado.

Esta regra existe porque já foi ao contrário, e a correção não veio de uma discussão
de princípio: veio de uma contagem. Durante algum tempo publicaram-se vinte e sete
incidentes cuja única fonte era um site de extorsão, com o argumento de que subiriam
a caso documentado quando aparecesse fonte independente. Foram-se contar quantos
tinham subido. **Nenhum.** Zero em vinte e sete.

O que ficava, na prática, eram vinte e sete organizações nomeadas ao lado da palavra
extorsão, numa página indexável, com base na palavra de um adversário e sem que nada
disso viesse a ser confirmado por ninguém. Estão em `data/fila/alegacoes-retiradas/`,
versionadas e reversíveis: qualquer uma volta no dia em que uma fonte independente a
confirmar, e nessa altura entra pelo que essa fonte diz.

O que estes testes impedem não é o erro deliberado — quem cura sabe da regra. É o
descuido: um incidente que perde a fonte independente numa correção, uma ficha
importada à pressa, uma fonte reclassificada. A política editorial 3.1 diz a regra;
isto fá-la valer.

As fontes de sites de extorsão continuam ativas no catálogo, e é bom que continuem:
dez incidentes confirmados pelas próprias entidades citam-nas como corroboração, a
dizer quem reivindicou e quando. Nada aqui as proíbe. O que se proíbe é o incidente
que assenta só nelas.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ingestao.comum import DIR_INCIDENTES, carregar_taxonomia, ler_json  # noqa: E402


def _incidentes() -> list[tuple[str, dict]]:
    return [(c.name, ler_json(c)) for c in sorted(DIR_INCIDENTES.glob("*.json"))]


def teste_nenhum_incidente_assenta_so_em_sites_de_extorsao():
    culpados = [
        nome
        for nome, inc in _incidentes()
        if inc["fontes"] and all(f["tipo"] == "leak_site" for f in inc["fontes"])
    ]
    assert not culpados, (
        "Estes incidentes só têm fontes de sites de extorsão, e um incidente não pode "
        "assentar na palavra de quem diz ter atacado (política editorial 3.1): "
        f"{culpados}. Ou aparece fonte independente, ou a ficha sai do registo para "
        "data/fila/alegacoes-retiradas/."
    )


def teste_nenhum_incidente_publicado_esta_alegado_pelo_atacante():
    culpados = [
        nome
        for nome, inc in _incidentes()
        if inc.get("estado_confirmacao") == "alegado_pelo_atacante"
    ]
    assert not culpados, (
        "O estado 'alegado pelo atacante' não é publicável: descreve o que fica de "
        f"fora do registo, não o que está cá dentro. Encontrado em: {culpados}"
    )


def teste_a_taxonomia_declara_o_nivel_como_nao_publicavel():
    """A regra tem de estar legível onde alguém a vai procurar.

    Se um dia o nível voltar a ser publicável, isto obriga a decisão a ser explícita e
    a passar por aqui — em vez de acontecer por uma ficha que ninguém reparou.
    """
    estados = carregar_taxonomia()["estados_confirmacao"]
    assert estados["alegado_pelo_atacante"].get("publicavel") is False
    nao_publicaveis = [n for n, e in estados.items() if e.get("publicavel") is False]
    assert nao_publicaveis == ["alegado_pelo_atacante"], (
        "É o único nível não publicável da escala. Se passou a haver outro, a política "
        f"editorial tem de o dizer: {nao_publicaveis}"
    )


def teste_listagem_de_extorsao_solta_nao_chega_a_fila():
    """A regra tem de agir onde os casos nascem, e não só onde são publicados.

    Se a listagem sem par continuasse a entrar na fila, um curador acabaria por
    publicá-la um dia — a fadiga de curadoria é o modo de falha mais provável deste
    projeto, dito assim desde o primeiro dia. É mais barato não a pôr lá.
    """
    from ingestao.recolher import motivo_para_rejeitar

    motivo = motivo_para_rejeitar("leak_site", None, None, {})
    assert motivo and "3.1" in motivo


def teste_listagem_de_extorsao_com_incidente_a_que_se_ligar_passa():
    """O outro lado da regra, e a razão de o ransomware.live continuar ativo."""
    from ingestao.recolher import motivo_para_rejeitar

    sugestao = {"incidente_id": "2026-metro-mondego", "similaridade": 0.9}
    assert motivo_para_rejeitar("leak_site", sugestao, None, {}) is None


def teste_uma_noticia_sem_par_continua_a_entrar_na_fila():
    """A regra é sobre alegações de atacantes, não sobre falta de corroboração.

    Uma notícia de um único órgão é uma fonte independente e publicável — no nível
    'noticiado por uma única fonte'. Confundir as duas coisas esvaziaria o registo.
    """
    from ingestao.recolher import motivo_para_rejeitar

    assert motivo_para_rejeitar("noticia", None, None, {}) is None
    assert motivo_para_rejeitar("regulador", None, None, {}) is None


def teste_o_site_nao_tem_pagina_de_alegacoes():
    site = Path(__file__).resolve().parent.parent / "site" / "src"
    assert not (site / "pages" / "alegacoes").exists(), (
        "A página /alegacoes/ foi retirada a 8 de agosto de 2026. Publicava nomes de "
        "organizações com base apenas em alegações de atacantes, e nenhuma das vinte "
        "e sete chegou a ser confirmada."
    )
