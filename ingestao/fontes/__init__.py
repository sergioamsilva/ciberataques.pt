"""Fontes de recolha.

Contrato único: cada módulo expõe `recolher() -> list[Item]`. Quem chama não precisa
de saber se por trás está um feed RSS, uma API ou um raspador de HTML, e trocar o
método de uma fonte é mudar um campo em referencia/fontes.yaml, não reescrever código.
"""

from __future__ import annotations

import hashlib
from dataclasses import asdict, dataclass, field


@dataclass
class Item:
    """Uma peça recolhida, já normalizada.

    É matéria-prima, não um incidente. Nada daqui chega ao registo sem passar pela
    triagem, pela extração e por um curador humano.
    """

    url: str
    url_canonica: str
    titulo: str
    publicador: str
    data_publicacao: str | None
    texto: str
    fonte: str
    obtido_em: str
    """Tipo de fonte na taxonomia, para o candidato herdar a proveniência correta."""
    tipo_fonte: str = "noticia"
    extra: dict = field(default_factory=dict)

    @property
    def sha256(self) -> str:
        """Impressão digital do conteúdo, para detetar edições silenciosas."""
        return hashlib.sha256(
            (self.titulo + "\n" + self.texto).encode("utf-8")
        ).hexdigest()

    @property
    def chave(self) -> str:
        """Chave de deduplicação ao nível do item."""
        return hashlib.sha256(
            (self.url_canonica + "\n" + self.titulo.strip().lower()).encode("utf-8")
        ).hexdigest()

    def para_dict(self) -> dict:
        dados = asdict(self)
        dados["sha256"] = self.sha256
        dados["chave"] = self.chave
        return dados


REGISTO: dict[str, str] = {
    "rss_media": "ingestao.fontes.rss_media",
    "ransomware_live": "ingestao.fontes.ransomware_live",
}


def recolher_de(nome: str) -> list[Item]:
    import importlib

    if nome not in REGISTO:
        raise KeyError(f"fonte desconhecida: {nome}. Conhecidas: {sorted(REGISTO)}")
    modulo = importlib.import_module(REGISTO[nome])
    return modulo.recolher()
