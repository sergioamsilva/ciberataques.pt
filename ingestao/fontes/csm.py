"""Acórdãos dos tribunais superiores, pela base do Conselho Superior da Magistratura.

É a fonte de prova mais forte que este registo pode ter: uma decisão judicial vale
mais do que uma acusação, e muito mais do que um comunicado. O acórdão que confirmou a
condenação do funcionário do IGFEJ é disso exemplo.

O caminho até aqui teve três obstáculos, e vale a pena estarem escritos porque nenhum
era óbvio:

  1. **A cadeia de certificados está incompleta.** O servidor não envia o intermediário
     da Sectigo, e a verificação falha. Está resolvido em `ingestao/rede.py`, sem
     desligar a verificação — ver `_remendar_cadeia()`.

  2. **A pesquisa é dynatable, e só funciona por GET.** O mesmo pedido por POST devolve
     a base inteira, sem filtro nenhum e sem erro — o pior modo de falha possível, o
     que responde com sucesso e resultados errados.

  3. **O campo é `filter_descriptors`, e não o de pesquisa livre.** O `freesearch`
     devolve zero para termos que existem; são os descritores que indexam a matéria.

O que a fonte dá e o que não dá, medido a 2026-08-07 sobre 343 876 acórdãos:

  FALSIDADE INFORMÁTICA  59      BURLA INFORMÁTICA      108
  ACESSO ILEGÍTIMO       49      DANO INFORMÁTICO         3
  SABOTAGEM INFORMÁTICA   0

Parecem muitos e não são: a esmagadora maioria são crimes contra pessoas singulares —
burla em vendas em linha, uso indevido de cartão — e não ataques a organizações. Além
disso os acórdãos são anonimizados: dizem "a ofendida" e "o Recorrente", não o nome de
quem foi atingido.

Isso não é defeito da fonte, é o que a jurisprudência é. E encaixa na regra editorial
deste registo, que tem por unidade a entidade atacada e não a vítima singular. A
triagem trata do resto: o que interessa é o caso raro em que o lesado é uma organização
nomeável, e é para esse que esta fonte existe.

**Não entra na recolha automática, e é uma decisão e não um esquecimento.** Medido
sobre 73 acórdãos: 22 passam a triagem e nenhum é um ataque a uma organização. São
crimes contra pessoas, violação de segredo bancário, e doutrina sobre os elementos
típicos das infrações. Pôr isto a alimentar a fila daria trinta por cento de ruído que
um curador teria de rejeitar um a um — e a fadiga de curadoria é o modo de falha mais
provável deste projeto, dito assim desde o primeiro dia.

É uma ferramenta de curador: invoca-se quando se investiga um caso concreto, para
procurar a decisão judicial que o sustente. Foi assim que se chegou ao acórdão do
funcionário do IGFEJ.

Sobre o robots.txt: não tem grupo para `*` e o `urllib.robotparser` autoriza-nos. Ainda
assim a recolha é por descritor, poucas páginas, com o intervalo declarado no catálogo
— nunca um varrimento dos 762 sitemaps.
"""

from __future__ import annotations

import html
import re
from datetime import datetime, timezone

import requests

from ingestao.comum import FONTES, ler_yaml
from ingestao.fontes import Item
from ingestao.rede import AGENTE, TEMPO_LIMITE, _remendar_cadeia, canonicalizar

BASE = "https://jurisprudencia.csm.org.pt"
ITENS = BASE + "/items/loadItems"

# Os nomes das infrações na Lei do Cibercrime, como aparecem nos descritores. É por
# eles que se procura, e não por texto livre: `freesearch` devolve zero para termos
# que existem nos descritores.
DESCRITORES = [
    "FALSIDADE INFORMÁTICA",
    "ACESSO ILEGÍTIMO",
    "DANO INFORMÁTICO",
    "BURLA INFORMÁTICA",
    "SABOTAGEM INFORMÁTICA",
]

POR_PAGINA = 25


