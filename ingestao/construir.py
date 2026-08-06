"""Constrói os índices derivados que o site consome.

Lê data/out/incidentes/*.json (a fonte canónica, escrita por curadoria humana) e escreve
os agregados ao lado. Tudo aqui é derivado e descartável: apagar os índices e voltar a
correr produz exatamente o mesmo resultado.

Não vai à rede. Não altera nenhum incidente.
"""

from __future__ import annotations

import sys
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ingestao.comum import (  # noqa: E402
    DIR_INCIDENTES,
    DIR_OUT,
    DIR_REFERENCIA,
    carregar_entidades,
    carregar_taxonomia,
    escrever_json,
    ler_json,
    ler_yaml,
)


def carregar_incidentes() -> list[dict]:
    incidentes = [ler_json(c) for c in sorted(DIR_INCIDENTES.glob("*.json"))]
    incidentes.sort(key=lambda i: (i["data"]["inicio"], i["id"]), reverse=True)
    return incidentes


def estado_maximo_sustentavel(incidente: dict, taxonomia: dict) -> str:
    """O estado de confirmação mais alto que as fontes deste incidente sustentam.

    É a derivação que a política editorial exige: o grau de confiança sai dos tipos de
    fonte presentes, nunca de um modelo de linguagem. Um curador pode declarar um estado
    mais baixo do que este (por prudência), nunca mais alto.
    """
    estados = taxonomia["estados_confirmacao"]
    fontes = incidente["fontes"]

    def sustenta(fonte: dict, exigidos: set[str]) -> bool:
        if fonte["tipo"] in exigidos:
            return True
        if "comunicado" in exigidos and fonte.get("contem_declaracao_da_entidade"):
            return True
        if "regulador" in exigidos and fonte.get("contem_declaracao_de_autoridade"):
            return True
        return False

    melhor = "alegado_pelo_atacante"
    for nome, regra in sorted(estados.items(), key=lambda kv: kv[1]["peso"]):
        if nome == "desmentido":
            continue  # nunca derivado: é sempre uma decisão editorial explícita
        exigidos = set(regra["exige_fonte_tipo"])
        apoiantes = [f for f in fontes if sustenta(f, exigidos)]
        if not apoiantes:
            continue
        minimo = regra.get("minimo_publicadores")
        if minimo and len({f["publicador"] for f in apoiantes}) < minimo:
            continue
        melhor = nome
        break
    return melhor


def resumir(incidente: dict) -> dict:
    """Versão leve para os índices: o suficiente para listar e filtrar, sem o corpo."""
    return {
        "id": incidente["id"],
        "titulo": incidente["titulo"],
        "data": incidente["data"]["inicio"],
        "precisao_data": incidente["data"]["precisao"],
        "ano": int(incidente["data"]["inicio"][:4]),
        # Os anos que o incidente atravessa. Quase sempre um só; a vaga hacktivista
        # de 2013 a 2016 durou quatro, e sem isto aparecia apenas em 2013 e fazia
        # 2014 e 2015 parecerem anos sem nada — que foi o que aconteceu até alguém
        # perguntar porquê.
        "anos": list(
            range(
                int(incidente["data"]["inicio"][:4]),
                int((incidente["data"].get("fim") or incidente["data"]["inicio"])[:4]) + 1,
            )
        ),
        "setor": incidente["setor"],
        "tipos_ataque": incidente["tipos_ataque"],
        "entidades_afetadas": incidente["entidades_afetadas"],
        "estado_confirmacao": incidente["estado_confirmacao"],
        "ator": (incidente.get("ator") or {}).get("grupo"),
        "n_fontes": len(incidente["fontes"]),
        "tem_disputas": bool(incidente.get("disputas")),
    }


