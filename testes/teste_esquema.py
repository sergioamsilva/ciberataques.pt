"""Valida o registo canónico contra o JSON Schema, e o JSON Schema contra a taxonomia.

O segundo é o menos óbvio e o mais importante: o esquema e a taxonomia declaram os
mesmos vocabulários em dois sítios (o esquema para que terceiros possam validar o
nosso JSON sem ler YAML, a taxonomia para que o site tenha os nomes legíveis). Se
divergirem em silêncio, passamos a aceitar valores que o site não sabe mostrar.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ingestao.comum import (  # noqa: E402
    DIR_INCIDENTES,
    ESQUEMA_INCIDENTE,
    carregar_entidades,
    carregar_taxonomia,
    ler_json,
)


@pytest.fixture(scope="module")
def esquema() -> dict:
    return ler_json(ESQUEMA_INCIDENTE)


@pytest.fixture(scope="module")
def taxonomia() -> dict:
    return carregar_taxonomia()


def incidentes() -> list[Path]:
    return sorted(DIR_INCIDENTES.glob("*.json"))


def teste_esquema_e_valido(esquema):
    Draft202012Validator.check_schema(esquema)


@pytest.mark.parametrize(
    "caminho_esquema,chave_taxonomia",
    [
        ("properties.setor.enum", "setores"),
        ("properties.tipos_ataque.items.enum", "tipos_ataque"),
        ("properties.estado_confirmacao.enum", "estados_confirmacao"),
        ("properties.cronologia.items.properties.tipo.enum", "tipos_evento"),
        ("properties.data.properties.precisao.enum", "precisoes_data"),
        ("$defs.fonte.properties.tipo.enum", "tipos_fonte"),
        (
            "properties.dados_pessoais.properties.categorias.items.enum",
            "categorias_dados",
        ),
    ],
)
def teste_enums_sincronizados_com_taxonomia(esquema, taxonomia, caminho_esquema, chave_taxonomia):
    no = esquema
    for parte in caminho_esquema.split("."):
        no = no[parte]
    assert set(no) == set(taxonomia[chave_taxonomia]), (
        f"O enum {caminho_esquema} do esquema divergiu de {chave_taxonomia} na taxonomia. "
        f"Só no esquema: {set(no) - set(taxonomia[chave_taxonomia])}. "
        f"Só na taxonomia: {set(taxonomia[chave_taxonomia]) - set(no)}."
    )


@pytest.mark.parametrize("caminho", incidentes(), ids=lambda p: p.stem)
def teste_incidente_valida(caminho, esquema):
    incidente = ler_json(caminho)
    erros = sorted(
        Draft202012Validator(esquema).iter_errors(incidente),
        key=lambda e: list(e.path),
    )
    assert not erros, "\n".join(
        f"  {'.'.join(str(p) for p in e.path) or '(raiz)'}: {e.message}" for e in erros
    )


@pytest.mark.parametrize("caminho", incidentes(), ids=lambda p: p.stem)
def teste_id_corresponde_ao_ficheiro(caminho):
    """O nome do ficheiro é o identificador citável. Não pode divergir do campo id."""
    assert ler_json(caminho)["id"] == caminho.stem


@pytest.mark.parametrize("caminho", incidentes(), ids=lambda p: p.stem)
def teste_entidades_existem_no_crosswalk(caminho):
    """Uma entidade desconhecida é uma sugestão para entidades.yaml, não um facto."""
    conhecidas = {e["id"] for e in carregar_entidades()}
    incidente = ler_json(caminho)
    referidas = set(incidente["entidades_afetadas"])
    referidas |= set(incidente.get("entidades_afetadas_em_cascata", []))
    assert referidas <= conhecidas, (
        f"Entidades ausentes de referencia/entidades.yaml: {sorted(referidas - conhecidas)}"
    )
