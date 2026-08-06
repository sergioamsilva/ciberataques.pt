"""A ligação ao MITRE ATT&CK tem de ser verificável, e não uma etiqueta bonita.

Um identificador como G1004 ou T1486 parece muito mais autoritário do que uma frase
em prosa, e é por isso que é mais perigoso quando está errado. Estes testes garantem
que cada identificador aponta para a página que diz apontar, e que nunca começámos a
atribuir técnicas a incidentes cujas fontes não as descrevem.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from ingestao.comum import DIR_INCIDENTES, DIR_REFERENCIA, ler_json, ler_yaml  # noqa: E402

ATORES = ler_yaml(DIR_REFERENCIA / "atores.yaml")


def teste_o_identificador_bate_certo_com_a_ligacao():
    for nome, dados in ATORES["atores"].items():
        m = dados.get("mitre")
        if not m:
            continue
        esperado = "groups" if m["tipo"] == "grupo" else "software"
        padrao = rf"^https://attack\.mitre\.org/{esperado}/{re.escape(m['id'])}/$"
        assert re.match(padrao, m["url"]), (
            f"{nome}: a ligação {m['url']} não corresponde a {m['tipo']} {m['id']}"
        )
        assert m["id"][0] == ("G" if m["tipo"] == "grupo" else "S"), (
            f"{nome}: identificador {m['id']} não condiz com o tipo {m['tipo']}"
        )


def teste_todos_os_atores_do_registo_foram_procurados():
    """Um ator sem entrada aqui é um ator que ninguém foi verificar.

    Sem isto, um grupo novo entraria no registo e a ausência de ligação ao ATT&CK
    seria indistinguível de "ainda não fomos ver".
    """
    do_registo = set()
    for caminho in DIR_INCIDENTES.glob("*.json"):
        grupo = (ler_json(caminho).get("ator") or {}).get("grupo")
        if grupo:
            do_registo.add(grupo)

    # Comparação insensível a maiúsculas: o tracker escreve "akira", a MITRE
    # escreve "Akira", e não vale a pena duplicar entradas por causa disso.
    conhecidos = {k.lower() for k in ATORES["atores"]}
    por_verificar = sorted(a for a in do_registo if a.lower() not in conhecidos)
    assert not por_verificar, (
        "atores no registo sem entrada em referencia/atores.yaml:\n  "
        + "\n  ".join(por_verificar)
        + "\nProcurar em attack.mitre.org e registar o resultado, mesmo que seja "
        "`mitre: null` — a ausência também é informação."
    )


def teste_nao_atribuimos_tecnicas_a_incidentes():
    """Nenhuma ficha pode ganhar técnicas ATT&CK sem que a fonte as descreva.

    Em 83 incidentes, um menciona phishing e dois nomeiam o vetor de entrada. Se
    algum dia aparecer um campo de técnicas numa ficha, ou é sustentado por uma
    fonte indexada — e então este teste tem de ser reescrito para o exigir — ou é
    inferência disfarçada de facto.
    """
    com_tecnicas = []
    for caminho in DIR_INCIDENTES.glob("*.json"):
        incidente = ler_json(caminho)
        tecnicas = (incidente.get("ator") or {}).get("tecnicas") or incidente.get("tecnicas")
        if tecnicas:
            com_tecnicas.append(incidente["id"])
    assert not com_tecnicas, (
        f"fichas com técnicas ATT&CK: {com_tecnicas}. Se vieram de uma fonte, "
        "acrescentar o índice da fonte e reescrever este teste para o exigir."
    )
