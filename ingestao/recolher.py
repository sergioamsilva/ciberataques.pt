"""Recolha completa: fontes → triagem → deduplicação → extração → fila de candidatos.

Termina na fila. Deliberadamente: nada aqui escreve em data/out. A promoção de um
candidato a incidente publicado é feita à mão com curar.py, e a publicação é um commit.

Correr sem chave de modelo é útil e suportado: a recolha e a triagem funcionam, e os
candidatos ficam sem extração, para um curador preencher.
"""

from __future__ import annotations

import sys
from datetime import date, datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ingestao.agrupar import deduplicar, sugerir_incidente  # noqa: E402
from ingestao.comum import (  # noqa: E402
    DIR_BRUTO,
    DIR_CANDIDATOS,
    DIR_REJEITADOS,
    escrever_json,
    garantir_dirs,
    ler_json,
)
from ingestao.fontes import Item, recolher_de  # noqa: E402
from ingestao.triagem import triar_muitos  # noqa: E402

VISTOS = DIR_BRUTO / "_vistos.json"
FONTES_ATIVAS = ["rss_media", "ransomware_live", "cnpd"]


def _vistos() -> set[str]:
    if VISTOS.exists():
        try:
            return set(ler_json(VISTOS))
        except Exception:
            return set()
    return set()


def _guardar_vistos(chaves: set[str]) -> None:
    escrever_json(VISTOS, sorted(chaves))


def _ja_na_fila() -> set[str]:
    """Chaves de itens já em fila ou já rejeitados.

    Sem isto, um caso rejeitado voltaria a aparecer todos os dias, que é a forma mais
    rápida de fazer um curador desistir.
    """
    chaves: set[str] = set()
    for pasta in (DIR_CANDIDATOS, DIR_REJEITADOS):
        for caminho in pasta.glob("*.json"):
            try:
                chave = ler_json(caminho).get("origem", {}).get("chave")
            except Exception:
                continue
            if chave:
                chaves.add(chave)
    return chaves


def _id_candidato(item: Item) -> str:
    return f"cand-{date.today().isoformat().replace('-', '')}-{item.chave[:8]}"


def _extraccao_de_leak_site(item: Item) -> dict:
    """Extração determinística para itens de trackers de sites de extorsão.

    Estes registos já vêm estruturados, com vítima, grupo e data em campos próprios.
    Não há aqui nada que um modelo de linguagem faça melhor, e evitamos processar
    texto escrito por adversários. `e_incidente_pt` fica a null e não a true: quem
    decide que uma vítima listada é um incidente do registo é um curador.
    """
    return {
        "e_incidente_pt": None,
        "razao": "listagem em site de extorsão; exige confirmação independente",
        "entidade_mencionada": item.extra.get("vitima"),
        "setor_sugerido": None,
        "tipos_ataque": ["ransomware"],
        "data_ocorrencia": item.data_publicacao,
        "precisao_data": "dia" if item.data_publicacao else "desconhecida",
        "ator_mencionado": item.extra.get("grupo") or None,
        "dados_pessoais_mencionados": None,
        "afirmacoes": [
            {
                "texto": f"{item.extra.get('vitima')} foi listada no site de extorsão.",
                "atribuida_a": item.extra.get("grupo") or "atacante",
            }
        ],
        "excerto_chave": None,
        "confianca": 1.0,
    }


def motivo_para_rejeitar(
    tipo_fonte: str,
    sugestao: dict | None,
    e_incidente: bool | None,
    extraccao: dict,
) -> str | None:
    """Porque é que este candidato não deve chegar à fila de curadoria, se não deve.

    Duas razões, e a segunda é recente.

    Uma listagem em site de extorsão não funda um incidente, e desde 8 de agosto de
    2026 nem sequer chega à fila quando não há nada a que se ligar. Não é desconfiança
    do tracker: é uma contagem. Das vinte e sete alegações que chegaram a ser
    publicadas, nenhuma ganhou alguma vez fonte independente — o argumento de que
    subiriam com o tempo não descrevia a realidade. Ver a política editorial 3.1.

    A listagem com `sugestao_agrupamento` sobrevive, e é essa a diferença que
    interessa: não vai fundar um incidente, vai juntar-se a um que já existe e que
    alguém independente confirmou. Aí é corroboração — diz quem reivindicou e quando —
    e vale o tempo de quem cura.
    """
    if tipo_fonte == "leak_site" and not sugestao:
        return (
            "listagem em site de extorsão sem incidente documentado a que se ligar; "
            "uma alegação de atacante não sustenta uma entrada (política editorial 3.1)"
        )
    if e_incidente is False:
        return extraccao.get("razao") or "não é incidente português"
    return None


