"""Verifica os explicadores por tipo de ataque.

O teste que mais importa é o dos identificadores digitais: uma referência académica
inventada é o erro mais destrutivo que este projeto pode cometer. Um incidente mal
datado corrige-se; uma bibliografia fabricada destrói a credibilidade de tudo o resto,
e é precisamente o tipo de erro que um texto gerado com apoio de modelos de linguagem
tende a produzir.

Por isso cada DOI é resolvido contra o CrossRef, e o título registado é comparado com
o que o CrossRef devolve. O teste vai à rede e está marcado como tal: corre com
`pytest -m rede`, e no guião de publicação.
"""

from __future__ import annotations

import json
import re
import sys
import urllib.request
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from ingestao.comum import carregar_taxonomia, normalizar  # noqa: E402

DIR_EXPLICADORES = RAIZ / "site" / "src" / "content" / "tipos"
AGENTE = "ciberataques.pt/1.0 (mailto:correcoes@ciberataques.pt)"


def _frontmatter(caminho: Path) -> dict:
    import yaml

    texto = caminho.read_text(encoding="utf-8")
    partes = texto.split("---", 2)
    assert len(partes) >= 3, f"{caminho.name}: sem frontmatter"
    return yaml.safe_load(partes[1])


def explicadores() -> list[Path]:
    return sorted(DIR_EXPLICADORES.glob("*.md"))


@pytest.mark.parametrize("caminho", explicadores(), ids=lambda p: p.stem)
def teste_tipo_existe_na_taxonomia(caminho):
    """Um explicador para um tipo que o registo não usa seria conteúdo órfão."""
    dados = _frontmatter(caminho)
    assert dados["tipo"] in carregar_taxonomia()["tipos_ataque"], (
        f"'{dados['tipo']}' não existe em referencia/taxonomia.yaml"
    )
    assert dados["tipo"] == caminho.stem, "o nome do ficheiro tem de ser o tipo"


@pytest.mark.parametrize("caminho", explicadores(), ids=lambda p: p.stem)
def teste_tem_referencias(caminho):
    dados = _frontmatter(caminho)
    assert dados.get("referencias"), "um explicador sem referências não é publicável"
    for ref in dados["referencias"]:
        assert ref.get("doi") or ref.get("url"), (
            f"a referência '{ref['titulo']}' não tem DOI nem URL: não é verificável"
        )


@pytest.mark.parametrize("caminho", explicadores(), ids=lambda p: p.stem)
def teste_ligacoes_internas_apontam_para_incidentes_existentes(caminho):
    """As ligações para fichas dentro do texto não podem apontar para o vazio."""
    from ingestao.comum import DIR_INCIDENTES

    existentes = {p.stem for p in DIR_INCIDENTES.glob("*.json")}
    texto = caminho.read_text(encoding="utf-8")
    for referido in re.findall(r"\(/incidentes/([a-z0-9-]+)/\)", texto):
        assert referido in existentes, (
            f"{caminho.name} liga para o incidente inexistente '{referido}'"
        )


@pytest.mark.rede
@pytest.mark.parametrize("caminho", explicadores(), ids=lambda p: p.stem)
def teste_dois_resolvem_e_correspondem(caminho):
    """Cada DOI resolve no CrossRef e o título bate certo com o que registámos.

    Não basta o DOI existir: um DOI válido apontando para outro artigo seria uma
    citação errada, que é apenas uma forma mais subtil de inventar bibliografia.
    """
    for ref in _frontmatter(caminho)["referencias"]:
        doi = ref.get("doi")
        if not doi:
            continue

        pedido = urllib.request.Request(
            f"https://api.crossref.org/works/{doi}", headers={"User-Agent": AGENTE}
        )
        try:
            with urllib.request.urlopen(pedido, timeout=30) as resposta:
                dados = json.load(resposta)["message"]
        except Exception as erro:  # noqa: BLE001
            pytest.fail(f"o DOI {doi} não resolveu no CrossRef: {erro}")

        registado = normalizar(ref["titulo"])
        obtido = normalizar(dados["title"][0])
        assert registado == obtido, (
            f"o DOI {doi} existe mas aponta para outro artigo.\n"
            f"  registámos: {ref['titulo']}\n"
            f"  CrossRef  : {dados['title'][0]}"
        )

        ano_crossref = dados.get("issued", {}).get("date-parts", [[None]])[0][0]
        if ano_crossref:
            assert abs(int(ref["ano"]) - int(ano_crossref)) <= 1, (
                f"ano divergente para {doi}: registámos {ref['ano']}, "
                f"CrossRef diz {ano_crossref}"
            )
