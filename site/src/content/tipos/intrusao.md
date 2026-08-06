---
tipo: intrusao
titulo: O que é uma intrusão
resumo: >-
  Acesso não autorizado a sistemas, quando o objetivo final não é público. É a
  classificação mais comum deste registo, e isso diz mais sobre o que as
  organizações portuguesas divulgam do que sobre o que lhes acontece.
fases:
  - Acesso inicial
  - Persistência
  - Reconhecimento
  - Movimento lateral
  - Recolha
visivel_a_partir_de: 5
nota_fases: >-
  Sem encriptação nem extorsão não há efeito visível nenhum, e é por isso que
  estes casos se descobrem tantas vezes por aviso de terceiros.
revisto_em: "2026-08-05"
pontos_chave:
  - >-
    Não implica encriptação nem publicação de dados. Alguém entrou e esteve lá dentro — o que fez, e durante quanto tempo, é quase sempre o que fica por apurar.
  - >-
    Descobre-se tarde porque não há um perfil estável de «normal» contra o qual comparar: o tráfego de uma organização muda com a hora, a época e cada projeto novo.
  - >-
    Em vários casos deste registo a entidade soube por terceiros — pelo próprio atacante, ou por aparecer listada num site de extorsão. Não é negligência: é a natureza do problema.
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
  - autores: "Sommer, R., Paxson, V."
    ano: 2010
    titulo: "Outside the Closed World: On Using Machine Learning for Network Intrusion Detection"
    publicacao: "2010 IEEE Symposium on Security and Privacy"
    doi: "10.1109/sp.2010.25"
    nota: >-
      Explica porque a deteção de intrusões é um problema estruturalmente diferente
      dos outros: não existe um perfil estável de «normal», e o custo de um falso
      positivo num ambiente real é altíssimo.
  - autores: "Khraisat, A., Gondal, I., Vamplew, P., Kamruzzaman, J."
    ano: 2019
    titulo: "Survey of intrusion detection systems: techniques, datasets and challenges"
    publicacao: "Cybersecurity, 2(20)"
    doi: "10.1186/s42400-019-0038-7"
    nota: >-
      Revisão das abordagens de deteção e das suas limitações, incluindo a
      dificuldade persistente com ataques que não correspondem a assinatura conhecida.
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

## Porque se descobre tarde

A deteção de intrusões é um problema estruturalmente mais difícil do que parece, e a
literatura é explícita quanto à razão: ao contrário de outros domínios onde se
distingue o normal do anómalo, aqui não existe um perfil estável de normalidade. O
tráfego de uma organização varia com a hora, a época, um projeto novo, uma campanha.

A consequência prática está visível neste arquivo: em vários casos portugueses a
entidade soube do ataque por terceiros — pelo próprio atacante, como na
[Universidade de Aveiro](/incidentes/2026-universidade-de-aveiro/), ou por
aparecer listada num site de extorsão. Não é negligência; é a natureza do problema.
