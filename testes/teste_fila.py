"""A fila de candidatos não pode crescer sem ser revista.

Este teste existe por causa de uma falha concreta e repetida: o pipeline apanhou
Gondomar, a Navigator, a ERSAR, Vimioso, a Misericórdia de Santo Tirso e o atacante
da Câmara de Chaves — e nenhum foi registado, porque ninguém reviu a fila. Todos
foram depois encontrados um a um, por alguém perguntar.

A deteção nunca falhou. Falhou a curadoria, e falhou em silêncio: uma fila que
cresce não dá erro, não parte nenhum teste, e passa despercebida indefinidamente.

Estes testes tornam o silêncio audível.
"""

from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from ingestao.comum import (  # noqa: E402
    DIR_CANDIDATOS,
    DIR_INCIDENTES,
    indice_entidades,
    ler_json,
    normalizar_entidade,
)

# Acima disto, a fila deixou de ser uma lista de trabalho e passou a ser um monte.
# O número não é arbitrário: é o que uma pessoa consegue rever numa sessão.
MAX_FILA = 90

# Um candidato mais velho do que isto sem decisão é um candidato esquecido.
MAX_DIAS_SEM_REVISAO = 30


def candidatos() -> list[dict]:
    return [ler_json(p) for p in sorted(DIR_CANDIDATOS.glob("*.json"))]


def teste_fila_nao_cresce_indefinidamente():
    fila = candidatos()
    assert len(fila) <= MAX_FILA, (
        f"a fila tem {len(fila)} candidatos por rever, acima do limite de {MAX_FILA}.\n"
        "Correr `python curar.py` e decidir. Uma fila que ninguém revê é um "
        "pipeline que produz para o vazio — foi assim que a Navigator, a ERSAR e "
        "Gondomar ficaram por registar durante meses."
    )


def teste_candidatos_de_entidades_ja_registadas_nao_ficam_na_fila():
    """Um candidato cuja entidade já tem incidente deve ter sido decidido.

    Ou acrescenta informação ao incidente existente — como a atribuição do ataque à
    Câmara de Chaves, que estava na fila e faltava na ficha — ou é ruído e vai para
    os rejeitados. Ficar na fila não é uma das opções.
    """
    registadas: set[str] = set()
    for caminho in DIR_INCIDENTES.glob("*.json"):
        incidente = ler_json(caminho)
        registadas |= set(incidente["entidades_afetadas"])
        registadas |= set(incidente.get("entidades_afetadas_em_cascata", []))

    idx = indice_entidades()
    pendentes = []
    for candidato in candidatos():
        nome = (candidato.get("extraccao") or {}).get("entidade_mencionada") or ""
        if not nome:
            continue
        eid = idx.get(normalizar_entidade(nome))
        if eid and eid in registadas:
            pendentes.append(f"{nome} → {eid}")

    assert not pendentes, (
        "há candidatos na fila cuja entidade já tem incidente registado:\n  "
        + "\n  ".join(pendentes)
        + "\nCada um ou acrescenta informação ao incidente, ou é rejeitado."
    )


def teste_candidatos_nao_apodrecem():
    """Nenhum candidato deve ficar mais de um mês sem decisão."""
    hoje = date.today()
    velhos = []
    for candidato in candidatos():
        triado = (candidato.get("triado_em") or "")[:10]
        if not triado:
            continue
        try:
            dias = (hoje - date.fromisoformat(triado)).days
        except ValueError:
            continue
        if dias > MAX_DIAS_SEM_REVISAO:
            velhos.append(f"{candidato.get('titulo_origem', candidato['id'])[:60]} ({dias} dias)")

    assert not velhos, (
        f"{len(velhos)} candidatos estão há mais de {MAX_DIAS_SEM_REVISAO} dias na "
        "fila sem decisão:\n  " + "\n  ".join(velhos[:10])
    )


def teste_dominios_resolvem_para_entidades():
    """Um domínio tem de resolver para a entidade, como o nome resolve.

    Os sites de extorsão identificam vítimas por domínio. Enquanto o índice só
    resolvia nomes, os candidatos `thenavigatorcompany.com`, `smtuc.pt`,
    `trustinnews.pt`, `portodelisboa.pt`, `aguasdoporto.pt` e `cm-vimioso.pt`
    ficaram na fila — quatro deles com o incidente já publicado — e o teste acima
    passava, porque também ele resolvia por nome. O guarda tinha o mesmo ponto cego
    daquilo que devia guardar.
    """
    from ingestao.comum import formas_de_dominio

    assert formas_de_dominio("https://www.smtuc.pt/horarios") == ["smtuc.pt", "smtuc"]
    assert formas_de_dominio("SMTUC") == []
    assert formas_de_dominio("Câmara Municipal de Vimioso") == []

    idx = indice_entidades()
    for dominio, esperado in [
        ("smtuc.pt", "smtuc"),
        ("trustinnews.pt", "trust-in-news"),
        ("thenavigatorcompany.com", "navigator"),
    ]:
        assert idx.get(normalizar_entidade(dominio)) == esperado, (
            f"{dominio} devia resolver para {esperado}"
        )