def construir(hoje: str | None = None) -> dict:
    taxonomia = carregar_taxonomia()
    entidades = {e["id"]: e for e in carregar_entidades()}
    incidentes = carregar_incidentes()

    avisos: list[str] = []
    for incidente in incidentes:
        maximo = estado_maximo_sustentavel(incidente, taxonomia)
        declarado = incidente["estado_confirmacao"]
        pesos = taxonomia["estados_confirmacao"]
        if declarado != "desmentido" and pesos[declarado]["peso"] < pesos[maximo]["peso"]:
            avisos.append(
                f"{incidente['id']}: declara '{declarado}' mas as fontes só sustentam "
                f"'{maximo}'."
            )

    # A taxonomia é a autoridade e vive em YAML, para ser legível e comentada. O site
    # precisa dos nomes legíveis, e não vamos meter um parser de YAML no build do Astro.
    escrever_json(DIR_REFERENCIA / "taxonomia.json", taxonomia)

    resumos = [resumir(i) for i in incidentes]
    escrever_json(DIR_OUT / "incidentes.json", resumos)

    # Por entidade, incluindo o impacto em cascata, que é registado à parte para não
    # inflacionar as contagens: o INEM não foi atacado em 2022, foi atingido.
    por_entidade: dict[str, dict] = {}
    for eid, entidade in entidades.items():
        diretos = [r["id"] for r in resumos if eid in r["entidades_afetadas"]]
        cascata = [
            i["id"]
            for i in incidentes
            if eid in i.get("entidades_afetadas_em_cascata", [])
        ]
        if not diretos and not cascata:
            continue
        # As `chaves` seguem para o site: alimentam o índice de pesquisa, para que
        # procurar "MEO" encontre a Altice e "Continente" encontre a Sonae MC.
        por_entidade[eid] = {
            **entidade,
            "incidentes": diretos,
            "incidentes_em_cascata": cascata,
        }
    escrever_json(DIR_OUT / "entidades.json", por_entidade)

    cronologia = defaultdict(list)
    for resumo in resumos:
        cronologia[str(resumo["ano"])].append(resumo["id"])
    escrever_json(DIR_OUT / "cronologia.json", dict(sorted(cronologia.items(), reverse=True)))

    # A contagem de fontes por incidente é publicada de propósito: é o que torna o viés
    # de cobertura mensurável a partir dos próprios dados, em vez de ficar implícito.
    fontes_por_incidente = Counter(r["n_fontes"] for r in resumos)
    tipos = Counter(t for r in resumos for t in r["tipos_ataque"])

    agregados = {
        "total": len(resumos),
        "por_ano": dict(sorted(Counter(r["ano"] for r in resumos).items())),
        "por_setor": dict(Counter(r["setor"] for r in resumos).most_common()),
        "por_tipo_ataque": dict(tipos.most_common()),
        "por_estado_confirmacao": dict(
            Counter(r["estado_confirmacao"] for r in resumos).most_common()
        ),
        "por_ator": dict(
            Counter(r["ator"] for r in resumos if r["ator"]).most_common()
        ),
        "distribuicao_fontes_por_incidente": dict(sorted(fontes_por_incidente.items())),
        "incidentes_com_disputas": sum(1 for r in resumos if r["tem_disputas"]),
    }
    escrever_json(DIR_OUT / "agregados.json", agregados)

    # Uma linha por fonte, com o incidente a que pertence. É a exportação que serve
    # jornalistas: permite ver que órgãos cobriram o quê, e quais os incidentes que só
    # uma fonte sustenta.
    fontes = [
        {
            "incidente_id": incidente["id"],
            "indice": indice,
            **{k: v for k, v in fonte.items() if k != "sha256"},
        }
        for incidente in incidentes
        for indice, fonte in enumerate(incidente["fontes"])
    ]
    escrever_json(DIR_OUT / "fontes.json", fontes)

    # -------------------------------------------------------------------------
    # Contexto oficial: o denominador, em ficheiro próprio.
    #
    # Vive separado de agregados.json de propósito. São contagens de outra
    # entidade, com outro universo e outra metodologia, e a única coisa que não
    # podem sofrer é serem somadas às nossas por distração de quem lê o JSON.
    # Um ficheiro à parte torna a distinção estrutural em vez de documental.
    # A ligação de cada ator ao MITRE ATT&CK, quando existe. É uma ligação e não uma
    # caracterização do incidente: ver o cabeçalho de referencia/atores.yaml.
    atores = ler_yaml(DIR_REFERENCIA / "atores.yaml")
    escrever_json(DIR_OUT / "atores.json", atores)

    contexto = ler_yaml(DIR_REFERENCIA / "cncs.yaml")
    por_ano_registo = Counter(r["ano"] for r in resumos)
    contexto["comparacao"] = {
        str(ano): {
            "cert_pt": dados["incidentes"],
            "neste_registo": por_ano_registo.get(int(ano), 0),
        }
        for ano, dados in contexto["anos"].items()
    }
    escrever_json(DIR_OUT / "contexto.json", contexto)

    manifesto = {
        "construido_em": hoje or date.today().isoformat(),
        "esquema": "incidente-1",
        "licenca_dados": "CC BY 4.0",
        "total_incidentes": len(resumos),
        "total_fontes": len(fontes),
        "total_entidades": len(por_entidade),
        "anos": sorted({r["ano"] for r in resumos}),
    }
    escrever_json(DIR_OUT / "manifesto.json", manifesto)

    return {"manifesto": manifesto, "avisos": avisos}


if __name__ == "__main__":
    resultado = construir()
    m = resultado["manifesto"]
    print(
        f"  {m['total_incidentes']} incidentes, {m['total_fontes']} fontes, "
        f"{m['total_entidades']} entidades, anos {m['anos'][0]}-{m['anos'][-1]}"
    )
    for aviso in resultado["avisos"]:
        print(f"  AVISO  {aviso}")
    sys.exit(1 if resultado["avisos"] else 0)
