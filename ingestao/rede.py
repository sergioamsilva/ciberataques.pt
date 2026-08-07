"""O único ponto de saída para a rede.

Nenhum módulo de fonte faz `requests.get` diretamente. Tudo passa por aqui, para que
as garantias sejam verificáveis num só sítio:

  - o destino não é uma rede interna, mesmo depois de redirecionamentos;
  - o domínio está declarado em referencia/fontes.yaml;
  - o robots.txt do sítio permite o acesso;
  - respeita-se um intervalo mínimo entre pedidos ao mesmo servidor;
  - identificamo-nos honestamente, com forma de contacto.

Um agregador cívico que raspa sítios de terceiros tem a obrigação de se portar bem.
Estas não são otimizações: são a diferença entre um projeto defensável e um scraper.
"""

from __future__ import annotations

import ipaddress
import socket
import ssl
import subprocess
import tempfile
import time
import urllib.robotparser
from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import urlparse, urlunparse

import requests

from ingestao.comum import (
    DIR_BRUTO,
    FONTES,
    TEMPO_LIMITE,
    TENTATIVAS,
    escrever_json,
    ler_json,
    ler_yaml,
)

# Identificamo-nos e damos forma de contacto. Um operador de sítio que queira falar
# connosco, ou bloquear-nos, tem de conseguir fazê-lo.
AGENTE = "ciberataques.pt/1.0 (+https://ciberataques.pt/sobre; correcoes@ciberataques.pt)"

MAX_REDIRECIONAMENTOS = 5
CACHE_ROBOTS_SEGUNDOS = 24 * 3600
FICHEIRO_CACHE = DIR_BRUTO / "_cache.json"


class ErroDeRede(Exception):
    """Falha ao obter um recurso, já com as tentativas esgotadas."""


class DestinoRecusado(ErroDeRede):
    """O destino não passou nas verificações de segurança ou de boa conduta."""


class RecursoBloqueado(ErroDeRede):
    """O servidor recusou-nos o acesso, mas o recurso existe.

    Distinguir isto de um 404 é essencial na verificação de ligações: o Público
    devolve 403 a acessos automatizados, e tratar isso como ligação morta marcaria
    dezenas de fontes válidas como perdidas.
    """


@dataclass
class Resposta:
    url_final: str
    estado: int
    texto: str
    cabecalhos: dict
    """True quando o servidor respondeu 304: o conteúdo não mudou desde a última visita."""
    nao_modificado: bool = False


@dataclass
class _EstadoAnfitriao:
    ultimo_pedido: float = 0.0
    robots: urllib.robotparser.RobotFileParser | None = None
    robots_obtido_em: float = 0.0
    bloqueado: bool = field(default=False)


_anfitrioes: dict[str, _EstadoAnfitriao] = {}
_fontes_declaradas: dict | None = None


def _catalogo() -> dict:
    global _fontes_declaradas
    if _fontes_declaradas is None:
        _fontes_declaradas = ler_yaml(FONTES) if Path(FONTES).exists() else {"fontes": []}
    return _fontes_declaradas


def dominios_permitidos() -> set[str]:
    """Domínios declarados em referencia/fontes.yaml, incluindo os desativados.

    O alistamento é obrigatório: um domínio fora da lista é erro, não aviso. Sem isto,
    bastaria um redirecionamento ou uma ligação num feed para nos pôr a descarregar de
    qualquer sítio da internet.
    """
    permitidos: set[str] = set()
    for fonte in _catalogo().get("fontes", []):
        for dominio in fonte.get("dominios", []):
            permitidos.add(dominio.lower().removeprefix("www."))
    return permitidos


def _ip_seguro(anfitriao: str) -> bool:
    """Recusa destinos que resolvam para redes internas.

    Portado de salesRadar/backend/app/services/enrichment_service.py:24, com uma
    diferença que importa: aqui é chamado a cada salto de redirecionamento, e não
    apenas na URL inicial. O original valida só o primeiro pedido, pelo que um 302
    para 127.0.0.1 passaria.
    """
    try:
        infos = socket.getaddrinfo(anfitriao, None, socket.AF_UNSPEC, socket.SOCK_STREAM)
    except socket.gaierror:
        return False
    if not infos:
        return False
    for info in infos:
        endereco = info[4][0]
        try:
            ip = ipaddress.ip_address(endereco)
        except ValueError:
            return False
        if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved:
            return False
        if ip.is_multicast or ip.is_unspecified:
            return False
        # Ponto de metadados das nuvens: nunca é um destino legítimo para nós.
        if endereco.startswith("169.254."):
            return False
    return True


