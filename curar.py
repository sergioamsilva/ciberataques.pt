#!/usr/bin/env python3
"""Curadoria: promove candidatos da fila a incidentes publicados.

É aqui que a revisão humana acontece, e é deliberadamente uma ferramenta local de
terminal: sem servidor, sem autenticação, sem base de dados. A publicação continua a
ser um `git commit`, e é essa a garantia de que nada chega ao ar sem alguém olhar.

    python curar.py                 # percorre a fila
    python curar.py --resumo        # só mostra o que está por rever

Teclas por candidato:
    a   aceitar como incidente novo (abre o esboço no editor)
    j   juntar a um incidente existente
    r   rejeitar, com motivo
    s   saltar, decidir depois
    q   sair
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
import tempfile
from datetime import date
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
sys.path.insert(0, str(RAIZ))

from ingestao.agrupar import sugerir_incidente  # noqa: E402
from ingestao.comum import (  # noqa: E402
    DIR_CANDIDATOS,
    DIR_INCIDENTES,
    DIR_REJEITADOS,
    escrever_json,
    ler_json,
    slug,
)
from ingestao.extrair import casar_entidade  # noqa: E402

NEGRITO = "\033[1m"
APAGADO = "\033[2m"
VERMELHO = "\033[31m"
VERDE = "\033[32m"
AMARELO = "\033[33m"
FIM = "\033[0m"


def candidatos() -> list[Path]:
    return sorted(DIR_CANDIDATOS.glob("*.json"))


def _campo(rotulo: str, valor, largura: int = 22) -> str:
    return f"  {APAGADO}{rotulo:<{largura}}{FIM}{valor}"


def mostrar(candidato: dict) -> None:
    origem = candidato.get("origem", {})
    extraccao = candidato.get("extraccao", {})

    print(f"\n{NEGRITO}{candidato.get('titulo_origem', '(sem título)')}{FIM}")
    print(_campo("publicador", origem.get("publicador", "?")))
    print(_campo("data", origem.get("data", "?")))
    print(_campo("url", origem.get("url", "?")))
    print(_campo("tipo de fonte", origem.get("tipo_fonte", "noticia")))

    print(f"\n  {APAGADO}--- extração ---{FIM}")
    print(_campo("é incidente PT", extraccao.get("e_incidente_pt")))
    print(_campo("entidade", extraccao.get("entidade_mencionada") or "—"))
    print(_campo("setor", extraccao.get("setor_sugerido") or "—"))
    print(_campo("tipos", ", ".join(extraccao.get("tipos_ataque") or []) or "—"))
    print(_campo("data ocorrência", extraccao.get("data_ocorrencia") or "—"))
    print(_campo("ator", extraccao.get("ator_mencionado") or "—"))
    print(_campo("dados pessoais", extraccao.get("dados_pessoais_mencionados")))
    print(_campo("confiança extração", extraccao.get("confianca")))

    afirmacoes = extraccao.get("afirmacoes") or []
    if afirmacoes:
        print(f"\n  {APAGADO}--- quem afirma o quê ---{FIM}")
        for a in afirmacoes:
            print(f"    {AMARELO}{a['atribuida_a']}{FIM}: {a['texto']}")

    entidade_id, sugestao_nova = casar_entidade(extraccao.get("entidade_mencionada"))
    if entidade_id:
        print(f"\n  {VERDE}entidade conhecida:{FIM} {entidade_id}")
    elif sugestao_nova:
        print(
            f"\n  {VERMELHO}entidade desconhecida:{FIM} {sugestao_nova}"
            f"\n  {APAGADO}acrescentar a referencia/entidades.yaml antes de aceitar{FIM}"
        )

    sugestao = candidato.get("sugestao_agrupamento")
    if sugestao:
        print(
            f"\n  {AMARELO}pode pertencer a:{FIM} {sugestao['incidente_id']}"
            f" ({sugestao['similaridade']}) — {sugestao['razao']}"
        )


def esboco(candidato: dict, entidade_id: str) -> dict:
    """Esboço de incidente a partir da extração, para o curador editar.

    Note-se o que NÃO vem preenchido: o resumo, que é sempre escrito por uma pessoa,
    e o estado de confirmação, que é derivado dos tipos de fonte.
    """
    extraccao = candidato.get("extraccao", {})
    origem = candidato.get("origem", {})
    data_inicio = extraccao.get("data_ocorrencia") or origem.get("data") or date.today().isoformat()
    ano = data_inicio[:4]
    tipo_fonte = origem.get("tipo_fonte", "noticia")

    return {
        "id": f"{ano}-{slug(entidade_id)}",
        "titulo": f"Ciberataque a {extraccao.get('entidade_mencionada') or entidade_id}",
        "resumo": "POR ESCREVER: três a cinco frases, com o que as fontes sustentam.",
        "entidades_afetadas": [entidade_id],
        "setor": extraccao.get("setor_sugerido") or "tecnologia",
        "tipos_ataque": extraccao.get("tipos_ataque") or ["intrusao"],
        "data": {
            "inicio": data_inicio,
            "precisao": extraccao.get("precisao_data") or "desconhecida",
            "divulgacao": origem.get("data"),
        },
        # Derivado do tipo de fonte, não escolhido: uma peça de site de extorsão só
        # pode entrar como alegação.
        "estado_confirmacao": (
            "alegado_pelo_atacante" if tipo_fonte == "leak_site" else "noticiado_por_uma_fonte"
        ),
        "ator": {
            "grupo": extraccao.get("ator_mencionado"),
            "atribuicao_por": "reivindicacao" if extraccao.get("ator_mencionado") else None,
            "confianca": "baixa" if extraccao.get("ator_mencionado") else None,
            "nota": None,
        },
        "dados_pessoais": {
            "afetados": extraccao.get("dados_pessoais_mencionados"),
            "categorias": [],
            "titulares_declarados": None,
            "nota": None,
        },
        "impacto": {"servicos_afetados": []},
        "notificacoes": {},
        "cronologia": [],
        "fontes": [
            {
                "tipo": tipo_fonte,
                "url": origem.get("url"),
                "url_arquivo": None,
                "publicador": origem.get("publicador"),
                "data": origem.get("data"),
                "titulo": candidato.get("titulo_origem"),
                "excerto": extraccao.get("excerto_chave"),
                "sha256": origem.get("sha256"),
                "estado_ligacao": "viva",
            }
        ],
        "disputas": [],
        "relacionados": [],
        "revisao": {
            "curador": os.environ.get("CURADOR", "ss"),
            "data": date.today().isoformat(),
            "versao": 1,
            "nota": None,
        },
        "correcoes": [],
    }


def abrir_no_editor(dados: dict) -> dict | None:
    editor = os.environ.get("EDITOR", "nano")
    with tempfile.NamedTemporaryFile("w+", suffix=".json", delete=False, encoding="utf-8") as f:
        import json

        json.dump(dados, f, ensure_ascii=False, indent=2, sort_keys=True)
        caminho = Path(f.name)
    try:
        subprocess.run([editor, str(caminho)], check=False)
        import json

        return json.loads(caminho.read_text(encoding="utf-8"))
    except Exception as erro:
        print(f"  {VERMELHO}não foi possível ler o ficheiro editado: {erro}{FIM}")
        return None
    finally:
        caminho.unlink(missing_ok=True)


def aceitar(candidato: dict, caminho_candidato: Path) -> None:
    extraccao = candidato.get("extraccao", {})
    entidade_id, sugestao_nova = casar_entidade(extraccao.get("entidade_mencionada"))
    if not entidade_id:
        print(
            f"  {VERMELHO}entidade desconhecida ({sugestao_nova}). "
            f"Acrescente-a a referencia/entidades.yaml e volte a este candidato.{FIM}"
        )
        return

    proposta = esboco(candidato, entidade_id)
    destino = DIR_INCIDENTES / f"{proposta['id']}.json"
    sufixo = 2
    while destino.exists():
        proposta["id"] = f"{proposta['id'].rsplit('-', 1)[0]}-{sufixo}" if proposta["id"][-1].isdigit() else f"{proposta['id']}-{sufixo}"
        destino = DIR_INCIDENTES / f"{proposta['id']}.json"
        sufixo += 1

    editado = abrir_no_editor(proposta)
    if editado is None:
        return
    if "POR ESCREVER" in editado.get("resumo", ""):
        print(f"  {VERMELHO}o resumo continua por escrever. Nada foi publicado.{FIM}")
        return

    escrever_json(destino, editado)
    caminho_candidato.unlink(missing_ok=True)
    print(f"  {VERDE}escrito{FIM} data/out/incidentes/{destino.name}")
    print(f"  {APAGADO}rever com `git diff` e comprometer. O commit é a publicação.{FIM}")


def rejeitar(candidato: dict, caminho: Path) -> None:
    motivo = input("  motivo da rejeição: ").strip()
    candidato["estado"] = "rejeitado"
    candidato["motivo_rejeicao"] = motivo or "sem motivo indicado"
    candidato["rejeitado_em"] = date.today().isoformat()
    escrever_json(DIR_REJEITADOS / caminho.name, candidato)
    caminho.unlink(missing_ok=True)
    # As rejeições ficam versionadas: são registo do que decidimos não publicar, e
    # evitam que o mesmo caso volte a consumir tempo de curadoria.
    print(f"  {APAGADO}rejeitado e arquivado em data/fila/rejeitados/{FIM}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--resumo", action="store_true", help="só listar a fila")
    args = parser.parse_args()

    fila = candidatos()
    if not fila:
        print("A fila está vazia.")
        return

    if args.resumo:
        print(f"{len(fila)} candidatos por rever:\n")
        for caminho in fila:
            c = ler_json(caminho)
            print(f"  {c.get('titulo_origem', caminho.stem)[:90]}")
            print(f"    {APAGADO}{c.get('origem', {}).get('publicador', '?')}{FIM}")
        return

    print(f"{len(fila)} candidatos por rever.\n")
    for caminho in fila:
        candidato = ler_json(caminho)
        mostrar(candidato)
        escolha = input(f"\n  {NEGRITO}[a]ceitar [j]untar [r]ejeitar [s]altar [q]sair: {FIM}").strip().lower()

        if escolha == "q":
            break
        if escolha == "a":
            aceitar(candidato, caminho)
        elif escolha == "j":
            alvo = input("  id do incidente de destino: ").strip()
            destino = DIR_INCIDENTES / f"{alvo}.json"
            if not destino.exists():
                print(f"  {VERMELHO}não existe: {alvo}{FIM}")
                continue
            # Juntar é acrescentar uma fonte a um incidente existente. Deliberadamente
            # feito no editor: acrescentar uma fonte muda o grau de confiança, e isso
            # tem de passar por olhos humanos.
            incidente = ler_json(destino)
            origem = candidato.get("origem", {})
            incidente["fontes"].append(
                {
                    "tipo": origem.get("tipo_fonte", "noticia"),
                    "url": origem.get("url"),
                    "url_arquivo": None,
                    "publicador": origem.get("publicador"),
                    "data": origem.get("data"),
                    "titulo": candidato.get("titulo_origem"),
                    "excerto": candidato.get("extraccao", {}).get("excerto_chave"),
                    "sha256": origem.get("sha256"),
                    "estado_ligacao": "viva",
                }
            )
            incidente["revisao"]["versao"] = incidente["revisao"].get("versao", 1) + 1
            incidente["revisao"]["data"] = date.today().isoformat()
            editado = abrir_no_editor(incidente)
            if editado:
                escrever_json(destino, editado)
                caminho.unlink(missing_ok=True)
                print(f"  {VERDE}fonte acrescentada a{FIM} {alvo}")
        elif escolha == "r":
            rejeitar(candidato, caminho)
        else:
            print(f"  {APAGADO}saltado{FIM}")

    print(f"\n{APAGADO}Reveja com `git diff` e comprometa. O commit é a publicação.{FIM}")


if __name__ == "__main__":
    main()
