"""O catálogo tem de cobrir os órgãos que efetivamente nos dão fontes.

Uma medição simples e incómoda, feita a 2026-08-07: 49 das 246 fontes do registo —
uma em cada cinco — vinham de domínios que não estavam no catálogo. Um quinto do que o
arquivo sabe entrou por alguém tropeçar nele, e não pela recolha.

Não é razoável exigir zero: há fontes que aparecem uma vez e não voltam, e catalogar um
órgão por causa de um artigo seria ruído. Mas um domínio que já deu VÁRIAS fontes e
continua fora do catálogo é uma lacuna de recolha, não um acaso — e é isso que este
teste vigia.

Foi assim que se descobriu que a Renascença, um órgão nacional com sete fontes no
registo, nunca tinha estado no catálogo.
"""

from __future__ import annotations

import collections
import json
import sys
from pathlib import Path
from urllib.parse import urlparse

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from ingestao.comum import DIR_INCIDENTES, FONTES, ler_json, ler_yaml  # noqa: E402

# Acima disto, um domínio deixou de ser acaso e passou a ser padrão.
MINIMO_PARA_CATALOGAR = 3

# Órgãos recorrentes que não é possível catalogar, com a razão. Uma exceção sem razão
# escrita é uma lacuna a fingir que é decisão.
SEM_FEED = {
    # Verificado a 2026-08-07: /feed, /rss, /rssFeed e /feed/rss devolvem 404, e a
    # página não declara <link rel="alternate">. Continua a ser citável à mão.
    "tsf.pt": "não publica RSS descobrível",
}


def dominios_do_catalogo() -> set[str]:
    dominios = set()
    for fonte in ler_yaml(FONTES)["fontes"]:
        for d in fonte.get("dominios", []):
            dominios.add(d.replace("www.", ""))
    return dominios


def teste_orgaos_recorrentes_estao_no_catalogo():
    catalogo = dominios_do_catalogo()
    uso: collections.Counter[str] = collections.Counter()
    for caminho in DIR_INCIDENTES.glob("*.json"):
        for fonte in ler_json(caminho)["fontes"]:
            anfitriao = urlparse(fonte["url"]).netloc.replace("www.", "")
            if anfitriao:
                uso[anfitriao] += 1

    em_falta = [
        (h, n) for h, n in uso.items()
        if n >= MINIMO_PARA_CATALOGAR
        and not any(h == d or h.endswith("." + d) for d in catalogo)
        and h not in SEM_FEED
    ]
    assert not em_falta, (
        "domínios com "
        f"{MINIMO_PARA_CATALOGAR} ou mais fontes no registo e fora do catálogo:\n  "
        + "\n  ".join(f"{h} ({n} fontes)" for h, n in sorted(em_falta, key=lambda x: -x[1]))
        + "\nSe o órgão publica sobre isto com regularidade, a recolha devia vê-lo."
    )