def _validar(url: str) -> str:
    partes = urlparse(url)
    if partes.scheme not in ("http", "https"):
        raise DestinoRecusado(f"esquema não permitido: {url}")
    anfitriao = (partes.hostname or "").lower()
    if not anfitriao:
        raise DestinoRecusado(f"URL sem anfitrião: {url}")

    registavel = anfitriao.removeprefix("www.")
    permitidos = dominios_permitidos()
    if permitidos and not any(
        registavel == d or registavel.endswith("." + d) for d in permitidos
    ):
        raise DestinoRecusado(
            f"domínio não declarado em referencia/fontes.yaml: {anfitriao}"
        )

    if not _ip_seguro(anfitriao):
        raise DestinoRecusado(f"destino resolve para rede interna ou inválida: {anfitriao}")
    return anfitriao


def _estado(anfitriao: str) -> _EstadoAnfitriao:
    return _anfitrioes.setdefault(anfitriao, _EstadoAnfitriao())


def _texto_do_robots(url: str) -> str | None:
    """Obtém o robots.txt com o NOSSO user-agent, seguindo redirecionamentos.

    Não se usa RobotFileParser.read(): esse método vai à rede com o user-agent do
    urllib, que muitos WAF devolvem 403, e o parser interpreta 403 como "proibido
    tudo". O efeito é desativar em silêncio fontes que na realidade nos permitem o
    acesso — foi o que aconteceu com o Diário de Notícias, que declara `Allow: /`.

    Devolve None quando não há robots.txt legível, o que é diferente de uma proibição.
    """
    partes = urlparse(url)
    alvo = f"{partes.scheme}://{partes.netloc}/robots.txt"

    for _ in range(MAX_REDIRECIONAMENTOS):
        anfitriao = (urlparse(alvo).hostname or "").lower()
        if not anfitriao or not _ip_seguro(anfitriao):
            return None
        try:
            resposta = requests.get(
                alvo,
                headers={"User-Agent": AGENTE},
                timeout=TEMPO_LIMITE,
                allow_redirects=False,
            )
        except requests.RequestException:
            return None

        if resposta.status_code in (301, 302, 303, 307, 308):
            destino = resposta.headers.get("Location")
            if not destino:
                return None
            alvo = requests.compat.urljoin(alvo, destino)
            continue

        if resposta.status_code == 200:
            if resposta.encoding is None:
                resposta.encoding = resposta.apparent_encoding
            return resposta.text
        # 404 e afins: não há regras, logo não há proibição.
        # 401 e 403 no próprio robots.txt significam que não o conseguimos ler, e não
        # que estamos proibidos de tudo. Tratamos como ausência de regras.
        return None
    return None


def _robots_permite(url: str, anfitriao: str) -> bool:
    estado = _estado(anfitriao)
    agora = time.monotonic()
    if estado.robots is None or agora - estado.robots_obtido_em > CACHE_ROBOTS_SEGUNDOS:
        leitor = urllib.robotparser.RobotFileParser()
        texto = _texto_do_robots(url)
        # Alguns robots.txt portugueses começam com BOM, o que faz o parser ignorar a
        # primeira diretiva `User-agent` e desalinhar todas as regras seguintes.
        linhas = (texto or "").lstrip("﻿").splitlines()
        leitor.parse(linhas)
        estado.robots = leitor
        estado.robots_obtido_em = agora
    return estado.robots.can_fetch(AGENTE, url)


def _intervalo_do_anfitriao(anfitriao: str) -> float:
    registavel = anfitriao.removeprefix("www.")
    for fonte in _catalogo().get("fontes", []):
        for dominio in fonte.get("dominios", []):
            d = dominio.lower().removeprefix("www.")
            if registavel == d or registavel.endswith("." + d):
                return float(fonte.get("intervalo_s", 2))
    return 2.0


