"""Pré-filtro determinístico, sem modelo de linguagem.

Corta o corpus antes de gastar tokens. É o mesmo princípio do PORTUGAL_KEYWORDS do
iocRadar, mas com um objetivo adicional: proteger a curadoria. Se a triagem for frouxa,
a fila enche, o curador desiste e o projeto morre de excesso de trabalho, não de falta
de dados.

Nada aqui decide se algo é um incidente. Só decide o que vale a pena olhar.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ingestao.comum import DIR_REFERENCIA, ler_yaml, normalizar  # noqa: E402
from ingestao.fontes import Item  # noqa: E402

LEXICO = DIR_REFERENCIA / "triagem.yaml"

# Um item precisa de somar isto para passar. Calibrado para deixar entrar o que tem
# marcador forte ou combinação clara, e cortar o resto.
LIMIAR = 3


@dataclass
class Resultado:
    passa: bool
    pontuacao: int
    razao: str


_lexico: dict | None = None


def lexico() -> dict:
    global _lexico
    if _lexico is None:
        bruto = ler_yaml(LEXICO)
        _lexico = {
            chave: [normalizar(t) for t in termos]
            for chave, termos in bruto.items()
        }
    return _lexico


def _contem(texto: str, termos: list[str]) -> list[str]:
    return [t for t in termos if t in texto]


def triar(item: Item) -> Resultado:
    lex = lexico()
    # O título pesa mais do que o corpo: é onde a informação está concentrada e onde
    # o ruído editorial é menor.
    titulo = normalizar(item.titulo)
    corpo = normalizar(item.texto)
    tudo = f"{titulo} {corpo}"

    # As fontes de sites de extorsão saltam a triagem de RELEVÂNCIA: já são, por
    # construção, uma alegação de ataque. O que lhes falta é confirmação.
    #
    # O que não saltam é a verificação de PAÍS. Durante algum tempo saltavam, com o
    # argumento de que o tracker já filtrava por Portugal — e por aí entraram uma
    # construtora do Ontário chamada Aveiro Constructors, uma aplicação turística da
    # Nouvelle-Aquitaine e uma empresa de `sacor.fr`. A etiqueta de país do tracker
    # é um palpite dele, não um facto nosso.
    if item.tipo_fonte == "leak_site":
        indicio = (item.extra or {}).get("indicio_pais")
        if indicio == "estrangeiro":
            motivo = (item.extra or {}).get("indicio_pais_motivo", "indício de país estrangeiro")
            return Resultado(False, 0, f"listada como PT pelo tracker, mas {motivo}")
        return Resultado(True, 99, "fonte de site de extorsão, entra sempre")

    fortes = _contem(tudo, lex["fortes"])
    ataque = _contem(tudo, lex["ataque"])
    pt_forte = _contem(tudo, lex["portugal_forte"])
    # Os nomes de concelho contam como marcador fraco, a par das outras pistas
    # territoriais. Ver o cabeçalho da secção `concelhos` em triagem.yaml.
    pt_fraco = _contem(tudo, lex["portugal"] + lex.get("concelhos", []))
    estrangeiro = _contem(tudo, lex["estrangeiro"])
    ruido = _contem(tudo, lex["ruido"])
    # Contexto processual: arguidos, buscas, acusação. Ver a nota em triagem.yaml —
    # só conta acompanhado de termo informático, e a regra está mais abaixo.
    judicial = _contem(tudo, lex.get("processo_judicial", []))

    if not ataque:
        return Resultado(False, 0, "sem qualquer termo de ataque")

    # Um marcador estrangeiro só é anulado por um marcador português inequívoco.
    # Sem esta regra, "hospital" bastava para dar um hospital de Munique por
    # português, porque marcadores como "hospital" descrevem realidades universais.
    if estrangeiro and not pt_forte:
        return Resultado(
            False, 0, f"caso aparentemente estrangeiro: {estrangeiro[0]}"
        )

    if not pt_forte and not pt_fraco:
        return Resultado(False, 0, "sem marcador português")

    pontuacao = 0
    pontuacao += 4 if fortes else 0
    # O vocabulário do processo penal soma, mas nunca abre a porta sozinho: a
    # condição é haver já um termo de ataque, que a linha acima garante existir.
    # Sem isto, o feed da Polícia Judiciária — que é quase todo tráfico, incêndios e
    # homicídios — entrava inteiro na fila.
    pontuacao += 2 if judicial else 0
    pontuacao += 2 if _contem(titulo, lex["ataque"]) else 1
    pontuacao += 2 if pt_forte else 0
    pontuacao += 1 if pt_fraco else 0
    pontuacao -= 3 if ruido else 0

    razoes = []
    if fortes:
        razoes.append(f"marcador forte: {fortes[0]}")
    if ataque:
        razoes.append(f"ataque: {ataque[0]}")
    if pt_forte:
        razoes.append(f"portugal: {pt_forte[0]}")
    elif pt_fraco:
        razoes.append(f"portugal (fraco): {pt_fraco[0]}")
    if judicial:
        razoes.append(f"processo: {judicial[0]}")
    if ruido:
        razoes.append(f"ruído: {ruido[0]}")

    return Resultado(pontuacao >= LIMIAR, pontuacao, "; ".join(razoes))


def triar_muitos(itens: list[Item]) -> tuple[list[Item], list[tuple[Item, Resultado]]]:
    """Devolve (aprovados, rejeitados_com_razao)."""
    aprovados: list[Item] = []
    rejeitados: list[tuple[Item, Resultado]] = []
    for item in itens:
        resultado = triar(item)
        if resultado.passa:
            aprovados.append(item)
        else:
            rejeitados.append((item, resultado))
    return aprovados, rejeitados
