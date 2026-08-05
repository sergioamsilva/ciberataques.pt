#!/usr/bin/env python3
"""Localiza cópias arquivadas das fontes citadas e preenche `url_arquivo`.

Uma ligação numa ficha é a prova do que ali se afirma. Quando morre, a afirmação
fica sem sustentação e o arquivo deixa de valer o que dizia valer. Preencher
`url_arquivo` é, por isso, trabalho de integridade e não uma conveniência.

Usamos o **Internet Archive** para preencher `url_arquivo` automaticamente.

O **Arquivo.pt**, da FCCN, seria a escolha natural — preserva o domínio .pt desde
1996 e tem quase tudo o que citamos, muitas vezes capturado no próprio dia do
incidente. Mas o seu robots.txt termina com `Disallow: /wayback` para todos os
agentes, com exceções apenas para uma lista de domínios nomeados. Consultá-lo
programaticamente seria desrespeitar uma instrução explícita, e a política
editorial deste projeto não o permite.

A distinção que resolve o problema: um robots.txt regula **raspagem**, não
**hiperligações**. Por isso o site gera, para cada fonte, uma ligação de pesquisa
no Arquivo.pt que o leitor segue no seu navegador — ver `site/src/components/
Cobertura.astro`. O leitor fica com o melhor arquivo para conteúdo português, e nós
não raspamos nada.

Com `--submeter`, o que não estiver arquivado é submetido ao Save Page Now do
Internet Archive. É o passo que fecha o ciclo: procurar cópias resolve o passado,
mas uma notícia de hoje que ninguém arquive é uma prova que se vai perder. O ónus
de alojar a cópia fica do lado do arquivo público, e não nosso, o que também
importa do ponto de vista de direitos de autor.

    python ingestao/arquivo.py             # procura cópias existentes
    python ingestao/arquivo.py --submeter  # + pede o arquivamento das que faltam
    python ingestao/arquivo.py --refazer   # revisita tudo
    python ingestao/arquivo.py --resumo    # só mostra a cobertura atual
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from urllib.parse import quote

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from ingestao.comum import DIR_INCIDENTES, escrever_json, ler_json  # noqa: E402
from ingestao.rede import ErroDeRede, obter  # noqa: E402

CDX_ARQUIVO_PT = "https://arquivo.pt/wayback/cdx"
DISPONIVEL_IA = "https://archive.org/wayback/available"


def _timestamp_da_data(data: str) -> str:
    """AAAA-MM-DD para o carimbo AAAAMMDD000000 que as APIs esperam."""
    return data.replace("-", "") + "000000"


def ligacao_de_pesquisa_no_arquivo_pt(url: str) -> str:
    """Ligação para o leitor consultar as capturas de um URL no Arquivo.pt.

    NÃO faz qualquer pedido. É apenas a construção de uma hiperligação, que o
    leitor segue no seu navegador — e a distinção é toda: o robots.txt do
    Arquivo.pt proíbe raspagem de /wayback, e nós respeitamo-lo; o que ele não
    regula, nem pode, é para onde apontamos uma ligação.

    Fica assim disponível o melhor arquivo para conteúdo português, sem que o
    projeto lhe faça um único pedido automatizado.
    """
    return f"https://arquivo.pt/wayback/*/{url}"


def pedir_arquivamento(url: str) -> bool:
    """Pede ao Internet Archive que arquive uma página ainda não preservada.

    É o passo que fecha o ciclo: procurar cópias só resolve o passado, e mais de
    dois terços das nossas fontes não tinham nenhuma. Uma notícia de hoje que
    ninguém arquive é uma prova que vamos perder.

    O ónus de alojar a cópia fica do lado do Internet Archive, e não nosso — é uma
    decisão deliberada e com consequências legais: não republicamos texto de
    terceiros, apenas pedimos a um arquivo público que faça o que existe para fazer.

    O Save Page Now aplica limites por endereço e devolve 429 com frequência. Falhar
    aqui não é erro: é sinal para tentar mais tarde.
    """
    try:
        resposta = obter(
            f"https://web.archive.org/save/{url}",
            usar_cache=False,
            aceitar="text/html",
        )
    except ErroDeRede:
        return False
    return resposta.estado in (200, 201)


def procurar_no_internet_archive(url: str, perto_de: str) -> str | None:
    pedido = f"{DISPONIVEL_IA}?url={quote(url, safe='')}&timestamp={_timestamp_da_data(perto_de)}"
    try:
        resposta = obter(pedido, usar_cache=False, aceitar="application/json")
    except ErroDeRede:
        return None
    try:
        dados = json.loads(resposta.texto)
    except json.JSONDecodeError:
        return None
    instantaneo = (dados.get("archived_snapshots") or {}).get("closest") or {}
    if instantaneo.get("available") and instantaneo.get("url"):
        return instantaneo["url"]
    return None


def preencher(refazer: bool = False, submeter: bool = False) -> dict:
    total = achados_ia = ja_tinha = sem_copia = 0
    pedidos_feitos = pedidos_recusados = 0

    for caminho in sorted(DIR_INCIDENTES.glob("*.json")):
        incidente = ler_json(caminho)
        mudou = False

        for fonte in incidente["fontes"]:
            total += 1
            if fonte.get("url_arquivo") and not refazer:
                ja_tinha += 1
                continue

            url = fonte["url"]
            # As páginas de trackers de sites de extorsão mudam ao sabor das
            # vítimas listadas e não vale a pena fixá-las no tempo.
            if fonte["tipo"] == "leak_site":
                sem_copia += 1
                continue

            arquivada = procurar_no_internet_archive(url, fonte["data"])

            # Não existe cópia: pedimos que seja criada. Uma notícia que ninguém
            # arquive é uma prova que vamos perder, e o custo de o pedir é um
            # pedido HTTP.
            if not arquivada and submeter:
                if pedir_arquivamento(url):
                    pedidos_feitos += 1
                    # O arquivamento não é instantâneo. Voltamos a procurar já,
                    # e o que não aparecer fica para a próxima passagem.
                    arquivada = procurar_no_internet_archive(url, fonte["data"])
                    if not arquivada:
                        print(f"  pedido           {incidente['id']}  {fonte['publicador']}")
                else:
                    pedidos_recusados += 1

            if arquivada:
                fonte["url_arquivo"] = arquivada
                mudou = True
                achados_ia += 1
                print(f"  arquivada        {incidente['id']}  {fonte['publicador']}")
            else:
                sem_copia += 1
                print(f"  \033[33msem cópia\033[0m        {incidente['id']}  {fonte['publicador']}")

        if mudou:
            escrever_json(caminho, incidente)

    return {
        "total": total,
        "internet_archive": achados_ia,
        "ja_tinha": ja_tinha,
        "sem_copia": sem_copia,
        "pedidos_feitos": pedidos_feitos,
        "pedidos_recusados": pedidos_recusados,
    }


def resumo() -> None:
    com = sem = 0
    for caminho in sorted(DIR_INCIDENTES.glob("*.json")):
        for fonte in ler_json(caminho)["fontes"]:
            if fonte.get("url_arquivo"):
                com += 1
            else:
                sem += 1
    total = com + sem
    pct = 100 * com / total if total else 0
    print(f"  {com} de {total} fontes com cópia arquivada ({pct:.0f}%)")


if __name__ == "__main__":
    if "--resumo" in sys.argv:
        resumo()
        sys.exit(0)

    r = preencher(
        refazer="--refazer" in sys.argv,
        submeter="--submeter" in sys.argv,
    )
    print(
        f"\n  {r['total']} fontes · "
        f"{r['internet_archive']} arquivadas agora · "
        f"{r['ja_tinha']} já tinham · "
        f"{r['sem_copia']} sem cópia"
    )
    if r["pedidos_feitos"] or r["pedidos_recusados"]:
        print(
            f"  {r['pedidos_feitos']} pedidos de arquivamento aceites · "
            f"{r['pedidos_recusados']} recusados (voltar a correr mais tarde)"
        )
    print(
        "  O Arquivo.pt não é consultado programaticamente, por o seu robots.txt o "
        "proibir.\n  Cada fonte tem, no site, uma ligação de pesquisa lá — que é "
        "hiperligação, não raspagem."
    )
