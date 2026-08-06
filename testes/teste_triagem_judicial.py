"""A triagem tem de ver os casos que chegam pela justiça, sem engolir o resto do crime.

O ataque de 2024 às plataformas clínicas do Estado — certidões de óbito falsas no
SICO, mais de trezentas e cinquenta receitas falsas de medicamentos controlados,
três detidos em prisão preventiva e acusação do Ministério Público — nunca foi
detetado. Não por descuido: o léxico conhecia "ataque informático" e "ransomware", e
não conhecia uma única das infrações da Lei do Cibercrime.

O pipeline via ataques noticiados como notícia de tecnologia e era cego a ataques
noticiados como notícia de crime — que é justamente a via que traz arguidos, acusação
ou condenação, o degrau mais alto desta escala de confiança.

A correção tem duas metades, e a segunda é tão importante como a primeira: o feed da
Polícia Judiciária traz TODO o crime investigado. Se o vocabulário processual valesse
por si, a fila enchia-se de tráfico de estupefacientes e a curadoria morria — que é o
modo de falha que este projeto identificou como o mais provável.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from ingestao.comum import resolver_entidade  # noqa: E402
from ingestao.fontes import Item  # noqa: E402
from ingestao.triagem import triar  # noqa: E402


def noticia(titulo: str, texto: str = "") -> Item:
    return Item(
        url="https://exemplo.pt/a",
        url_canonica="https://exemplo.pt/a",
        titulo=titulo,
        publicador="exemplo",
        data_publicacao="2025-07-31",
        texto=texto,
        fonte="rss_media",
        obtido_em="2025-07-31T00:00:00+00:00",
        tipo_fonte="noticia",
        extra={},
    )


def teste_o_caso_que_motivou_isto_passa():
    resultado = triar(
        noticia(
            "Hackers atacaram o Ministério da Saúde e até passaram certidões de óbito",
            "Três detidos em prisão preventiva. O Ministério Público acusa de burla "
            "qualificada e falsidade informática. Usaram credenciais roubadas de médicos "
            "no SICO.",
        )
    )
    assert resultado.passa, f"rejeitado: {resultado.razao}"


@pytest.mark.parametrize(
    "titulo",
    [
        # Títulos reais do feed da Polícia Judiciária, verificados a 2026-08-06.
        "Operação “DUAS CARAS” – Suspeitos de rede criminosa de tráfico de estupefacientes",
        "Detido suspeito de incêndio em Gondomar",
        "Santarém: PJ detém suspeito de crime de extorsão com recurso a arma de fogo",
        "Dois estrangeiros detidos por tráfico de pessoas e auxílio à imigração ilegal",
        "Detenção por dupla tentativa de homicídio em Olhão",
    ],
)
def teste_o_crime_comum_da_pj_nao_entra(titulo):
    """Prova que o vocabulário processual sozinho não abre a porta."""
    resultado = triar(noticia(titulo, "A Polícia Judiciária deteve o suspeito após buscas."))
    assert not resultado.passa, f"entrou indevidamente: {resultado.razao}"


def teste_uma_infracao_da_lei_do_cibercrime_e_marcador_forte():
    resultado = triar(
        noticia(
            "PJ deteve suspeitos de falsidade informática e acesso ilegítimo a sistemas do Estado",
            "Três arguidos. A investigação apura acessos à Segurança Social Direta.",
        )
    )
    assert resultado.passa and resultado.pontuacao >= 6, resultado.razao


@pytest.mark.parametrize(
    "plataforma,esperado",
    [
        ("SICO", "sns"),
        ("PEM", "sns"),
        ("PRVR", "sns"),
        ("Segurança Social Direta", "seguranca-social"),
        ("e-fatura", "autoridade-tributaria"),
        ("Autenticação.Gov", "ama"),
    ],
)
def teste_as_plataformas_do_estado_resolvem_para_quem_as_opera(plataforma, esperado):
    """A cobertura fala do nome da plataforma e quase nunca do da entidade."""
    assert resolver_entidade(plataforma) == esperado
