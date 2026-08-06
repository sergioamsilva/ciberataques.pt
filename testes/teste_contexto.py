"""O denominador oficial não pode contaminar as contagens do registo.

O contexto.json traz números do CERT.PT: outra entidade, outro universo, outra
metodologia. São publicados ao lado dos nossos precisamente para se verem as duas
coisas separadas, e o pior que lhes pode acontecer é alguém somá-los aos nossos por
distração ao ler o JSON. A separação é estrutural — ficheiro à parte — e estes
testes impedem que deixe de o ser.
"""

from __future__ import annotations

import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from ingestao.comum import DIR_OUT, DIR_REFERENCIA, ler_json, ler_yaml  # noqa: E402

OBRIGATORIOS = ("incidentes", "edicao", "url", "citacao")


def teste_cada_ano_diz_de_onde_veio():
    """Um número oficial sem a edição e a citação de onde saiu não é verificável."""
    cncs = ler_yaml(DIR_REFERENCIA / "cncs.yaml")
    for ano, dados in cncs["anos"].items():
        em_falta = [c for c in OBRIGATORIOS if not dados.get(c)]
        assert not em_falta, f"{ano}: falta {em_falta}"
        assert isinstance(dados["incidentes"], int) and dados["incidentes"] > 0
        assert dados["url"].startswith("https://"), f"{ano}: ligação insegura ou relativa"


def teste_o_contexto_nao_entra_nos_agregados():
    """As contagens do CERT.PT não podem aparecer em agregados.json."""
    agregados = ler_json(DIR_OUT / "agregados.json")
    proibidos = {"cert_pt", "contexto", "cncs", "comparacao"}
    intrusos = proibidos & set(agregados)
    assert not intrusos, (
        f"agregados.json passou a conter {intrusos}. O denominador oficial vive em "
        "contexto.json e não se mistura com as contagens do registo."
    )


def teste_a_comparacao_usa_a_contagem_real_do_registo():
    """O 'neste_registo' tem de bater com os incidentes efetivamente publicados."""
    contexto = ler_json(DIR_OUT / "contexto.json")
    incidentes = ler_json(DIR_OUT / "incidentes.json")
    por_ano: dict[int, int] = {}
    for r in incidentes:
        por_ano[r["ano"]] = por_ano.get(r["ano"], 0) + 1

    for ano, c in contexto["comparacao"].items():
        esperado = por_ano.get(int(ano), 0)
        assert c["neste_registo"] == esperado, (
            f"{ano}: contexto diz {c['neste_registo']} incidentes nossos, "
            f"o registo tem {esperado}"
        )


def teste_o_registo_nunca_supera_o_oficial_sem_alguem_reparar():
    """Um sinal de erro: mais incidentes nossos do que o total oficial do ano.

    Não é impossível em teoria — contamos coisas diferentes — mas na prática seria
    quase de certeza um engano de curadoria ou uma leitura errada do relatório.
    """
    contexto = ler_json(DIR_OUT / "contexto.json")
    suspeitos = [
        ano for ano, c in contexto["comparacao"].items() if c["neste_registo"] > c["cert_pt"]
    ]
    assert not suspeitos, f"anos com mais incidentes nossos do que oficiais: {suspeitos}"
