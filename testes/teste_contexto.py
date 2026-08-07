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


def teste_a_desagregacao_por_setor_diz_de_onde_vem():
    """Misturar CERT.PT com CNPD sem o dizer seria a pior coisa que este ficheiro faz.

    Para 2024 o relatório do CERT.PT descreve os setores em palavras e não em
    percentagens. Os únicos números com desagregação são os das notificações de
    violação de dados à CNPD, que medem outra coisa: o que as entidades comunicaram à
    autoridade de proteção de dados, e não o que o CERT.PT registou.

    Inventar percentagens do CERT.PT a partir de "subiram a energia e a administração
    local" seria exatamente o que este projeto existe para não fazer.
    """
    cncs = ler_yaml(DIR_REFERENCIA / "cncs.yaml")
    for ano, dados in cncs["anos"].items():
        setores = dados.get("setores")
        if not setores:
            continue
        assert setores.get("origem"), f"{ano}: desagregação por setor sem origem declarada"
        assert setores.get("unidade"), f"{ano}: desagregação sem unidade declarada"
        assert setores.get("valores"), f"{ano}: desagregação sem valores"
        for setor, pct in setores["valores"].items():
            assert 0 < pct <= 100, f"{ano}/{setor}: percentagem implausível ({pct})"


def teste_os_setores_da_desagregacao_existem_na_taxonomia():
    """Uma percentagem oficial atribuída a um setor que o registo não usa nunca
    apareceria em página nenhuma, e ninguém daria por isso."""
    from ingestao.comum import carregar_taxonomia

    validos = set(carregar_taxonomia()["setores"])
    cncs = ler_yaml(DIR_REFERENCIA / "cncs.yaml")
    for ano, dados in cncs["anos"].items():
        for setor in (dados.get("setores") or {}).get("valores", {}):
            assert setor in validos, f"{ano}: '{setor}' não existe em taxonomia.yaml"
