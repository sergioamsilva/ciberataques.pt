"""A fonte da CNPD lê o índice, nunca os PDF, e não pode duplicar-se no catálogo.

Dois enganos concretos deram origem a estes testes.

O primeiro: a CNPD já estava no catálogo de fontes, desativada, com a nota "desativado
até haver parser". Ao escrever o parser acrescentei uma segunda entrada com o mesmo id
em vez de atualizar a que existia, e `_configuracao()` — que devolve a primeira que
encontra — continuou a devolver a desativada. A fonte parecia não funcionar quando o
que estava errado era o catálogo ter duas entradas.

O segundo é sobre o que a fonte pode prometer. Os PDF da CNPD são digitalizações sem
camada de texto: a deliberação 984/2018 tem vinte páginas de imagens em 7,7 MB, de que
o pdftotext extrai vinte bytes. Se alguém um dia acrescentar leitura de PDF a este
módulo, tem de saber que precisa de reconhecimento ótico e não de um extrator de texto.
"""

from __future__ import annotations

import collections
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from ingestao.comum import FONTES, ler_yaml  # noqa: E402
from ingestao.fontes import REGISTO  # noqa: E402
from ingestao.fontes.cnpd import CARTAO, _ano_da_deliberacao  # noqa: E402


def catalogo() -> list[dict]:
    return ler_yaml(FONTES)["fontes"]


def teste_nenhuma_fonte_esta_duplicada_no_catalogo():
    """Duas entradas com o mesmo id fazem a primeira ganhar, em silêncio."""
    contagem = collections.Counter(f["id"] for f in catalogo())
    duplicadas = [i for i, n in contagem.items() if n > 1]
    assert not duplicadas, (
        f"ids repetidos em referencia/fontes.yaml: {duplicadas}. "
        "Atualizar a entrada existente em vez de acrescentar outra."
    )


def teste_todo_o_metodo_declarado_e_conhecido():
    """Uma fonte ativa com um método que ninguém implementa nunca recolhe nada.

    Nem todos os métodos passam pelo registo de `recolher_de`: `api` designa as que
    são usadas diretamente por ingestao/arquivo.py, fora do ciclo de recolha. O que
    não pode acontecer é aparecer um método que nada no código reconheça.
    """
    conhecidos = {"rss", "api", "html", "navegador"}
    em_falta = [
        (f["id"], f.get("metodo")) for f in catalogo()
        if f.get("ativa") and f.get("metodo") not in conhecidos
    ]
    assert not em_falta, f"fontes ativas com método desconhecido: {em_falta}"


def teste_a_cnpd_esta_ativa_e_e_fonte_de_autoridade():
    cnpd = [f for f in catalogo() if f["id"] == "cnpd"]
    assert len(cnpd) == 1, f"esperada uma entrada da CNPD, há {len(cnpd)}"
    assert cnpd[0]["ativa"] is True
    assert cnpd[0]["metodo"] == "html", "a recolha é raspagem de HTML do índice"
    assert cnpd[0].get("tipo_fonte") == "regulador", (
        "uma deliberação é fonte primária de autoridade, não notícia"
    )


def teste_o_cartao_do_indice_e_reconhecido():
    """O HTML do Umbraco, na forma verificada a 2026-08-07."""
    exemplo = (
        '<div class="c-card c-card-s">\r\n'
        '    <a href="/umbraco/surface/cnpdDecision/download/122033" target="_blank">\r\n'
        '        <div class="c-card-header-medium">Delibera&#231;&#227;o 1072/2022</div>\r\n'
        '        <div class="c-card-header">CNPD</div>\r\n'
        '            <div class="c-card-text">Aplica&#231;&#227;o de san&#231;&#227;o</div>\r\n'
        "    </a>\r\n</div>"
    )
    achados = CARTAO.findall(exemplo)
    assert len(achados) == 1, "o cartão do índice deixou de ser reconhecido"
    caminho, titulo, _, _ = achados[0]
    assert caminho.endswith("/122033")
    assert "1072/2022" in titulo


def teste_o_ano_sai_do_numero_da_deliberacao():
    assert _ano_da_deliberacao("Deliberação 984/2018") == "2018"
    assert _ano_da_deliberacao("Deliberação 1072/2022") == "2022"
    assert _ano_da_deliberacao("sem número") is None
