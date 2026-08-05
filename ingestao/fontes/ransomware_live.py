"""Vítimas portuguesas publicadas em sites de extorsão, via o tracker ransomware.live.

Esta é a fonte que exige mais cuidado de todo o projeto, por três razões:

  1. O que aqui vem é a versão do atacante. Tudo entra na fila marcado como alegação
     e nunca pode ser promovido a confirmado sem fonte independente. A garantia é
     estrutural: o tipo de fonte é `leak_site`, e a taxonomia não permite que um
     incidente só com fontes deste tipo suba na escala de confiança.
  2. Nunca espelhamos o conteúdo deles, nunca ligamos a endereços .onion, e citamos
     sempre o tracker. A ligação pública aponta para a página do tracker, não para o
     sítio do grupo.
  3. O limite declarado é de um pedido por minuto por endpoint. Está em
     referencia/fontes.yaml e é a camada de rede que o impõe.

O nível gratuito declara-se para uso pessoal: pedir a chave PRO gratuita antes de
usar isto em produção pública.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone

from ingestao.comum import FONTES, ler_yaml
from ingestao.fontes import Item
from ingestao.rede import DestinoRecusado, ErroDeRede, canonicalizar, obter

PAGINA_PUBLICA = "https://www.ransomware.live/map/PT"


def _configuracao() -> dict | None:
    catalogo = ler_yaml(FONTES)
    for fonte in catalogo["fontes"]:
        if fonte["id"] == "ransomware-live":
            return fonte if fonte.get("ativa") else None
    return None


def _data(registo: dict) -> str | None:
    for campo in ("discovered", "published", "attackdate"):
        valor = registo.get(campo)
        if not valor:
            continue
        texto = str(valor).strip().replace("T", " ")
        candidata = texto[:10]
        try:
            datetime.strptime(candidata, "%Y-%m-%d")
            return candidata
        except ValueError:
            continue
    return None


def recolher() -> list[Item]:
    fonte = _configuracao()
    if not fonte:
        return []

    try:
        resposta = obter(fonte["endpoint"], aceitar="application/json")
    except (ErroDeRede, DestinoRecusado) as erro:
        print(f"  AVISO  ransomware-live: {erro}")
        return []

    if resposta.nao_modificado:
        return []

    try:
        registos = json.loads(resposta.texto)
    except json.JSONDecodeError as erro:
        print(f"  AVISO  ransomware-live: resposta não é JSON válido ({erro})")
        return []

    if isinstance(registos, dict):
        registos = registos.get("victims") or registos.get("data") or []

    agora = datetime.now(timezone.utc).isoformat(timespec="seconds")
    itens: list[Item] = []

    for registo in registos:
        if not isinstance(registo, dict):
            continue
        vitima = (
            registo.get("victim")
            or registo.get("post_title")
            or registo.get("name")
            or ""
        ).strip()
        if not vitima:
            continue
        grupo = (registo.get("group") or registo.get("group_name") or "").strip()

        # A ligação pública aponta sempre para o tracker, nunca para o sítio do grupo.
        # Se o registo trouxer um endereço .onion, ignoramo-lo por completo.
        url = PAGINA_PUBLICA

        itens.append(
            Item(
                url=url,
                url_canonica=canonicalizar(f"{url}#{vitima.lower()}"),
                titulo=f"{vitima} listada em site de extorsão"
                + (f" ({grupo})" if grupo else ""),
                publicador="ransomware.live",
                data_publicacao=_data(registo),
                # Não copiamos a descrição publicada pelo grupo: é texto escrito por
                # adversários, com valor informativo nulo e risco de manipulação.
                texto=(
                    f"O grupo {grupo or 'não identificado'} listou {vitima} no seu site "
                    "de extorsão. Alegação do atacante, sem confirmação independente."
                ),
                fonte="ransomware_live",
                obtido_em=agora,
                tipo_fonte="leak_site",
                extra={
                    "vitima": vitima,
                    "grupo": grupo,
                    "setor_declarado": registo.get("activity") or "",
                },
            )
        )

    return itens
