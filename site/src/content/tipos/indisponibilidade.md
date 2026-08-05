---
tipo: indisponibilidade
titulo: O que significa indisponibilidade de serviço
resumo: >-
  O serviço deixou de funcionar por ação deliberada, sem que a causa técnica seja
  pública. É uma classificação de efeito, não de método — e nomeia com precisão
  aquilo que se sabe quando não se sabe mais.
revisto_em: "2026-08-05"
referencias:
  - autores: "Cichonski, P., Millar, T., Grance, T., Scarfone, K."
    ano: 2012
    titulo: "Computer Security Incident Handling Guide: Recommendations of the National Institute of Standards and Technology"
    publicacao: "NIST Special Publication 800-61 Revision 2"
    doi: "10.6028/NIST.SP.800-61r2"
    nota: >-
      Define o impacto de um incidente em três dimensões — funcional, de
      informação e de recuperabilidade —, distinção que sustenta a separação entre
      efeito e causa usada aqui.
  - autores: "Mirkovic, J., Reiher, P."
    ano: 2004
    titulo: "A taxonomy of DDoS attack and DDoS defense mechanisms"
    publicacao: "ACM SIGCOMM Computer Communication Review, 34(2)"
    doi: "10.1145/997150.997156"
    nota: >-
      Referência para a causa técnica mais comum de indisponibilidade deliberada,
      quando essa causa é conhecida.
---

## O que é

Indisponibilidade é a classificação usada quando um serviço deixou de funcionar
**por ação deliberada** e a causa técnica não é pública. Não diz como; diz o quê.

## Porque existe uma categoria para um efeito

Porque a alternativa seria pior. Perante um comunicado que diz apenas que os
serviços estão em baixo, há três caminhos:

1. Inventar a causa. Inaceitável.
2. Não registar. Perde-se o incidente.
3. Registar o que se sabe, com o nome exato do que se sabe.

Este registo escolhe o terceiro. `indisponibilidade` significa: houve interrupção
deliberada, e ninguém disse publicamente porquê.

Quando a causa é conhecida, aparece a par: os casos de [negação de serviço](/tipos/ddos/)
têm ambas as classificações, porque aí sabe-se o método *e* o efeito.

## O que a indisponibilidade custa

O impacto raramente se limita à organização atingida. Este registo tem os casos que
o demonstram melhor:

- No [ataque à Vodafone](/incidentes/2022-vodafone-portugal/), em fevereiro de 2022,
  cerca de quatro milhões de clientes ficaram sem serviço — e com eles o INEM, os
  bombeiros e a rede Multibanco, que dependiam daquela rede. Nenhuma destas
  entidades foi atacada.
- No [ataque à AMA](/incidentes/2024-ama/), o que caiu foi a infraestrutura de
  autenticação do Estado. O efeito chegou ao portal do SNS 24 e a médicos
  impedidos de enviar receitas por mensagem escrita.
- Na [OesteCIM](/incidentes/2025-oestecim/), doze municípios ficaram com serviços
  degradados por um único ataque.

É por isso que este registo separa `entidades_afetadas` de
`entidades_afetadas_em_cascata`: contar o INEM como vítima de um ciberataque em
2022 seria factualmente errado, mas ignorar que ficou sem comunicações seria
esconder o essencial.

## Quanto tempo dura

A duração é o melhor indicador de gravidade que este registo consegue oferecer de
forma comparável, e varia em duas ordens de grandeza:

| Caso | Tempo até reposição |
|---|---|
| [FC Porto](/incidentes/2022-sporting-fc-porto/) | menos de uma hora |
| [Vodafone](/incidentes/2022-vodafone-portugal/) | quatro dias |
| [AMA](/incidentes/2024-ama/) | mais de uma semana |
| [SESARAM](/incidentes/2023-sesaram/) | cinco semanas |
| [Câmara da Guarda](/incidentes/2026-camara-municipal-da-guarda/) | mais de quatro meses |

O que distingue os extremos raramente é a sofisticação do ataque. É se as cópias de
segurança sobreviveram — comparar [Alcobaça](/incidentes/2024-camara-municipal-de-alcobaca/),
que as tinha intactas, com a [Figueira da Foz](/incidentes/2022-camara-municipal-da-figueira-da-foz/),
onde foram atingidas.
