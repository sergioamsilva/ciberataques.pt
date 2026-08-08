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


# ------------------------------------------- integridade da série do CERT.PT

def teste_cada_ano_declara_a_base_de_contagem():
    """Antes e depois de 2020 o CERT.PT não conta a mesma coisa.

    A partir de 2020 as vulnerabilidades passaram a ser contabilizadas como
    incidentes, e o próprio CNCS chama-lhe "quebra de série". Um ano sem esta
    declaração é um ano que alguém vai comparar com o vizinho errado.
    """
    anos = ler_yaml(DIR_REFERENCIA / "cncs.yaml")["anos"]
    quebra = ler_yaml(DIR_REFERENCIA / "cncs.yaml")["quebra_de_serie"]["ano"]
    for ano, dados in anos.items():
        assert "base_de_contagem" in dados, f"{ano} não diz em que base foi contado"
        esperada = "sem_vulnerabilidades" if int(ano) < quebra else "com_vulnerabilidades"
        assert dados["base_de_contagem"] == esperada, (
            f"{ano} declara base {dados['base_de_contagem']}, mas a quebra de série é "
            f"em {quebra} — devia ser {esperada}"
        )


def teste_o_ano_da_quebra_publica_os_dois_valores():
    """O ano da quebra é o único que se compara para trás e para a frente.

    Só o consegue fazer se guardar as duas contagens: a nova, que segue para os anos
    seguintes, e a antiga, que é a que se compara com o ano anterior.
    """
    cncs = ler_yaml(DIR_REFERENCIA / "cncs.yaml")
    ano = cncs["anos"][cncs["quebra_de_serie"]["ano"]]
    assert ano.get("quebra_de_serie") is True
    assert ano.get("incidentes_sem_vulnerabilidades"), (
        "o ano da quebra tem de publicar também a contagem na base antiga"
    )
    assert ano["incidentes_sem_vulnerabilidades"] < ano["incidentes"], (
        "a contagem sem vulnerabilidades tem de ser menor do que a que as inclui"
    )


def teste_um_setor_nosso_vem_sempre_da_mesma_categoria_do_cert_pt():
    """A correspondência entre taxonomias tem de ser estável ao longo dos anos.

    Este teste nasce de um erro real. O setor `tecnologia` saía de "Infraestruturas
    Digitais" em 2022 e de "Prestadores de Serviços de Internet" em 2023 — duas
    categorias diferentes do CERT.PT com o mesmo destino aqui. O site mostrava a
    evolução de 7% para 26% como se fosse o mesmo setor a crescer, quando era a
    régua a mudar a meio da medição.

    Um valor por ano é um facto; uma série exige que a régua não mude.
    """
    anos = ler_yaml(DIR_REFERENCIA / "cncs.yaml")["anos"]
    origem: dict[str, tuple[set[str], str]] = {}
    problemas = []
    for ano, dados in sorted(anos.items()):
        for setor, info in (dados.get("setores", {}).get("categorias_cert_pt") or {}).items():
            # O CERT.PT renomeia categorias entre edições sem mudar o que elas
            # medem. Um `categoria_anterior` declarado é isso, e não uma troca de
            # categoria: aceita-se, mas tem de estar escrito.
            nomes = {info["categoria"]} | {info["categoria_anterior"]} if info.get(
                "categoria_anterior"
            ) else {info["categoria"]}
            if setor in origem and not (nomes & origem[setor][0]):
                anterior, ano_anterior = origem[setor]
                problemas.append(
                    f"{setor}: {ano_anterior} usa '{sorted(anterior)[0]}' e {ano} usa "
                    f"'{info['categoria']}'"
                )
            origem.setdefault(setor, (nomes, str(ano)))
    assert not problemas, (
        "Setores nossos alimentados por categorias diferentes do CERT.PT conforme o "
        "ano — a comparação entre anos deixa de medir a mesma coisa:\n  "
        + "\n  ".join(problemas)
    )


def teste_percentagens_declaradas_batem_com_os_numeros_absolutos():
    """Onde há contagem absoluta, a percentagem tem de sair dela.

    Guarda contra o erro de copiar à mão: um número de uma linha e a percentagem da
    linha de baixo.
    """
    cncs = ler_yaml(DIR_REFERENCIA / "cncs.yaml")
    problemas = []
    for ano, dados in cncs["anos"].items():
        setores = dados.get("setores") or {}
        for setor, info in (setores.get("categorias_cert_pt") or {}).items():
            declarada = setores["valores"][setor]
            assert declarada == info["percentagem"], (
                f"{ano}/{setor}: valores diz {declarada}%, categorias diz "
                f"{info['percentagem']}%"
            )
    assert not problemas, "\n  ".join(problemas)


def teste_as_percentagens_de_cada_ano_saem_todas_da_mesma_base():
    """Dentro de um ano, número e percentagem têm de ser coerentes entre si.

    Não se pode testar contra o total do ano, porque a base do CERT.PT não é essa e
    nem sequer é a mesma em todos os anos: em 2022 as percentagens saem da soma das
    atribuições setoriais (~2850, superior ao total porque um incidente pode contar
    em vários setores) e em 2023 saem do total do ano. É por isso que as percentagens
    dos dois anos não se comparam, e que o site mostra os absolutos.

    O que se pode exigir, e apanha a gralha de copiar um número emparelhado com a
    percentagem da linha ao lado, é que todos os setores de um ano impliquem a MESMA
    base. Se um deles implicar outra, alguém trocou um valor.
    """
    cncs = ler_yaml(DIR_REFERENCIA / "cncs.yaml")
    problemas = []
    for ano, dados in cncs["anos"].items():
        setores = dados.get("setores") or {}
        cats = setores.get("categorias_cert_pt") or {}
        if not cats:
            continue
        assert setores.get("base_da_percentagem"), (
            f"{ano} publica percentagens sem dizer sobre que base foram calculadas"
        )
        # Uma percentagem publicada como inteiro p corresponde a um valor real em
        # [p-0,5; p+0,5], logo a base implícita por um setor é um intervalo e não um
        # ponto. Se existir uma base compatível com todos os setores do ano, os
        # números batem certo; se a interseção dos intervalos for vazia, algum
        # número está emparelhado com a percentagem errada.
        limites = []
        for setor, info in cats.items():
            n, p = info["numero"], info["percentagem"]
            limites.append((n / (p + 0.5) * 100, n / (p - 0.5) * 100, setor))
        minimo = max(l for l, _, _ in limites)
        maximo = min(a for _, a, _ in limites)
        if minimo > maximo:
            culpados = [
                f"{s} ({cats[s]['numero']} a {cats[s]['percentagem']}% → base "
                f"{l:.0f}–{a:.0f})"
                for l, a, s in sorted(limites)
            ]
            problemas.append(
                f"{ano}: não há base que explique todos os setores — " + "; ".join(culpados)
            )
    assert not problemas, "\n  ".join(problemas)
