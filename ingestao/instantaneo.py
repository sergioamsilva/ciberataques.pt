"""Deteção de revisões silenciosas.

Adaptado de snsRadar/ingest/snapshot.py, com a mesma filosofia e três aplicações em
vez de uma:

  1. Fontes já citadas. Um artigo editado depois de publicado é prática real na
     imprensa portuguesa, e um artigo removido deixa a nossa citação a apontar para o
     vazio. Guardar o SHA-256 permite provar o que a fonte dizia numa data concreta.
  2. Ficheiros do registo canónico, para o site poder mostrar "última verificação"
     com prova.
  3. Vítimas que desaparecem de um tracker de sites de extorsão. Não é ruído: é sinal,
     e tipicamente significa que o resgate foi pago.

Os manifestos ficam versionados para sempre. São a prova.
"""

from __future__ import annotations

import hashlib
import sys
from datetime import date, datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ingestao.comum import (  # noqa: E402
    DIR_INCIDENTES,
    DIR_INSTANTANEOS,
    escrever_json,
    ler_json,
)
from ingestao.rede import (  # noqa: E402
    DestinoRecusado,
    ErroDeRede,
    RecursoBloqueado,
    obter,
)

MANIFESTO_ATUAL = DIR_INSTANTANEOS / "manifesto-atual.json"


def sha256(texto: str) -> str:
    return hashlib.sha256(texto.encode("utf-8")).hexdigest()


def _manifesto_anterior() -> dict:
    if MANIFESTO_ATUAL.exists():
        try:
            return ler_json(MANIFESTO_ATUAL)
        except Exception:
            return {}
    return {}


def instantaneo_do_registo() -> dict[str, str]:
    """Impressão digital de cada incidente publicado."""
    return {
        caminho.stem: sha256(caminho.read_text(encoding="utf-8"))
        for caminho in sorted(DIR_INCIDENTES.glob("*.json"))
    }


def verificar_fontes(limite: int | None = None) -> list[dict]:
    """Revisita as fontes citadas e relata as que mudaram ou morreram.

    Devolve uma lista de ocorrências em linguagem legível, para o log da execução.
    Não altera o registo: a decisão de marcar uma ligação como morta é editorial.
    """
    anterior = _manifesto_anterior().get("fontes", {})
    ocorrencias: list[dict] = []
    atual: dict[str, dict] = {}
    contados = 0

    for caminho in sorted(DIR_INCIDENTES.glob("*.json")):
        incidente = ler_json(caminho)
        for indice, fonte in enumerate(incidente["fontes"]):
            if limite is not None and contados >= limite:
                break
            chave = f"{incidente['id']}#{indice}"
            url = fonte["url"]
            contados += 1

            try:
                resposta = obter(url, usar_cache=False)
            except (RecursoBloqueado, DestinoRecusado) as erro:
                # 403 e afins significam que o servidor nos recusa, não que a página
                # desapareceu. O Público devolve 403 a todos os automatismos, e
                # tratá-lo como ligação morta marcaria dezenas de fontes válidas
                # como perdidas.
                atual[chave] = {"url": url, "estado": "nao_verificavel"}
                ocorrencias.append(
                    {
                        "tipo": "nao_verificavel",
                        "incidente": incidente["id"],
                        "url": url,
                        "detalhe": str(erro),
                    }
                )
                continue
            except ErroDeRede as erro:
                # 404, 410 e falhas de rede persistentes: a ligação morreu de facto.
                # A ficha passa a apontar só para a cópia arquivada.
                atual[chave] = {"url": url, "estado": "morta"}
                ocorrencias.append(
                    {
                        "tipo": "morreu",
                        "incidente": incidente["id"],
                        "url": url,
                        "detalhe": str(erro),
                    }
                )
                continue

            impressao = sha256(resposta.texto)
            registo_anterior = anterior.get(chave, {})
            if registo_anterior.get("sha256") and registo_anterior["sha256"] != impressao:
                ocorrencias.append(
                    {
                        "tipo": "revisto",
                        "incidente": incidente["id"],
                        "url": url,
                        "detalhe": "o conteúdo mudou desde a última verificação",
                    }
                )
            atual[chave] = {
                "url": url,
                "sha256": impressao,
                "estado": "viva",
                "verificado_em": date.today().isoformat(),
            }

    manifesto = {
        "gerado_em": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "registo": instantaneo_do_registo(),
        "fontes": atual,
    }
    escrever_json(MANIFESTO_ATUAL, manifesto)
    carimbo = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    escrever_json(DIR_INSTANTANEOS / f"manifesto-{carimbo}.json", manifesto)

    return ocorrencias


def comparar_vitimas(vitimas_atuais: set[str]) -> list[str]:
    """Vítimas que constavam do tracker e desapareceram.

    Um desaparecimento costuma significar que o resgate foi pago, e isso é informação,
    não ruído. Registamos para que a cronologia de um incidente o possa refletir.
    """
    anterior = set(_manifesto_anterior().get("vitimas_leak", []))
    return sorted(anterior - vitimas_atuais)


if __name__ == "__main__":
    limite = None
    if "--verificar-fontes" in sys.argv:
        for i, arg in enumerate(sys.argv):
            if arg == "--limite" and i + 1 < len(sys.argv):
                limite = int(sys.argv[i + 1])
        ocorrencias = verificar_fontes(limite=limite)
        if not ocorrencias:
            print("  todas as fontes verificadas estão iguais e vivas")
        for o in ocorrencias:
            marca = {"morreu": "MORREU", "revisto": "revisto", "nao_verificavel": "?"}[o["tipo"]]
            print(f"  {marca:6} {o['incidente']}  {o['url']}")
        sys.exit(1 if any(o["tipo"] == "morreu" for o in ocorrencias) else 0)
    print("Uso: python ingestao/instantaneo.py --verificar-fontes [--limite N]")
