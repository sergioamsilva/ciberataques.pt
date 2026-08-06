"""A triagem tem de reconhecer a administração local, e não só a nacional.

Nasce de uma falha concreta: uma notícia intitulada "Página de Facebook da Junta
de Freguesia de Águeda alvo de ataque informático" foi rejeitada pela triagem com
o motivo "sem marcador português".

O léxico conhecia o CNCS, a CNPD, a Polícia Judiciária e a Autoridade Tributária,
e não conhecia nenhuma das 3091 freguesias do país. Reproduzia, dentro do código,
exatamente o viés que este registo critica na imprensa: as instituições nacionais
são legíveis, as locais não são.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from ingestao.fontes import Item  # noqa: E402
from ingestao.triagem import triar  # noqa: E402


def noticia(titulo: str, texto: str) -> Item:
    return Item(
        url="https://exemplo.pt/a",
        url_canonica="https://exemplo.pt/a",
        titulo=titulo,
        publicador="imprensa local",
        data_publicacao="2026-06-22",
        texto=texto,
        fonte="rss_media",
        obtido_em="2026-06-22T10:00:00+00:00",
        tipo_fonte="noticia",
        extra={},
    )


@pytest.mark.parametrize(
    "titulo",
    [
        "Página de Facebook da Junta de Freguesia de Águeda alvo de ataque informático",
        "União de Freguesias de Alcabideche alvo de ataque informático",
        "Assembleia de Freguesia sem sistemas após ataque informático",
    ],
)
def teste_a_camada_da_freguesia_passa_a_triagem(titulo):
    resultado = triar(noticia(titulo, "A entidade confirmou o ataque informático aos seus sistemas."))
    assert resultado.passa, f"rejeitado: {resultado.razao}"


def teste_um_caso_estrangeiro_continua_a_ser_rejeitado():
    """Alargar o léxico não pode abrir a porta a casos de fora."""
    resultado = triar(
        noticia(
            "Prefeitura sofre ataque informático",
            "A prefeitura brasileira confirmou um ataque informático aos seus sistemas.",
        )
    )
    assert not resultado.passa, "um caso brasileiro passou a triagem"


def teste_o_gazeteiro_dos_concelhos_esta_completo_e_sem_o_ambiguo():
    """307 dos 308 concelhos, e a ausência do 308.º é deliberada.

    A triagem conhecia nove nomes de lugares portugueses num registo que aspira a
    cobrir 308 municípios, e por isso o título "Junta de São Salvador, em Ílhavo,
    foi alvo de ataque informático" não continha um único marcador português.

    Falta Cuba, no distrito de Beja: é o único concelho cujo nome é também o de um
    país, e apanharia notícias de Havana. Se alguém o acrescentar sem pensar, este
    teste explica porque não deve.
    """
    from ingestao.comum import DIR_REFERENCIA, ler_yaml

    lex = ler_yaml(DIR_REFERENCIA / "triagem.yaml")
    concelhos = lex["concelhos"]
    assert len(concelhos) == 307, f"esperados 307 concelhos, há {len(concelhos)}"
    assert "Cuba" not in concelhos, (
        "Cuba foi acrescentada ao gazeteiro. É o único concelho cujo nome é também o "
        "de um país: 'ataque informático em Cuba' passaria a apanhar Havana."
    )
    for esperado in ("Ílhavo", "Santa Comba Dão", "Marco de Canaveses", "Estremoz", "Serpa"):
        assert esperado in concelhos, f"{esperado} em falta no gazeteiro"
