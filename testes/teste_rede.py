"""Verifica as garantias da camada de rede.

O teste que mais importa é o do redirecionamento: um servidor externo que responda
302 para 127.0.0.1 tem de ser recusado. É a falha que existe na versão original desta
proteção, no salesRadar, e é fácil de reintroduzir sem dar por isso.
"""

from __future__ import annotations

import http.server
import socket
import sys
import threading
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ingestao import rede  # noqa: E402
from ingestao.comum import ler_yaml  # noqa: E402
from ingestao.comum import FONTES  # noqa: E402


def teste_recusa_esquemas_estranhos():
    for url in ("file:///etc/passwd", "ftp://exemplo.pt/x", "gopher://exemplo.pt"):
        with pytest.raises(rede.DestinoRecusado):
            rede._validar(url)


def teste_recusa_localhost_e_redes_internas():
    for url in (
        "http://127.0.0.1/",
        "http://localhost/",
        "http://10.0.0.1/",
        "http://192.168.1.1/",
        "http://169.254.169.254/latest/meta-data/",
        "http://[::1]/",
    ):
        with pytest.raises(rede.DestinoRecusado):
            rede._validar(url)


def teste_recusa_dominio_nao_declarado():
    """O alistamento é obrigatório: um domínio fora de fontes.yaml é erro, não aviso."""
    with pytest.raises(rede.DestinoRecusado) as erro:
        rede._validar("https://exemplo-que-nao-esta-no-catalogo.pt/artigo")
    assert "não declarado" in str(erro.value)


def teste_dominios_permitidos_vem_do_catalogo():
    permitidos = rede.dominios_permitidos()
    assert "eco.sapo.pt" in permitidos
    assert "ransomware.live" in permitidos
    # Os desativados continuam declarados: desativar não é apagar.
    assert "cnpd.pt" in permitidos


def teste_subdominios_de_dominio_declarado_sao_aceites(monkeypatch):
    monkeypatch.setattr(rede, "_ip_seguro", lambda anfitriao: True)
    assert rede._validar("https://www.eco.sapo.pt/x") == "www.eco.sapo.pt"


def teste_canonicalizar_remove_ruido():
    limpo = rede.canonicalizar(
        "https://ECO.sapo.pt/2022/02/08/artigo/?utm_source=twitter&id=7&fbclid=abc#topo"
    )
    assert limpo == "https://eco.sapo.pt/2022/02/08/artigo?id=7"

    # A mesma peça partilhada de dois sítios tem de dar a mesma chave.
    a = rede.canonicalizar("https://eco.sapo.pt/x/?utm_campaign=a")
    b = rede.canonicalizar("https://eco.sapo.pt/x#seccao")
    assert a == b


def teste_intervalo_por_anfitriao_sai_do_catalogo():
    # O ransomware.live declara 1 pedido por minuto; usamos 65s por margem.
    assert rede._intervalo_do_anfitriao("api.ransomware.live") >= 60
    assert rede._intervalo_do_anfitriao("eco.sapo.pt") == 3


def teste_catalogo_e_coerente():
    catalogo = ler_yaml(FONTES)
    ids = [f["id"] for f in catalogo["fontes"]]
    assert len(ids) == len(set(ids)), "há identificadores de fonte repetidos"
    for fonte in catalogo["fontes"]:
        assert fonte.get("dominios"), f"{fonte['id']} não declara domínios"
        assert fonte["metodo"] in ("rss", "api", "html", "navegador")
        assert isinstance(fonte["ativa"], bool)
        if fonte["metodo"] == "rss" and fonte["ativa"]:
            assert fonte.get("feeds"), f"{fonte['id']} está ativa mas não tem feeds"


class _ServidorQueRedireciona(http.server.BaseHTTPRequestHandler):
    destino = "http://127.0.0.1/interno"

    def do_GET(self):  # noqa: N802
        self.send_response(302)
        self.send_header("Location", self.destino)
        self.end_headers()

    def log_message(self, *args):
        pass


@pytest.fixture
def servidor_malicioso():
    """Servidor local que responde 302 para um endereço interno."""
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        porta = s.getsockname()[1]
    servidor = http.server.HTTPServer(("127.0.0.1", porta), _ServidorQueRedireciona)
    fio = threading.Thread(target=servidor.serve_forever, daemon=True)
    fio.start()
    yield porta
    servidor.shutdown()


def teste_redirecionamento_para_rede_interna_e_recusado(servidor_malicioso, monkeypatch):
    """A verificação tem de correr a CADA salto, não só na URL inicial.

    Simulamos um domínio externo legítimo que redireciona para 127.0.0.1. Se a
    validação só corresse na primeira URL, este pedido chegaria à rede interna.
    """
    porta = servidor_malicioso

    # Fazemos o domínio de partida passar no alistamento e na verificação de IP,
    # deixando apenas o segundo salto por validar — que é o que queremos testar.
    original = rede._validar

    def validar_falso(url: str) -> str:
        anfitriao = (rede.urlparse(url).hostname or "").lower()
        if anfitriao == "fonte-legitima.pt":
            return anfitriao
        return original(url)

    monkeypatch.setattr(rede, "_validar", validar_falso)
    monkeypatch.setattr(rede, "_robots_permite", lambda url, anfitriao: True)
    monkeypatch.setattr(
        rede.requests,
        "get",
        lambda url, **kw: _resposta_302(f"http://127.0.0.1:{porta}/alvo"),
    )

    with pytest.raises(rede.DestinoRecusado):
        rede.obter("https://fonte-legitima.pt/artigo", usar_cache=False)


class _RespostaFalsa:
    def __init__(self, estado: int, cabecalhos: dict):
        self.status_code = estado
        self.headers = cabecalhos
        self.text = ""
        self.encoding = "utf-8"
        self.apparent_encoding = "utf-8"


def _resposta_302(destino: str):
    return _RespostaFalsa(302, {"Location": destino})
