"""Nenhum nome de condenado aparece no registo, nem nos títulos e endereços citados.

A secção 4 da política editorial deixou, em outubro de 2026, de admitir nomes de
condenados. O risco não está no texto que escrevemos — esse revê-se — mas no que
citamos: o título de uma notícia ou o endereço de um artigo trazem o nome sem que
ninguém o escreva. Foi assim que um entrou, através do título e do slug de uma fonte.

Os nomes vivem em referencia/nomes-proibidos.txt apenas como SHA-256, e o teste
compara os hashes de cada sequência de duas a quatro palavras de todos os textos.
"""

from __future__ import annotations

import hashlib
import re
import unicodedata
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
LISTA = RAIZ / "referencia" / "nomes-proibidos.txt"
ONDE = [
    (RAIZ / "data" / "out", "*.json"),
    (RAIZ / "data" / "fila", "*.json"),
    (RAIZ / "referencia", "*.*"),
    (RAIZ / "site" / "src", "*.*"),
]


def normalizar(texto: str) -> str:
    texto = unicodedata.normalize("NFKD", texto.lower())
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    return " ".join(re.sub(r"[^a-z0-9]+", " ", texto).split())


def hash_do_nome(nome: str) -> str:
    return hashlib.sha256(normalizar(nome).encode()).hexdigest()


def proibidos() -> set[str]:
    return {
        linha.strip()
        for linha in LISTA.read_text(encoding="utf-8").splitlines()
        if linha.strip() and not linha.startswith("#")
    }


def teste_a_lista_so_tem_hashes():
    for h in proibidos():
        assert re.fullmatch(r"[0-9a-f]{64}", h), "a lista guarda hashes, nunca nomes"


def teste_nenhum_nome_proibido_aparece():
    alvo = proibidos()
    achados = []
    for pasta, padrao in ONDE:
        for f in pasta.rglob(padrao):
            if not f.is_file():
                continue
            try:
                palavras = normalizar(f.read_text(encoding="utf-8")).split()
            except UnicodeDecodeError:
                continue
            for n in (2, 3, 4):
                for i in range(len(palavras) - n + 1):
                    if hashlib.sha256(" ".join(palavras[i : i + n]).encode()).hexdigest() in alvo:
                        achados.append(str(f.relative_to(RAIZ)))
                        break
    assert not achados, f"nome de condenado em: {sorted(set(achados))}"
