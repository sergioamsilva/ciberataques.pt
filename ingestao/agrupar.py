"""Deduplicação e sugestão de agrupamento.

Três camadas, todas com o mesmo princípio: SUGEREM, nunca decidem.

  1. Ao nível do item: chave de URL canónica e título. Um item já visto não volta ao
     modelo, o que é sobretudo uma poupança de custo.
  2. Ao nível do texto: SimHash. O teletipo da Lusa aparece em seis sítios com títulos
     diferentes, e sem isto seriam seis candidatos para o mesmo facto.
  3. Ao nível do incidente: propõe ligar um candidato a um incidente já publicado.

A lição está escrita no snsRadar, em ingest/common.py: a normalização agressiva "é
demasiado permissiva para decidir sozinha; nunca usar para juntar automaticamente".
Aplica-se aqui na íntegra. Uma fusão errada de dois incidentes distintos é um erro
difícil de detetar depois, porque desaparece do registo sem deixar rasto.
"""

from __future__ import annotations

import hashlib
import re
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ingestao.comum import DIR_INCIDENTES, ler_json, normalizar  # noqa: E402
from ingestao.fontes import Item  # noqa: E402

# Distância de Hamming abaixo da qual duas peças se consideram a mesma.
LIMIAR_SIMHASH = 3
# Janela para propor que um candidato pertence a um incidente já registado.
JANELA_DIAS = 45


def simhash(texto: str, bits: int = 64) -> int:
    """SimHash sobre 5-gramas de palavras.

    Deteta a mesma peça reescrita, que é o caso comum quando vários órgãos publicam
    o mesmo teletipo com título próprio.
    """
    palavras = normalizar(texto).split()
    if len(palavras) < 5:
        palavras = palavras or [""]
        gramas = [" ".join(palavras)]
    else:
        gramas = [" ".join(palavras[i : i + 5]) for i in range(len(palavras) - 4)]

    vetor = [0] * bits
    for grama in gramas:
        digest = int.from_bytes(hashlib.blake2b(grama.encode(), digest_size=8).digest(), "big")
        for i in range(bits):
            vetor[i] += 1 if (digest >> i) & 1 else -1
    return sum(1 << i for i in range(bits) if vetor[i] > 0)


def distancia(a: int, b: int) -> int:
    return bin(a ^ b).count("1")


def deduplicar(itens: list[Item], vistos: set[str] | None = None) -> list[Item]:
    """Remove repetidos por chave exata e por semelhança de texto."""
    vistos = vistos or set()
    saida: list[Item] = []
    impressoes: list[int] = []

    for item in itens:
        if item.chave in vistos:
            continue
        # Quando há corpo suficiente, a impressão é feita SÓ sobre o corpo. O mesmo
        # despacho da Lusa sai com título próprio em cada órgão, e incluir o título
        # fazia com que duas cópias do mesmo texto parecessem peças diferentes.
        corpo = item.texto if len(item.texto.split()) >= 25 else f"{item.titulo} {item.texto}"
        impressao = simhash(corpo)
        if any(distancia(impressao, outra) <= LIMIAR_SIMHASH for outra in impressoes):
            continue
        vistos.add(item.chave)
        impressoes.append(impressao)
        saida.append(item)

    return saida


def _dias(a: str, b: str) -> int:
    return abs((date.fromisoformat(a) - date.fromisoformat(b)).days)


def sugerir_incidente(
    entidade_id: str | None,
    data_candidata: str | None,
    tipos: list[str] | None,
) -> dict | None:
    """Propõe o incidente publicado a que um candidato provavelmente pertence.

    Devolve uma sugestão com pontuação e razão, para um humano decidir. Nunca funde.
    """
    if not entidade_id or not data_candidata:
        return None

    melhor = None
    for caminho in sorted(DIR_INCIDENTES.glob("*.json")):
        incidente = ler_json(caminho)
        if entidade_id not in incidente["entidades_afetadas"]:
            continue
        try:
            distancia_dias = _dias(data_candidata, incidente["data"]["inicio"])
        except ValueError:
            continue
        if distancia_dias > JANELA_DIAS:
            continue

        comuns = set(tipos or []) & set(incidente["tipos_ataque"])
        pontuacao = 0.5
        pontuacao += 0.3 * (1 - distancia_dias / JANELA_DIAS)
        pontuacao += 0.2 if comuns else 0.0

        razao = (
            f"mesma entidade, {distancia_dias} dias de diferença"
            + (f", tipos em comum: {', '.join(sorted(comuns))}" if comuns else "")
        )
        if melhor is None or pontuacao > melhor["similaridade"]:
            melhor = {
                "incidente_id": incidente["id"],
                "titulo": incidente["titulo"],
                "similaridade": round(pontuacao, 2),
                "razao": razao,
            }

    return melhor