def _configuracao() -> dict | None:
    for fonte in ler_yaml(FONTES)["fontes"]:
        if fonte["id"] == "csm-jurisprudencia":
            return fonte if fonte.get("ativa") else None
    return None


def _texto(bruto: str | None) -> str:
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", bruto or ""))).strip()


def _data_iso(data: str | None) -> str | None:
    """"27/01/2022" -> "2022-01-27"."""
    if not data:
        return None
    m = re.match(r"(\d{2})/(\d{2})/(\d{4})", data.strip())
    return f"{m.group(3)}-{m.group(2)}-{m.group(1)}" if m else None


def recolher(descritores: list[str] | None = None, paginas: int = 1) -> list[Item]:
    fonte = _configuracao()
    if not fonte:
        return []

    sessao = requests.Session()
    sessao.headers.update(
        {"User-Agent": AGENTE, "X-Requested-With": "XMLHttpRequest"}
    )
    # Este anfitrião envia a cadeia de certificados incompleta. A reparação é a mesma
    # da camada de rede e continua a validar tudo — ver _remendar_cadeia().
    try:
        # A primeira visita estabelece a sessão. Sem ela o servidor recusa.
        sessao.get(BASE + "/", timeout=TEMPO_LIMITE)
    except requests.exceptions.SSLError:
        remendo = _remendar_cadeia("jurisprudencia.csm.org.pt")
        if not remendo:
            print("  AVISO  csm: cadeia de certificados incompleta e irreparável")
            return []
        sessao.verify = remendo
        try:
            sessao.get(BASE + "/", timeout=TEMPO_LIMITE)
        except requests.RequestException as erro:
            print(f"  AVISO  csm: sessão não estabelecida ({erro})")
            return []
    except requests.RequestException as erro:
        print(f"  AVISO  csm: sessão não estabelecida ({erro})")
        return []

    obtido_em = datetime.now(timezone.utc).isoformat(timespec="seconds")
    itens: list[Item] = []
    vistos: set[str] = set()

    for descritor in descritores or DESCRITORES:
        for pagina in range(1, paginas + 1):
            try:
                # GET, e não POST: por POST o servidor responde 200 com a base
                # inteira, ignorando o filtro em silêncio.
                resposta = sessao.get(
                    ITENS,
                    params={
                        "queries[filter_descriptors]": descritor,
                        "page": pagina,
                        "perPage": POR_PAGINA,
                    },
                    timeout=TEMPO_LIMITE,
                )
                resposta.raise_for_status()
                dados = resposta.json()
            except (requests.RequestException, ValueError) as erro:
                print(f"  AVISO  csm {descritor}: {erro}")
                break

            registos = dados.get("records") or []
            if not registos:
                break

            for r in registos:
                ecli = (r.get("ecli") or "").strip()
                if not ecli or ecli in vistos:
                    continue
                vistos.add(ecli)

                sumario = _texto(r.get("sumario"))
                descs = _texto(r.get("descritores"))
                tribunal = _texto(r.get("tribunal"))
                url = f"{BASE}/ecli/{ecli}"

                itens.append(
                    Item(
                        url=url,
                        url_canonica=canonicalizar(url),
                        titulo=f"{tribunal}, acórdão de {r.get('dataAcordao','')} — {descs[:120]}",
                        publicador="Jurisprudência do CSM",
                        data_publicacao=_data_iso(r.get("dataAcordao")),
                        # O sumário é o que a triagem lê. O acórdão integral fica na
                        # ligação, para quem curar.
                        texto=f"{descs}. {sumario}",
                        fonte="csm-jurisprudencia",
                        obtido_em=obtido_em,
                        tipo_fonte="regulador",
                        extra={
                            "ecli": ecli,
                            "tribunal": tribunal,
                            "descritor_procurado": descritor,
                            "decisao": _texto(r.get("decisao")),
                            # Os acórdãos são anonimizados: dizem "a ofendida" e não o
                            # nome. Um caso só é registável se a entidade lesada for
                            # identificável por outra via.
                            "anonimizado": True,
                        },
                    )
                )

    return itens
