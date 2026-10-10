"""A dívida de excertos não volta a crescer em silêncio.

Em outubro de 2026 nenhuma das 219 fontes do registo tinha excerto: o campo existia
no esquema, o site sabia mostrá-lo, e ninguém o preenchia. O excerto é o que deixa o
leitor ver, sem sair da ficha, que a fonte diz o que dizemos que diz — sobretudo a
declaração da entidade em que assenta "confirmado pela entidade".

Avisa, não falha: há fontes de onde não se consegue tirar texto (paywall, páginas
desenhadas em JavaScript, servidores que recusam automatismos), e um teste que
falhasse por isso empurraria para excertos inventados, que é o pior resultado
possível. O aviso aparece no resumo do pytest a cada execução.
"""

from __future__ import annotations

import json
import warnings
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
INCIDENTES = RAIZ / "data" / "out" / "incidentes"


def teste_fichas_sem_nenhum_excerto_sao_assinaladas():
    sem = []
    for caminho in sorted(INCIDENTES.glob("*.json")):
        inc = json.loads(caminho.read_text(encoding="utf-8"))
        citaveis = [f for f in inc["fontes"] if f["tipo"] != "leak_site"]
        if citaveis and not any(f.get("excerto") for f in citaveis):
            sem.append(inc["id"])
    if sem:
        warnings.warn(
            f"{len(sem)} fichas sem nenhum excerto: {', '.join(sem[:8])}"
            + (" …" if len(sem) > 8 else ""),
            stacklevel=1,
        )


def teste_excertos_de_declaracao_estao_onde_devem():
    """Um excerto numa fonte de site de extorsão seria texto do atacante na ficha."""
    for caminho in INCIDENTES.glob("*.json"):
        inc = json.loads(caminho.read_text(encoding="utf-8"))
        for i, f in enumerate(inc["fontes"]):
            assert not (f["tipo"] == "leak_site" and f.get("excerto")), (
                f"{inc['id']} fontes[{i}]: excerto em fonte de site de extorsão"
            )