def recolher(usar_llm: bool = True, max_llm: int | None = None) -> dict:
    garantir_dirs()
    vistos = _vistos() | _ja_na_fila()

    brutos: list[Item] = []
    for nome in FONTES_ATIVAS:
        try:
            obtidos = recolher_de(nome)
        except Exception as erro:
            print(f"  AVISO  fonte {nome} falhou por completo: {erro}")
            continue
        print(f"  {nome}: {len(obtidos)} itens")
        brutos.extend(obtidos)

    novos = [i for i in brutos if i.chave not in vistos]
    aprovados, rejeitados = triar_muitos(novos)
    unicos = deduplicar(aprovados)

    print(
        f"  recolhidos {len(brutos)} · novos {len(novos)} · "
        f"triados {len(aprovados)} · únicos {len(unicos)}"
    )

    extrair_fn = None
    if usar_llm:
        try:
            from ingestao.extrair import MAX_CANDIDATOS_DIA, extrair

            extrair_fn = extrair
            if max_llm is None:
                max_llm = MAX_CANDIDATOS_DIA
        except Exception as erro:
            print(f"  AVISO  extração por modelo indisponível ({erro}); segue sem ela")

    if max_llm is not None and len(unicos) > max_llm:
        print(
            f"  AVISO  {len(unicos)} candidatos excedem o limite diário de {max_llm}. "
            f"Ficam {len(unicos) - max_llm} por extrair, e entram na fila sem extração."
        )

    escritos = 0
    agora = datetime.now(timezone.utc).isoformat(timespec="seconds")
    gastos_llm = 0

    for item in unicos:
        # Os itens de sites de extorsão já trazem vítima, grupo e data em campos
        # estruturados. Mandá-los ao modelo seria pagar para extrair o que já vem
        # extraído, e ainda por cima a partir de texto escrito por adversários.
        if item.tipo_fonte == "leak_site":
            extraccao = _extraccao_de_leak_site(item)
        elif extrair_fn and (max_llm is None or gastos_llm < max_llm):
            extraccao = extrair_fn(item) or {}
            gastos_llm += 1
        else:
            extraccao = {}

        # Um item que o modelo diz não ser incidente português vai direto para os
        # rejeitados, com o motivo. Não desaparece: fica registado que decidimos não
        # o publicar, e não volta a consumir tempo de curadoria.
        e_incidente = extraccao.get("e_incidente_pt")
        entidade = extraccao.get("entidade_mencionada")

        sugestao = None
        if entidade:
            from ingestao.extrair import casar_entidade

            entidade_id, _ = casar_entidade(entidade)
            sugestao = sugerir_incidente(
                entidade_id,
                extraccao.get("data_ocorrencia") or item.data_publicacao,
                extraccao.get("tipos_ataque"),
            )

        candidato = {
            "id": _id_candidato(item),
            "estado": "novo",
            "origem": {
                "fonte": item.fonte,
                "publicador": item.publicador,
                "url": item.url,
                "url_canonica": item.url_canonica,
                "data": item.data_publicacao,
                "sha256": item.sha256,
                "chave": item.chave,
                "tipo_fonte": item.tipo_fonte,
            },
            "titulo_origem": item.titulo,
            "extraccao": extraccao,
            "confianca_llm": extraccao.get("confianca"),
            "sugestao_agrupamento": sugestao,
            "motivo_rejeicao": None,
            "triado_em": agora,
        }

        motivo = motivo_para_rejeitar(item.tipo_fonte, sugestao, e_incidente, extraccao)
        if motivo:
            candidato["estado"] = "rejeitado"
            candidato["motivo_rejeicao"] = motivo
            escrever_json(DIR_REJEITADOS / f"{candidato['id']}.json", candidato)
        else:
            escrever_json(DIR_CANDIDATOS / f"{candidato['id']}.json", candidato)
            escritos += 1

        vistos.add(item.chave)

    # Os rejeitados pela triagem determinística não vão para a fila: são demasiados e
    # o motivo é mecânico. Guardamos só a chave, para não voltarem.
    for item, _ in rejeitados:
        vistos.add(item.chave)

    _guardar_vistos(vistos)

    return {
        "recolhidos": len(brutos),
        "novos": len(novos),
        "triados": len(aprovados),
        "unicos": len(unicos),
        "candidatos": escritos,
    }


if __name__ == "__main__":
    usar_llm = "--sem-llm" not in sys.argv
    resultado = recolher(usar_llm=usar_llm)
    print(f"\n  {resultado['candidatos']} candidatos novos na fila")
    if resultado["candidatos"]:
        print("  rever com: python curar.py")
