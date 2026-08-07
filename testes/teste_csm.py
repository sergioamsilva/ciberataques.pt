"""A fonte do CSM é ferramenta de curador, e a pesquisa só funciona de uma maneira.

Três coisas custaram a descobrir e nenhuma dá erro quando está errada — que é o que
justifica testá-las.

A pesquisa **tem de ser GET**. O mesmo pedido por POST devolve 200, com JSON válido e
343 876 registos: a base inteira, com o filtro ignorado em silêncio. É o pior modo de
falha possível, o que responde com sucesso e resultados errados.

O campo **é `filter_descriptors`**. O de pesquisa livre, `freesearch`, devolve zero
para termos que existem nos descritores.

E a fonte **não entra na recolha automática**. Medido sobre 73 acórdãos: 22 passam a
triagem e nenhum é um ataque a uma organização — são crimes contra pessoas, segredo
bancário e doutrina sobre elementos típicos. Alimentar a fila com isso seria trinta por
cento de ruído para um curador rejeitar à mão.
"""

from __future__ import annotations

import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from ingestao.fontes.csm import DESCRITORES, _data_iso, _texto  # noqa: E402
from ingestao.recolher import FONTES_ATIVAS  # noqa: E402


def teste_a_pesquisa_e_por_get_e_por_descritor():
    fonte = (RAIZ / "ingestao" / "fontes" / "csm.py").read_text(encoding="utf-8")
    assert "sessao.get(" in fonte and "sessao.post(" not in fonte, (
        "a pesquisa do CSM tem de ser GET: por POST o servidor responde 200 com a "
        "base inteira e o filtro ignorado, sem erro nenhum"
    )
    assert "queries[filter_descriptors]" in fonte, (
        "o campo é filter_descriptors; freesearch devolve zero para termos que existem"
    )


def teste_nao_alimenta_a_recolha_automatica():
    """22 em 73 passam a triagem e nenhum é ataque a organização."""
    assert "csm-jurisprudencia" not in FONTES_ATIVAS, (
        "o CSM não entra na recolha automática: é ferramenta de curador, para procurar "
        "a decisão judicial de um caso concreto. Ver o cabeçalho de ingestao/fontes/csm.py."
    )


def teste_os_descritores_sao_as_infracoes_da_lei_do_cibercrime():
    for esperado in ("FALSIDADE INFORMÁTICA", "ACESSO ILEGÍTIMO", "SABOTAGEM INFORMÁTICA"):
        assert esperado in DESCRITORES


def teste_a_data_do_acordao_fica_em_iso():
    assert _data_iso("27/01/2022") == "2022-01-27"
    assert _data_iso("") is None
    assert _data_iso("data estranha") is None


def teste_o_texto_perde_o_html_e_as_entidades():
    assert _texto("<b>Ac&oacute;rd&atilde;o</b>  do   STJ") == "Acórdão do STJ"
    assert _texto(None) == ""
