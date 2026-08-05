"""Invariantes que o JSON Schema não consegue exprimir.

A mais importante: todo o facto publicado cita uma fonte que existe. O esquema garante
que `fonte` é um inteiro >= 0; só um teste consegue garantir que aponta para dentro do
array fontes[] deste incidente. Sem isto, um índice errado publicaria um facto sem
proveniência e ninguém daria por ela.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ingestao.comum import (  # noqa: E402
    DIR_INCIDENTES,
    MAX_EXCERTO,
    carregar_taxonomia,
    ler_json,
)


def incidentes() -> list[Path]:
    return sorted(DIR_INCIDENTES.glob("*.json"))


def _referencias_a_fontes(incidente: dict):
    """Produz (caminho legível, índice) para cada citação de fonte no incidente."""
    for i, evento in enumerate(incidente.get("cronologia", [])):
        yield f"cronologia[{i}]", evento["fonte"]
    for i, consequencia in enumerate(incidente.get("consequencias_regulatorias", [])):
        yield f"consequencias_regulatorias[{i}]", consequencia["fonte"]
    for i, disputa in enumerate(incidente.get("disputas", [])):
        yield f"disputas[{i}].fonte_afirmacao", disputa["fonte_afirmacao"]
        if disputa.get("fonte_contestacao") is not None:
            yield f"disputas[{i}].fonte_contestacao", disputa["fonte_contestacao"]


@pytest.mark.parametrize("caminho", incidentes(), ids=lambda p: p.stem)
def teste_citacoes_apontam_para_fontes_existentes(caminho):
    incidente = ler_json(caminho)
    total = len(incidente["fontes"])
    for local, indice in _referencias_a_fontes(incidente):
        assert 0 <= indice < total, (
            f"{local} cita a fonte {indice}, mas o incidente só tem {total} fontes. "
            "Nenhum facto pode ser publicado sem proveniência válida."
        )


@pytest.mark.parametrize("caminho", incidentes(), ids=lambda p: p.stem)
def teste_estado_confirmacao_sustentado_pelas_fontes(caminho):
    """O estado declarado tem de ser sustentado pelos tipos de fonte presentes.

    Impede que uma alegação de um site de extorsão apareça como confirmada, quer por
    erro de curadoria quer por um modelo de linguagem manipulado pelo texto que analisa.
    """
    incidente = ler_json(caminho)
    taxonomia = carregar_taxonomia()
    estado = incidente["estado_confirmacao"]
    regra = taxonomia["estados_confirmacao"][estado]

    exigidos = set(regra["exige_fonte_tipo"])

    def sustenta(fonte: dict) -> bool:
        if fonte["tipo"] in exigidos:
            return True
        # Uma notícia que reproduz a declaração vale como declaração, desde que o
        # curador o tenha afirmado explicitamente na fonte.
        if "comunicado" in exigidos and fonte.get("contem_declaracao_da_entidade"):
            return True
        if "regulador" in exigidos and fonte.get("contem_declaracao_de_autoridade"):
            return True
        return False

    sustentam = [f for f in incidente["fontes"] if sustenta(f)]
    assert sustentam, (
        f"O incidente declara '{estado}', que exige pelo menos uma fonte do tipo "
        f"{sorted(exigidos)} ou uma fonte marcada como contendo a declaração, mas "
        f"só tem fontes {sorted({f['tipo'] for f in incidente['fontes']})}."
    )

    minimo = regra.get("minimo_publicadores")
    if minimo:
        publicadores = {f["publicador"] for f in sustentam}
        assert len(publicadores) >= minimo, (
            f"O incidente declara '{estado}', que exige {minimo} publicadores "
            f"independentes, mas só tem {sorted(publicadores)}."
        )


@pytest.mark.parametrize("caminho", incidentes(), ids=lambda p: p.stem)
def teste_excertos_respeitam_o_limite(caminho):
    """Limite de 200 caracteres, imposto pela política editorial (secção 6)."""
    for i, fonte in enumerate(ler_json(caminho)["fontes"]):
        excerto = fonte.get("excerto")
        if excerto:
            assert len(excerto) <= MAX_EXCERTO, (
                f"fontes[{i}] tem um excerto de {len(excerto)} caracteres, acima do "
                f"limite de {MAX_EXCERTO} do direito de citação."
            )


@pytest.mark.parametrize("caminho", incidentes(), ids=lambda p: p.stem)
def teste_nao_ligamos_a_onion(caminho):
    """Nunca ligamos a sites de extorsão. Política editorial, secção 5."""
    for i, fonte in enumerate(ler_json(caminho)["fontes"]):
        assert ".onion" not in fonte["url"], (
            f"fontes[{i}] liga a um endereço .onion. Citar sempre a página do tracker "
            "público, nunca o site do grupo."
        )


@pytest.mark.parametrize("caminho", incidentes(), ids=lambda p: p.stem)
def teste_relacionados_existem(caminho):
    conhecidos = {p.stem for p in incidentes()}
    for outro in ler_json(caminho).get("relacionados", []):
        assert outro in conhecidos, f"O incidente relacionado '{outro}' não existe."


@pytest.mark.parametrize("caminho", incidentes(), ids=lambda p: p.stem)
def teste_datas_coerentes(caminho):
    """A divulgação não pode ser anterior à ocorrência."""
    data = ler_json(caminho)["data"]
    if data.get("divulgacao"):
        assert data["divulgacao"] >= data["inicio"], (
            "A data de divulgação é anterior à data do incidente."
        )
    if data.get("fim"):
        assert data["fim"] >= data["inicio"]


@pytest.mark.parametrize("caminho", incidentes(), ids=lambda p: p.stem)
def teste_numeros_do_atacante_nao_entram_no_impacto(caminho):
    """Um número que só uma fonte leak_site sustenta não pode viver em impacto.

    Guarda contra o erro mais fácil de cometer neste projeto: transcrever para a ficha
    técnica um volume de dados ou uma contagem de vítimas que existe apenas porque o
    atacante o disse. Esses números pertencem a disputas[], identificados como tal.
    """
    incidente = ler_json(caminho)
    tipos = {f["tipo"] for f in incidente["fontes"]}
    if tipos != {"leak_site"}:
        return
    impacto = incidente.get("impacto", {})
    for campo in ("pessoas_afetadas_declaradas", "custo_declarado_eur"):
        assert impacto.get(campo) is None, (
            f"impacto.{campo} está preenchido, mas a única fonte deste incidente é um "
            "site de extorsão. Mover o valor para disputas[]."
        )
    assert incidente.get("dados_pessoais", {}).get("titulares_declarados") is None, (
        "dados_pessoais.titulares_declarados está preenchido a partir de uma fonte que "
        "é apenas o atacante. Mover para disputas[]."
    )