def _esperar_a_vez(anfitriao: str) -> None:
    estado = _estado(anfitriao)
    intervalo = _intervalo_do_anfitriao(anfitriao)
    decorrido = time.monotonic() - estado.ultimo_pedido
    if estado.ultimo_pedido and decorrido < intervalo:
        time.sleep(intervalo - decorrido)
    estado.ultimo_pedido = time.monotonic()


def _cache() -> dict:
    if FICHEIRO_CACHE.exists():
        try:
            return ler_json(FICHEIRO_CACHE)
        except Exception:
            return {}
    return {}


def _guardar_cache(cache: dict) -> None:
    escrever_json(FICHEIRO_CACHE, cache)


def canonicalizar(url: str) -> str:
    """Remove o ruído que faz a mesma página parecer várias.

    Parâmetros de campanha e âncoras não mudam o conteúdo, mas mudam a chave de
    deduplicação. Sem isto, o mesmo artigo partilhado de três sítios diferentes
    entraria três vezes na fila de candidatos.
    """
    partes = urlparse(url)
    consulta = "&".join(
        p
        for p in partes.query.split("&")
        if p
        and not p.split("=")[0].lower().startswith(("utm_", "fbclid", "gclid", "ref", "_hs"))
    )
    return urlunparse(
        (partes.scheme, partes.netloc.lower(), partes.path.rstrip("/") or "/", "", consulta, "")
    )


# Cadeias de certificados incompletas, por anfitrião. Ver _confianca_para().
_INTERMEDIARIOS: dict[str, str | None] = {}


def _remendar_cadeia(anfitriao: str) -> str | None:
    """Tenta obter o intermediário que o servidor não enviou.

    Só é chamada **depois** de a verificação normal falhar, e nunca antes: ir buscar
    o intermediário a toda a gente seria um pedido a mais por anfitrião e esconderia
    problemas reais de certificado atrás de uma tentativa de reparação.

    Devolve o caminho de um conjunto que inclui o intermediário em falta, ou None se
    não for possível repará-lo — caso em que o erro original se mantém, como deve.

    Existe por causa de uma fonte concreta. A base de jurisprudência do Conselho
    Superior da Magistratura não envia o intermediário da Sectigo, e a validação
    falha com "unable to get local issuer certificate". Os browsers escondem isto
    porque vão buscar o certificado em falta ao endereço declarado na extensão de
    acesso à autoridade; o `requests` e o `curl` não o fazem.

    A distinção que importa: isto **não desliga a verificação**. O certificado
    continua a ser validado, e continua a ter de encadear até uma raiz de confiança
    do sistema — apenas se fornece o elo que o servidor deixou de enviar. Desligar a
    verificação seria aceitar qualquer certificado, e num projeto que valida cada
    destino contra SSRF isso seria uma contradição.
    """
    if anfitriao in _INTERMEDIARIOS:
        return _INTERMEDIARIOS[anfitriao]

    _INTERMEDIARIOS[anfitriao] = None
    try:
        pem = ssl.get_server_certificate((anfitriao, 443), timeout=TEMPO_LIMITE)
    except Exception:  # noqa: BLE001
        return None

    # O endereço onde a autoridade publica o certificado que assinou este.
    try:
        detalhes = subprocess.run(
            ["openssl", "x509", "-noout", "-text"],
            input=pem, capture_output=True, text=True, timeout=15,
        ).stdout
    except Exception:  # noqa: BLE001
        return None

    aia = None
    for linha in detalhes.splitlines():
        if "CA Issuers - URI:" in linha:
            aia = linha.split("CA Issuers - URI:", 1)[1].strip()
            break
    if not aia:
        return None

    try:
        bruto = requests.get(aia, timeout=TEMPO_LIMITE, headers={"User-Agent": AGENTE})
        bruto.raise_for_status()
        convertido = subprocess.run(
            ["openssl", "x509", "-inform", "DER"],
            input=bruto.content, capture_output=True, timeout=15,
        )
        intermediario = (
            convertido.stdout.decode() if convertido.returncode == 0
            else bruto.content.decode("ascii", "ignore")
        )
        if "BEGIN CERTIFICATE" not in intermediario:
            return None

        import certifi

        destino = Path(tempfile.gettempdir()) / f"ciberataques-ca-{anfitriao}.pem"
        destino.write_text(
            intermediario.strip() + "\n" + Path(certifi.where()).read_text(),
            encoding="utf-8",
        )
        _INTERMEDIARIOS[anfitriao] = str(destino)
        return str(destino)
    except Exception:  # noqa: BLE001
        return None


