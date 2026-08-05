"""Constantes, caminhos e utilitários partilhados por todo o pipeline.

Nada aqui toca na rede. Ver ingestao/rede.py para isso.
"""

from __future__ import annotations

import json
import re
import unicodedata
from pathlib import Path
from typing import Any

RAIZ = Path(__file__).resolve().parent.parent

DIR_REFERENCIA = RAIZ / "referencia"
DIR_DADOS = RAIZ / "data"
DIR_BRUTO = DIR_DADOS / "bruto"
DIR_ARQUIVO = DIR_DADOS / "arquivo"
DIR_FILA = DIR_DADOS / "fila"
DIR_CANDIDATOS = DIR_FILA / "candidatos"
DIR_REJEITADOS = DIR_FILA / "rejeitados"
DIR_OUT = DIR_DADOS / "out"
DIR_INCIDENTES = DIR_OUT / "incidentes"
DIR_INSTANTANEOS = DIR_DADOS / "instantaneos"
DIR_REGISTO = DIR_INSTANTANEOS / "registo"

ESQUEMA_INCIDENTE = DIR_REFERENCIA / "esquema-incidente.json"
TAXONOMIA = DIR_REFERENCIA / "taxonomia.yaml"
ENTIDADES = DIR_REFERENCIA / "entidades.yaml"
FONTES = DIR_REFERENCIA / "fontes.yaml"

# Limites de rede. Constantes e não configuráveis: uma fonte que precise de mais
# do que isto é uma fonte com um problema, e o problema deve ser resolvido no
# módulo dela, não a subir um timeout global.
TEMPO_LIMITE = 30
TENTATIVAS = 4

# Imposto pelo direito de citação (CDADC art. 75.º/2 g) e pelo direito conexo dos
# editores de imprensa (DL 47/2023, que exclui "excertos muito curtos"). Se um editor
# reclamar, removemos o excerto e mantemos a ligação: degradação sem perda de utilidade.
MAX_EXCERTO = 200


def garantir_dirs() -> None:
    """Cria as pastas que o pipeline assume existirem."""
    for caminho in (
        DIR_BRUTO,
        DIR_ARQUIVO,
        DIR_CANDIDATOS,
        DIR_REJEITADOS,
        DIR_INCIDENTES,
        DIR_INSTANTANEOS,
        DIR_REGISTO,
    ):
        caminho.mkdir(parents=True, exist_ok=True)


def normalizar(texto: str) -> str:
    """Reduz um nome à sua forma comparável: minúsculas, sem acentos, sem pontuação.

    Usado para casar nomes de entidades vindos de notícias contra as `chaves` de
    referencia/entidades.yaml. É deliberadamente permissivo, pelo que serve para
    SUGERIR uma correspondência e nunca para a decidir sozinho.
    """
    texto = unicodedata.normalize("NFKD", texto.lower())
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    texto = re.sub(r"[^a-z0-9\s]", " ", texto)
    return re.sub(r"\s+", " ", texto).strip()


# Formas jurídicas portuguesas, removidas antes de comparar nomes de entidades.
# "Vodafone Portugal — Comunicações Pessoais, S.A." e "Vodafone Portugal" têm de
# casar sem que o sufixo estrague a comparação.
_FORMAS_JURIDICAS = (
    "sociedade anonima", "unipessoal lda", "sgps", "s a", "sa", "lda", "ldª",
    "epe", "eperam", "ip", "crl", "ace", "eim", "em",
)
_PREFIXOS_PUBLICOS = (
    "municipio de", "camara municipal de", "junta de freguesia de",
    "instituto", "agencia", "direcao geral", "centro hospitalar",
)


def normalizar_entidade(nome: str) -> str:
    """Normalização agressiva para nomes de organizações.

    Remove formas jurídicas e prefixos administrativos. É MAIS permissiva do que
    normalizar() e por isso ainda menos apta a decidir sozinha: usar só para propor
    correspondências a um curador humano.
    """
    texto = normalizar(nome)
    for forma in _FORMAS_JURIDICAS:
        texto = re.sub(rf"\b{re.escape(forma)}\b", " ", texto)
    for prefixo in _PREFIXOS_PUBLICOS:
        if texto.startswith(prefixo + " "):
            texto = texto[len(prefixo) :]
            break
    return re.sub(r"\s+", " ", texto).strip()


def slug(texto: str) -> str:
    """Converte um nome num identificador estável para URL."""
    return re.sub(r"[^a-z0-9]+", "-", normalizar(texto)).strip("-")


def ler_json(caminho: Path) -> Any:
    with caminho.open(encoding="utf-8") as f:
        return json.load(f)


def escrever_json(caminho: Path, dados: Any) -> None:
    """Escreve JSON estável: chaves ordenadas, indentação fixa, newline final.

    A estabilidade importa mais do que parece. O registo vive em git e é revisto em
    diff; uma reordenação de chaves produziria um diff enorme e ilegível, e a revisão
    humana é a única coisa entre um boato e a publicação.
    """
    caminho.parent.mkdir(parents=True, exist_ok=True)
    texto = json.dumps(dados, ensure_ascii=False, indent=2, sort_keys=True)
    caminho.write_text(texto + "\n", encoding="utf-8")


def ler_yaml(caminho: Path) -> Any:
    import yaml

    with caminho.open(encoding="utf-8") as f:
        return yaml.safe_load(f)


def carregar_taxonomia() -> dict:
    return ler_yaml(TAXONOMIA)


def carregar_entidades() -> list[dict]:
    return ler_yaml(ENTIDADES)


def indice_entidades() -> dict[str, str]:
    """Mapa de chave normalizada para id de entidade.

    Inclui o nome, o nome curto e todas as `chaves` declaradas. É o que permite que
    "MEO" resolva para altice-portugal e "Continente" para sonae-mc.
    """
    indice: dict[str, str] = {}
    for entidade in carregar_entidades():
        candidatos = [entidade["nome"], entidade.get("nome_curto", "")]
        candidatos += entidade.get("chaves", [])
        for candidato in candidatos:
            if not candidato:
                continue
            indice.setdefault(normalizar_entidade(candidato), entidade["id"])
    return indice
