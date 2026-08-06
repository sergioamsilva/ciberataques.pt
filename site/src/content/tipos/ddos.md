---
tipo: ddos
titulo: O que é um ataque de negação de serviço
resumo: >-
  Inundar um serviço com pedidos até deixar de conseguir responder a quem é
  legítimo. Não implica entrar nos sistemas nem aceder a dados: o objetivo é
  apenas que o serviço deixe de estar disponível.
revisto_em: "2026-08-05"
pontos_chave:
  - >-
    Não implica entrada nos sistemas. Ninguém acede a dados nem copia ficheiros — o serviço fica apenas incapaz de atender quem o procura.
  - >-
    É difícil de travar porque cada pedido malicioso é indistinguível de um legítimo. O problema não está em nenhum deles, está no volume.
  - >-
    É muito mais comum do que as notícias sugerem: a medição à escala da Internet mostra dezenas de milhares de ataques por dia a nível global.
referencias:
  - autores: "Mirkovic, J., Reiher, P."
    ano: 2004
    titulo: "A taxonomy of DDoS attack and DDoS defense mechanisms"
    publicacao: "ACM SIGCOMM Computer Communication Review, 34(2)"
    doi: "10.1145/997150.997156"
    nota: >-
      A taxonomia clássica da área, com mais de mil e trezentas citações. Continua
      a ser a referência para classificar este tipo de ataque.
  - autores: "Zargar, S. T., Joshi, J., Tipper, D."
    ano: 2013
    titulo: "A Survey of Defense Mechanisms Against Distributed Denial of Service (DDoS) Flooding Attacks"
    publicacao: "IEEE Communications Surveys & Tutorials, 15(4)"
    doi: "10.1109/SURV.2013.031413.00127"
    nota: >-
      Revisão das defesas conhecidas e das suas limitações.
  - autores: "Jonker, M., King, A., Krupp, J., Rossow, C., Sperotto, A., Dainotti, A."
    ano: 2017
    titulo: "Millions of targets under attack: a macroscopic characterization of the DoS ecosystem"
    publicacao: "Proceedings of the 2017 Internet Measurement Conference (IMC)"
    doi: "10.1145/3131365.3131383"
    nota: >-
      Medição à escala da Internet ao longo de dois anos. Mostra que a negação de
      serviço é um fenómeno contínuo e de massa, e não uma sucessão de acontecimentos
      excecionais — cerca de um terço de todos os domínios ativos foi alvo no período
      estudado.
---

## O que é

Um ataque de negação de serviço consiste em dirigir a um sistema mais pedidos do
que ele consegue processar, até que deixe de responder. Quando os pedidos vêm de
muitas origens ao mesmo tempo — tipicamente equipamentos comprometidos espalhados
pelo mundo — chama-se **distribuído**, ou DDoS.

## O que este ataque não é

É a distinção mais importante e a mais frequentemente confundida na cobertura
noticiosa: **um ataque de negação de serviço não implica entrada nos sistemas**.
Ninguém acede a dados, ninguém copia ficheiros, nada é encriptado. O serviço fica
apenas incapaz de atender quem o procura.

Foi por isso que, no [ataque ao Millennium BCP](/incidentes/2022-millennium-bcp/),
o banco pôde garantir simultaneamente que os clientes tiveram dificuldades de
acesso e que não houve acesso a dados de clientes. As duas afirmações são
compatíveis, e neste registo os incidentes deste tipo têm por isso o campo de
dados pessoais marcado como não afetados.

## Como se distingue de indisponibilidade

A taxonomia deste registo separa `ddos` de `indisponibilidade` por uma razão
prática: o primeiro é uma **causa técnica concreta**, o segundo é um **efeito**.
Muitos comunicados portugueses descrevem serviços em baixo sem esclarecer porquê,
e nesses casos registamos o efeito, não uma causa que ninguém confirmou.

Quando a causa é conhecida, aparece: nos casos do
[Sporting e do FC Porto](/incidentes/2022-sporting-fc-porto/), uma fonte do clube
descreveu explicitamente milhões de pedidos de acesso a entupir o sítio.

## Porque é difícil de defender

A literatura é clara sobre o assimétrico deste problema: os pedidos maliciosos são,
individualmente, indistinguíveis dos legítimos. Não há nada de errado com cada um
deles — o problema é o volume. Distinguir um cliente que quer consultar o saldo de
um pedido automatizado dirigido a esgotar o servidor é, no limite, impossível de
fazer sem errar em algum dos lados.

Daí que a mitigação passe sobretudo por absorver o volume, filtrar por padrões e
recorrer a infraestrutura distribuída, e não por eliminar a possibilidade do
ataque.

## Duração e reincidência

Estes ataques tendem a ser curtos e a repetir-se. O sítio do FC Porto esteve em
baixo menos de uma hora. A [agência Lusa](/incidentes/2022-lusa/) foi atingida duas
vezes em treze dias, o que levou este registo a tratá-las como um só incidente com
dois episódios, e não como dois incidentes distintos.

## É muito mais comum do que as notícias sugerem

A medição à escala da Internet mostra um fenómeno contínuo e de massa: uma fração
muito substancial de todos os domínios ativos é alvo em algum momento, com dezenas
de milhares de ataques por dia a nível global.

Isso ajuda a ler o registo com a proporção certa. Os três casos portugueses aqui
documentados não são os três ataques de negação de serviço que houve em Portugal —
são os três que alguém noticiou, porque atingiram alvos com visibilidade. A
diferença entre ocorrência e cobertura é, neste tipo, maior do que em qualquer
outro.
