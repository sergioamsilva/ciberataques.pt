---
tipo: cadeia_fornecimento
titulo: O que é um ataque à cadeia de fornecimento
resumo: >-
  A organização é atingida através de um fornecedor, não por intrusão direta. Um
  único ataque produz muitas vítimas, e cada uma tem de responder por um incidente
  que não pôde prevenir nem investigar.
revisto_em: "2026-08-05"
referencias:
  - autores: "Ladisa, P., Plate, H., Martinez, M., Barais, O."
    ano: 2023
    titulo: "SoK: Taxonomy of Attacks on Open-Source Software Supply Chains"
    publicacao: "2023 IEEE Symposium on Security and Privacy"
    doi: "10.1109/SP46215.2023.10179304"
    nota: >-
      Taxonomia sistemática com 107 vetores de ataque distintos, ligados a 94
      incidentes reais e a 33 medidas de mitigação.
  - autores: "ENISA"
    ano: 2021
    titulo: "ENISA Threat Landscape for Supply Chain Attacks"
    publicacao: "Agência da União Europeia para a Cibersegurança"
    url: "https://www.enisa.europa.eu/publications/threat-landscape-for-supply-chain-attacks"
    nota: >-
      Relatório oficial europeu, com a distinção entre o ataque ao fornecedor e o
      efeito no cliente.
---

## O que é

Um ataque à cadeia de fornecimento atinge uma organização **através de outra**. O
alvo direto é um fornecedor, um prestador de serviços ou um componente de
software; as vítimas são todos os que dependem dele.

## Porque muda o cálculo do atacante

A economia é evidente: comprometer um fornecedor usado por milhares de clientes é
mais rentável do que atacar mil organizações uma a uma. A taxonomia de Ladisa e
colegas cataloga 107 vetores distintos e liga-os a 94 incidentes reais, o que dá a
medida de quão estabelecido está este modelo.

Este registo tem exemplos dos dois lados da relação:

- O ataque à [plataforma Canvas](/incidentes/2026-canvas-instituicoes-portuguesas/)
  foi a um fornecedor norte-americano, e teve efeito na Universidade Europeia e no
  IPAM. Nenhuma das duas foi atacada; ambas ficaram expostas.
- O ataque à [OesteCIM](/incidentes/2025-oestecim/) degradou serviços em **doze
  municípios do Oeste** de uma só vez. É cadeia de fornecimento dentro da própria
  administração pública.
- Na [rede de cacifos dos CTT](/incidentes/2026-ctt/), o comprometimento foi num
  sistema associado ao serviço, não no núcleo da empresa.

## O problema para quem é atingido

Quem sofre o efeito raramente controla a causa. Uma câmara municipal do Oeste não
podia auditar os sistemas da comunidade intermunicipal; uma universidade não
audita o código da plataforma que licencia. Fica com o dever de notificar os
titulares e com a responsabilidade pública, sem ter tido meios de prevenir nem de
investigar.

É também o que torna estes casos difíceis de contar. Quantos incidentes foi o
ataque à OesteCIM: um, ou doze? Este registo conta **um**, com as entidades
identificadas — porque contar doze inflacionaria a estatística com base num único
evento, e porque não temos informação específica sobre o impacto em cada município.

## Como aparece neste registo

A classificação `cadeia_fornecimento` é aplicada quando a entidade portuguesa foi
atingida **através de terceiro**, e regista-se sempre quem confirmou exposição.
Instituições que usam a mesma plataforma mas nada declararam não entram: registá-las
seria inventar cobertura.
