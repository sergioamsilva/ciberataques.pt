---
tipo: intrusao
titulo: O que é uma intrusão
resumo: >-
  Acesso não autorizado a sistemas, quando o objetivo final não é público. É a
  classificação mais comum deste registo, e isso diz mais sobre o que as
  organizações portuguesas divulgam do que sobre o que lhes acontece.
revisto_em: "2026-08-05"
referencias:
  - autores: "Cichonski, P., Millar, T., Grance, T., Scarfone, K."
    ano: 2012
    titulo: "Computer Security Incident Handling Guide: Recommendations of the National Institute of Standards and Technology"
    publicacao: "NIST Special Publication 800-61 Revision 2"
    doi: "10.6028/NIST.SP.800-61r2"
    nota: >-
      Guia de referência para tratamento de incidentes, incluindo as fases de
      deteção, análise, contenção e recuperação.
  - autores: "MITRE"
    ano: 2026
    titulo: "MITRE ATT&CK: Enterprise Matrix"
    publicacao: "MITRE Corporation"
    url: "https://attack.mitre.org/matrices/enterprise/"
    nota: >-
      Catálogo das técnicas observadas em intrusões reais, organizado pelas fases
      em que ocorrem. É a base de vocabulário comum da área.
---

## O que é

Intrusão é o acesso não autorizado a sistemas de uma organização. Neste registo
usa-se quando há acesso confirmado mas **o objetivo final do atacante não é
público** — não se sabe se houve encriptação, se houve cópia de dados, ou se o
acesso serviu apenas para preparar outra coisa.

## Porque é a classificação mais frequente aqui

É o tipo mais comum deste arquivo, e a razão não é técnica: é de comunicação. A
maior parte dos comunicados portugueses confirma que houve um ataque e evita
descrever a natureza.

Vê-se em série. A [Câmara de Loures](/incidentes/2022-camara-municipal-de-loures/)
descreveu um ataque "malicioso e deliberado" sem especificar que serviços foram
afetados nem se houve exposição de dados. O
[Grupo Visabeira](/incidentes/2023-visabeira/) não esclareceu que efeitos concretos
o ataque teve. A [Câmara da Guarda](/incidentes/2026-camara-municipal-da-guarda/)
falou em "incidente cibernético complexo".

Quando um registo classifica vinte e cinco incidentes como intrusão, isso é um
retrato da opacidade da comunicação, não da técnica dos atacantes.

## O tempo entre entrar e ser notado

A literatura sobre tratamento de incidentes separa deteção de ocorrência, e a
distância entre as duas é onde o dano se produz. Este registo documenta casos em
que essa distância é grande e casos em que a deteção nem sequer foi da vítima:

- No [EMGFA](/incidentes/2022-emgfa/), Portugal soube por alerta de serviços de
  informações norte-americanos, que encontraram documentos classificados à venda.
- No [Ministério dos Negócios Estrangeiros](/incidentes/2022-ministerio-dos-negocios-estrangeiros/),
  o alerta partiu do Serviço de Informações de Segurança.
- Na [Universidade de Aveiro](/incidentes/2026-universidade-de-aveiro/), foram os
  próprios atacantes que contactaram a instituição, à procura de um acordo.

Em nenhum destes casos a organização detetou o problema sozinha.

## Intrusão não é sinónimo de fuga de dados

Confirmar acesso não é confirmar cópia. São afirmações diferentes e este registo
mantém-nas separadas: um incidente pode ter `intrusao` sem ter `exfiltracao_dados`,
e o campo de dados pessoais fica a `null` — que significa *não é público*, e não
*não aconteceu*.

A distinção entre não ter havido e não se saber é, em muitos destes casos, a única
coisa honesta a registar.
