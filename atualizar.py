#!/usr/bin/env python3
"""Orquestrador do ciberataques.pt.

Falha alto ao primeiro erro: um registo parcialmente construído é pior do que um
registo não construído, porque parece bom.

    python atualizar.py              # reconstrói os índices a partir de data/out
    python atualizar.py --site       # + build do Astro e índice de pesquisa
    python atualizar.py --sem-testes # salta a validação (só para depuração)

A recolha de fontes NÃO está aqui, e não está por decisão de arquitetura: quando
existir, enche uma fila de candidatos e nunca escreve em data/out. A promoção de um
candidato a incidente publicado é sempre um ato humano, seguido de um commit.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import time
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
sys.path.insert(0, str(RAIZ))

from ingestao.comum import garantir_dirs  # noqa: E402


def passo(titulo: str):
    print(f"\n\033[1m{titulo}\033[0m")
    return time.monotonic()


def feito(inicio: float) -> None:
    print(f"  concluído em {time.monotonic() - inicio:.1f}s")


def correr(comando: list[str], cwd: Path | None = None) -> None:
    resultado = subprocess.run(comando, cwd=cwd or RAIZ)
    if resultado.returncode != 0:
        print(f"\n\033[31mFALHOU:\033[0m {' '.join(comando)}")
        sys.exit(resultado.returncode)


def python_do_venv() -> str:
    venv = RAIZ / ".venv" / "bin" / "python"
    return str(venv) if venv.exists() else sys.executable


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--site", action="store_true", help="constrói também o site")
    parser.add_argument("--sem-testes", action="store_true", help="salta a validação")
    args = parser.parse_args()

    garantir_dirs()
    py = python_do_venv()

    if not args.sem_testes:
        t = passo("Validar o registo")
        correr([py, "-m", "pytest"])
        feito(t)

    t = passo("Construir os índices")
    correr([py, "ingestao/construir.py"])
    feito(t)

    if args.site:
        site = RAIZ / "site"
        t = passo("Construir o site")
        correr(["npx", "astro", "build"], cwd=site)
        feito(t)

        # O índice de pesquisa é gerado a partir do HTML já construído, pelo que tem
        # de vir sempre depois do astro build. Invertê-los produz um índice do build
        # anterior, silenciosamente desatualizado.
        t = passo("Indexar a pesquisa")
        correr(["npx", "pagefind", "--site", "dist"], cwd=site)
        feito(t)

    print("\n\033[32mPronto.\033[0m")


if __name__ == "__main__":
    main()
