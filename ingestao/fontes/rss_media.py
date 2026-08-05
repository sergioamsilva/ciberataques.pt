"""Recolha dos feeds da comunicação social portuguesa.

Três armadilhas, todas encontradas na verificação de 2026-08-05 e documentadas em
referencia/NOTAS.md:

  1. Três feeds declaram ISO-8859-1. Lidos como UTF-8, todos os acentos partem-se.
  2. Os feeds retêm entre um e dez itens. A recolha tem de ser diária ou perde-se
     história, e isso é uma exigência operacional, não uma preferência.
  3. Muitos trazem apenas uma descrição truncada. O texto completo exige um segundo
     pedido, que só fazemos se o robots.txt permitir.
"""

from __future__ import annotations

import re
from datetime import datetime, timezone

import feedparser

from ingestao.comum import FONTES, ler_yaml
from ingestao.fontes import Item
from ingestao.rede import DestinoRecusado, ErroDeRede, canonicalizar, obter

_ETIQUETAS = re.compile(r"<[^>]+>")
_ESPACOS = re.compile(r"\s+")


def _limpar(html: str) -> str:
    return _ESPACOS.sub(" ", _ETIQUETAS.sub(" ", html or "")).strip()


def _data_iso(entrada) -> str | None:
    for campo in ("published_parsed", "updated_parsed"):
        valor = entrada.get(campo)
        if valor:
            return datetime(*valor[:6], tzinfo=timezone.utc).date().isoformat()
    return None


def _feeds_ativos() -> list[dict]:
    catalogo = ler_yaml(FONTES)
    return [
        f
        for f in catalogo["fontes"]
        if f.get("metodo") == "rss" and f.get("ativa") and f.get("feeds")
    ]


def recolher() -> list[Item]:
    agora = datetime.now(timezone.utc).isoformat(timespec="seconds")
    itens: list[Item] = []
    vistos: set[str] = set()

    for fonte in _feeds_ativos():
        for url_feed in fonte["feeds"]:
            try:
                resposta = obter(url_feed, aceitar="application/rss+xml, application/xml")
            except (ErroDeRede, DestinoRecusado) as erro:
                # Uma fonte em baixo não pode parar a recolha das outras. O silêncio
                # é que seria perigoso: teste_fontes.py acusa fontes sem resultados.
                print(f"  AVISO  {fonte['id']}: {erro}")
                continue

            if resposta.nao_modificado:
                continue

            analisado = feedparser.parse(resposta.texto)
            for entrada in analisado.entries:
                url = entrada.get("link")
                titulo = (entrada.get("title") or "").strip()
                if not url or not titulo:
                    continue

                canonica = canonicalizar(url)
                if canonica in vistos:
                    continue
                vistos.add(canonica)

                resumo = _limpar(
                    entrada.get("summary")
                    or (entrada.get("content") or [{}])[0].get("value", "")
                )

                itens.append(
                    Item(
                        url=url,
                        url_canonica=canonica,
                        titulo=titulo,
                        publicador=fonte["nome"],
                        data_publicacao=_data_iso(entrada),
                        texto=resumo,
                        fonte=fonte["id"],
                        obtido_em=agora,
                        tipo_fonte="noticia",
                        extra={"feed": url_feed},
                    )
                )

    return itens
