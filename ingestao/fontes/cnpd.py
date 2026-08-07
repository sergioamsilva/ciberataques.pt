"""Deliberações da Comissão Nacional de Proteção de Dados.

Lê o índice do histórico de decisões — **nunca os PDF**. A distinção não é preguiça,
é o que a fonte permite, e ficou apurado a 2026-08-07:

  Os PDF da CNPD são digitalizações sem camada de texto. A deliberação 984/2018 tem
  vinte páginas de imagens JPX a 150 ppp em 7,7 MB, e `pdftotext` extrai vinte bytes.
  Extrair o conteúdo exigiria reconhecimento ótico, que não é uma dependência que este
  projeto queira ter para o valor que daria.

O índice, esse, é bem estruturado e dá o suficiente para um curador decidir: número da
deliberação, entidade emissora, assunto em uma linha e ligação para o documento. É com
o assunto que a triagem trabalha.

Duas coisas que este módulo NÃO faz, e é importante que se saibam:

  1. **Não descobre a maioria dos ciberataques.** Das trinta e três deliberações
     publicadas entre 2018 e 2026, quase nenhuma resulta de um ataque — são
     videovigilância, avaliações de impacto, protocolos entre entidades e comunicações
     não solicitadas. A CNPD é uma autoridade de proteção de dados, não de
     cibersegurança, e a maior parte do que sanciona não tem atacante nenhum.

  2. **Não vê todas as decisões sancionatórias.** A coima ao Centro Hospitalar Barreiro
     Montijo foi revista para 380 mil euros em março de 2020, e essa decisão não consta
     da lista de deliberações publicadas. O que está publicado é um subconjunto.

O que justifica existir, apesar disso: quando uma violação de dados com origem em
ataque **é** sancionada, esta é a fonte primária — e uma deliberação vale mais do que
qualquer notícia sobre ela. Vale a pena olhar poucas vezes para o sítio certo.

Não há robots.txt em cnpd.pt (404 verificado), pelo que não há restrições declaradas.
Ainda assim a recolha é deliberadamente pouco frequente e identificada.
"""

from __future__ import annotations

import html
import re
from datetime import datetime, timezone

from ingestao.comum import FONTES, ler_yaml
from ingestao.fontes import Item
from ingestao.rede import DestinoRecusado, ErroDeRede, canonicalizar, obter

BASE = "https://www.cnpd.pt"
INDICE = BASE + "/decisoes/historico-de-decisoes/"

# Tipo 2 = DELIBERAÇÃO. Os outros são autorizações, pareceres, registos, diretrizes e
# regulamentos — matéria regulatória sem relação com incidentes.
TIPO_DELIBERACAO = "2"

# Cada resultado do índice. O HTML é gerado por Umbraco e estável nesta forma.
CARTAO = re.compile(
    r'<a href="(/umbraco/surface/cnpdDecision/download/\d+)"[^>]*>\s*'
    r'<div class="c-card-header-medium">(.*?)</div>\s*'
    r'<div class="c-card-header">(.*?)</div>\s*'
    r'(?:<div class="c-card-text">(.*?)</div>)?',
    re.S,
)


def _configuracao() -> dict | None:
    """A entrada da CNPD no catálogo, se estiver ativa.

    Procura pelo id e não pelo método: `metodo` descreve como se recolhe — aqui é
    `html`, porque é raspagem de HTML — e várias fontes partilham o mesmo valor. Foi
    por confundir as duas coisas que se chegou a ter duas entradas com o id `cnpd`
    no catálogo, uma delas desativada, e a desativada é que ganhava.
    """
    catalogo = ler_yaml(FONTES)
    for fonte in catalogo["fontes"]:
        if fonte["id"] == "cnpd":
            return fonte if fonte.get("ativa") else None
    return None


def _limpar(texto: str | None) -> str:
    return html.unescape(re.sub(r"<[^>]+>", " ", texto or "")).strip()


def _ano_da_deliberacao(titulo: str) -> str | None:
    """"Deliberação 984/2018" -> "2018"."""
    m = re.search(r"/(\d{4})\b", titulo)
    return m.group(1) if m else None


def recolher(anos: list[int] | None = None) -> list[Item]:
    fonte = _configuracao()
    if not fonte:
        return []

    # Por omissão, o ano corrente e o anterior. O histórico completo é trabalho de
    # arranque, feito uma vez à mão, e não coisa para repetir a cada recolha.
    if anos is None:
        agora = datetime.now(timezone.utc).year
        anos = [agora, agora - 1]

    itens: list[Item] = []
    obtido_em = datetime.now(timezone.utc).isoformat(timespec="seconds")

    for ano in anos:
        url = f"{INDICE}?year={ano}&type={TIPO_DELIBERACAO}&ent="
        try:
            resposta = obter(url)
        except (ErroDeRede, DestinoRecusado) as erro:
            print(f"  AVISO  cnpd {ano}: {erro}")
            continue
        if resposta.nao_modificado:
            continue

        for caminho, titulo, emissor, assunto in CARTAO.findall(resposta.texto):
            titulo = _limpar(titulo)
            assunto = _limpar(assunto)
            if not titulo:
                continue
            documento = BASE + caminho
            itens.append(
                Item(
                    url=documento,
                    url_canonica=canonicalizar(documento),
                    titulo=f"{titulo} — {assunto}" if assunto else titulo,
                    publicador="Comissão Nacional de Proteção de Dados",
                    data_publicacao=(
                        f"{_ano_da_deliberacao(titulo)}-01-01"
                        if _ano_da_deliberacao(titulo)
                        else None
                    ),
                    # O assunto é tudo o que há: o PDF é digitalizado e ilegível por
                    # meios automáticos. Quem cura decide a partir desta linha e do
                    # documento, que abre no browser.
                    texto=assunto,
                    fonte="cnpd",
                    obtido_em=obtido_em,
                    tipo_fonte="regulador",
                    extra={
                        "deliberacao": titulo,
                        "emissor": _limpar(emissor),
                        "ano": _ano_da_deliberacao(titulo),
                        "pdf_digitalizado": True,
                    },
                )
            )

    return itens
