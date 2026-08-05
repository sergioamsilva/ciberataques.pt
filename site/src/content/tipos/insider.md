---
tipo: insider
titulo: O que é uma ameaça interna
resumo: >-
  Quando quem causa o dano tem acesso legítimo: trabalhador, ex-trabalhador,
  prestador de serviços. É o tipo de incidente mais difícil de detetar, porque
  nada do que acontece parece, à partida, indevido.
revisto_em: "2026-08-05"
referencias:
  - autores: "Homoliak, I., Toffalini, F., Guarnizo, J., Elovici, Y., Ochoa, M."
    ano: 2019
    titulo: "Insight Into Insiders and IT: A Survey of Insider Threat Taxonomies, Analysis, Modeling, and Countermeasures"
    publicacao: "ACM Computing Surveys, 52(2)"
    doi: "10.1145/3303771"
    nota: >-
      A revisão de referência sobre o tema. Propõe a distinção entre o interno
      malicioso e o interno negligente, que é a que mais consequências tem para
      quem responde a um incidente.
  - autores: "Salem, M., Hershkop, S., Stolfo, S."
    ano: 2008
    titulo: "A Survey of Insider Attack Detection Research"
    publicacao: "Advances in Information Security, vol. 39"
    doi: "10.1007/978-0-387-77322-3_5"
    nota: >-
      Explica porque as defesas de perímetro são estruturalmente cegas a este tipo:
      são construídas para distinguir dentro de fora, e aqui o atacante já está
      dentro.
  - autores: "Maimon, D., Louderback, E."
    ano: 2019
    titulo: "Cyber-Dependent Crimes: An Interdisciplinary Review"
    publicacao: "Annual Review of Criminology, 2"
    doi: "10.1146/annurev-criminol-032317-092057"
    nota: >-
      Situa o abuso de acesso legítimo no conjunto mais vasto dos crimes
      dependentes de meios informáticos, e revê o que se sabe sobre motivação.
---

## O que é

Uma ameaça interna existe quando o dano é causado por alguém que tinha acesso
legítimo aos sistemas: um trabalhador, um ex-trabalhador cujo acesso não foi
revogado, um prestador de serviços, um estagiário.

A característica que define este tipo não é o vínculo laboral. É o facto de **as
credenciais usadas serem as próprias**, e portanto de nenhum sistema de deteção
poder assinalar uma entrada indevida — porque não houve nenhuma.

## Malicioso e negligente não são a mesma coisa

A literatura separa dois casos que a linguagem comum junta.

O **interno malicioso** age com intenção: copia a base de dados de clientes antes de
sair para a concorrência, altera registos, vende acessos. O **interno negligente**
não tem intenção nenhuma: perde um portátil sem cifra, reencaminha um ficheiro para
o endereço pessoal para trabalhar em casa, cai numa mensagem de
[phishing](/tipos/phishing_bec/) e entrega as credenciais.

A distinção importa por uma razão prática: o segundo é muito mais frequente e as
medidas que o reduzem — formação, cifra, princípio do menor privilégio — não são as
mesmas que travam o primeiro.

## Porque é o mais difícil de detetar

As defesas informáticas são, na sua esmagadora maioria, construídas para distinguir
o que vem de fora do que já está dentro. Um sistema que vigia a fronteira nada tem a
dizer sobre quem já a atravessou legitimamente.

Descarregar mil ficheiros é normal para quem trabalha com eles todos os dias. A
única forma de o assinalar seria conhecer o padrão habitual de cada pessoa e
reparar no desvio — o que levanta um problema próprio, que é o da vigilância de
trabalhadores, com limites legais claros em Portugal e na União Europeia.

## O interno negligente e o acesso indevido

Há um caso intermédio que este registo encontrou na prática: o
[acesso indevido a dados de utentes do SNS com credenciais de médico](/incidentes/2026-sns24-dados-de-utentes/).
Aí não houve invasão de sistema nenhum — houve credenciais legítimas usadas para
consultar o que não devia ser consultado.

Esse caso está classificado neste registo como
[intrusão](/tipos/intrusao/) e não como ameaça interna, por uma razão de rigor: não
foi apurado publicamente se quem usou as credenciais era o seu titular. A
classificação segue o que as fontes sustentam, não o que é plausível.

## Como este registo o trata

Não há, à data, nenhum incidente classificado como ameaça interna em Portugal. A
razão é quase certamente de cobertura e não de ocorrência: estes casos resolvem-se
em processo disciplinar ou em tribunal de trabalho, sem comunicado nem notícia, e
uma organização tem muito menos incentivo a divulgar que o problema veio de dentro.

Quando existe decisão judicial pública, este registo pode nomear a pessoa condenada
— é uma das três exceções da [política editorial](/metodologia/). Fora disso, nunca.