def obter(url: str, *, usar_cache: bool = True, aceitar: str | None = None) -> Resposta:
    """Descarrega um recurso, com todas as verificações aplicadas.

    Levanta DestinoRecusado se o destino não for admissível, e ErroDeRede se as
    tentativas se esgotarem.
    """
    atual = url
    cache = _cache() if usar_cache else {}
    chave = canonicalizar(url)

    for salto in range(MAX_REDIRECIONAMENTOS + 1):
        anfitriao = _validar(atual)

        if not _robots_permite(atual, anfitriao):
            raise DestinoRecusado(f"robots.txt não permite: {atual}")

        cabecalhos = {"User-Agent": AGENTE, "Accept-Language": "pt-PT,pt;q=0.9"}
        if aceitar:
            cabecalhos["Accept"] = aceitar
        guardado = cache.get(chave, {}) if salto == 0 else {}
        if guardado.get("etag"):
            cabecalhos["If-None-Match"] = guardado["etag"]
        if guardado.get("modificado_em"):
            cabecalhos["If-Modified-Since"] = guardado["modificado_em"]

        ultimo_erro: Exception | None = None
        resposta = None
        for tentativa in range(TENTATIVAS):
            _esperar_a_vez(anfitriao)
            try:
                confianca = _INTERMEDIARIOS.get(anfitriao) or True
                try:
                    resposta = requests.get(
                        atual,
                        headers=cabecalhos,
                        timeout=TEMPO_LIMITE,
                        allow_redirects=False,  # revalidamos cada salto à mão
                        verify=confianca,
                    )
                except requests.exceptions.SSLError:
                    # Uma cadeia incompleta é erro do servidor, não motivo para
                    # desistir nem para aceitar qualquer certificado. Tenta-se obter
                    # o elo em falta; se não der, o erro segue.
                    remendo = _remendar_cadeia(anfitriao)
                    if not remendo:
                        raise
                    resposta = requests.get(
                        atual,
                        headers=cabecalhos,
                        timeout=TEMPO_LIMITE,
                        allow_redirects=False,
                        verify=remendo,
                    )
                break
            except requests.RequestException as erro:
                ultimo_erro = erro
                # Recuo exponencial simples: 1s, 2s, 4s.
                time.sleep(2**tentativa)
        if resposta is None:
            raise ErroDeRede(f"{url}: {ultimo_erro}")

        if resposta.status_code in (429, 503):
            espera = resposta.headers.get("Retry-After")
            atraso = float(espera) if espera and espera.isdigit() else 60.0
            time.sleep(min(atraso, 300))
            continue

        if resposta.status_code == 304:
            return Resposta(atual, 304, "", dict(resposta.headers), nao_modificado=True)

        if resposta.status_code in (301, 302, 303, 307, 308):
            destino = resposta.headers.get("Location")
            if not destino:
                raise ErroDeRede(f"{atual}: redirecionamento sem destino")
            atual = requests.compat.urljoin(atual, destino)
            continue

        if resposta.status_code in (401, 403, 406, 451):
            raise RecursoBloqueado(f"{atual}: HTTP {resposta.status_code}")

        if resposta.status_code >= 400:
            raise ErroDeRede(f"{atual}: HTTP {resposta.status_code}")

        # Muitos feeds portugueses declaram ISO-8859-1 e partem-se se forem lidos
        # como UTF-8. Deixamos o requests decidir a partir dos cabeçalhos, e só
        # adivinhamos quando ele não sabe.
        if resposta.encoding is None:
            resposta.encoding = resposta.apparent_encoding

        if usar_cache:
            cache[chave] = {
                "etag": resposta.headers.get("ETag"),
                "modificado_em": resposta.headers.get("Last-Modified"),
                "visto_em": time.time(),
            }
            _guardar_cache(cache)

        return Resposta(atual, resposta.status_code, resposta.text, dict(resposta.headers))

    raise ErroDeRede(f"{url}: demasiados redirecionamentos")
