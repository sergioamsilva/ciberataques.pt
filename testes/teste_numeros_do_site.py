"""Nenhum número visível no site pode ser escrito à mão.

A página inicial anunciou durante meses "Dez anos, marca a marca", e continuou a
anunciá-lo depois de o registo passar a cobrir de 2012 a 2026, que são quinze. O
site construía, os testes passavam, e o título mentia.

É o mesmo erro que a banda do ano de pico evitou desde o início por derivar tudo
dos dados: um número escrito num sítio e os dados noutro acabam por divergir, e
quem lê não tem como saber qual dos dois está certo.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from ingestao.comum import DIR_OUT, ler_json  # noqa: E402

PAGINAS = RAIZ / "site" / "src" / "pages"
COMPONENTES = RAIZ / "site" / "src" / "components"

# Números por extenso a par de uma unidade que o registo mede, DENTRO DE TÍTULOS.
#
# Só títulos, e de propósito. Em prosa corrida estes números são quase sempre
# legítimos — "atacado seis anos antes", "estes dois anos são os mais frágeis" —
# e proibi-los daria um teste que ninguém conseguiria satisfazer sem escrever mal.
# Num título são uma afirmação sobre o registo inteiro, e é aí que a deriva
# acontece e que ninguém repara.
PADRAO = re.compile(
    r"<h[1-3][^>]*>(?:(?!</h[1-3]>).)*?\b(dois|três|quatro|cinco|seis|sete|oito|nove|"
    r"dez|onze|doze|treze|catorze|quinze|dezasseis|dezassete|dezoito|dezanove|vinte)\s+"
    r"(anos|incidentes|fontes|setores|entidades|tipos)\b",
    re.IGNORECASE | re.S,
)


def linhas_de_markup(caminho: Path) -> list[tuple[int, str]]:
    """Só o que está fora do frontmatter e fora de comentários de bloco."""
    texto = caminho.read_text(encoding="utf-8")
    partes = texto.split("---")
    markup = partes[2] if len(partes) >= 3 else texto
    markup = re.sub(r"\{/\*.*?\*/\}", "", markup, flags=re.S)
    markup = re.sub(r"/\*.*?\*/", "", markup, flags=re.S)
    achados = []
    for m in PADRAO.finditer(markup):
        linha = markup[: m.start()].count("\n") + 1
        achados.append((linha, m.group(0)[-70:]))
    return achados


def teste_nenhum_numero_do_registo_esta_escrito_a_mao():
    achados = []
    for caminho in [*PAGINAS.rglob("*.astro"), *COMPONENTES.rglob("*.astro")]:
        for n, linha in linhas_de_markup(caminho):
            achados.append(f"{caminho.relative_to(RAIZ)}:{n}: {linha.strip()[:90]}")
    assert not achados, (
        "números do registo escritos à mão no markup:\n  "
        + "\n  ".join(achados)
        + "\nDerivar dos dados, como em amplitudeEmAnos() e porExtenso()."
    )


def teste_a_amplitude_bate_certo_com_os_dados():
    agregados = ler_json(DIR_OUT / "agregados.json")
    anos = [int(a) for a in agregados["por_ano"]]
    assert max(anos) - min(anos) + 1 == 15, (
        "a amplitude do registo mudou; o título da página inicial deriva dela e "
        "acompanha sozinho, mas vale a pena confirmar que é intencional"
    )
