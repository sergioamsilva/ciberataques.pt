---
tipo: ransomware
titulo: O que é ransomware
resumo: >-
  Software que bloqueia o acesso aos dados de uma organização e exige pagamento
  para o devolver. Desde 2019 raramente se limita a isso: os dados são primeiro
  copiados, e a ameaça passa a ser publicá-los.
revisto_em: "2026-08-05"
referencias:
  - autores: "Oz, H., Aris, A., Levi, A., Uluagac, A. S."
    ano: 2022
    titulo: "A Survey on Ransomware: Evolution, Taxonomy, and Defense Solutions"
    publicacao: "ACM Computing Surveys, 54(11s)"
    doi: "10.1145/3514229"
    nota: >-
      Revisão sistemática da evolução do ransomware e das defesas conhecidas. É a
      referência mais citada da área.
  - autores: "Meurs, T., Cartwright, E., Cartwright, A., Junger, M., Abhishta, A."
    ano: 2024
    titulo: "Deception in double extortion ransomware attacks: An analysis of profitability and credibility"
    publicacao: "Computers & Security"
    doi: "10.1016/j.cose.2023.103670"
    nota: >-
      Estuda se a ameaça de divulgar dados é credível, e conclui que a dupla
      extorsão aumenta o valor pedido e a disposição para pagar.
  - autores: "ENISA"
    ano: 2022
    titulo: "ENISA Threat Landscape for Ransomware Attacks"
    publicacao: "Agência da União Europeia para a Cibersegurança"
    url: "https://www.enisa.europa.eu/publications/enisa-threat-landscape-for-ransomware-attacks"
    nota: >-
      Relatório oficial europeu. É a fonte da definição adotada neste registo.
---

## O que é

Ransomware é um ataque em que alguém toma o controlo dos sistemas de uma
organização e exige um pagamento para lhe devolver o acesso — ou, cada vez mais,
para **não tornar públicos** os dados que entretanto copiou. A definição adotada
neste registo é a da ENISA, e é deliberadamente ampla: descrevê-lo apenas como
"encriptação de ficheiros" deixou de corresponder à realidade.

## Porque mudou

Até cerca de 2019, o modelo era simples: encriptar e cobrar pela chave. Uma
organização com cópias de segurança intactas podia recusar-se a pagar e recuperar
sozinha. Foi o que aconteceu em [Alcobaça](/incidentes/2024-camara-municipal-de-alcobaca/),
cujo presidente invocou precisamente a existência de cópias.

A resposta dos atacantes foi copiar os dados **antes** de os encriptar. Passou a
haver duas alavancas em vez de uma: a organização pode recuperar os sistemas e
ainda assim ver a informação publicada. É a chamada **dupla extorsão**, e mudou o
cálculo: a investigação de Meurs e colegas mostra que estes ataques resultam em
pedidos maiores e em maior disposição para pagar do que os que apenas encriptam.

Neste registo, o padrão vê-se com clareza. No [Porto de Lisboa](/incidentes/2022-porto-de-lisboa/)
o grupo exigiu cerca de 1,5 milhões de euros para **não publicar**, e publicou
quando o prazo passou. Em [Gondomar](/incidentes/2023-camara-municipal-de-gondomar/)
os dados acabaram leiloados na dark web, com cartões de cidadão e passaportes.

## Porque as cópias de segurança nem sempre chegam

O conselho corrente é ter cópias. É bom conselho, mas incompleto por duas razões
que este registo documenta:

1. **As cópias também são alvo.** Na [Figueira da Foz](/incidentes/2022-camara-municipal-da-figueira-da-foz/),
   o ataque atingiu algumas cópias de segurança, e a reposição prolongou-se por
   semanas em vez de horas.
2. **Cópias não resolvem a exfiltração.** Recuperar os sistemas não desfaz o facto
   de a informação ter saído.

## O que costuma acontecer a seguir

A literatura descreve um ciclo com fases: acesso inicial, reconhecimento, elevação
de privilégios, movimento lateral, exfiltração, encriptação e extorsão. Entre a
entrada e o efeito visível podem passar dias ou semanas — no caso da
[Impresa](/incidentes/2022-impresa/), apurou-se que os atacantes tinham estado
vários dias dentro da rede antes de agir.

Daí que a data em que um ataque se torna público seja quase sempre posterior à
data em que começou, e que os primeiros números divulgados sejam quase sempre
provisórios.

## Como lemos os números

Muito do que se publica sobre um ataque de ransomware vem de quem o executou:
volumes de dados, número de vítimas, valores de resgate. Não são factos
verificados, são afirmações de uma parte interessada em parecer credível — e o
estudo de Meurs e colegas trata precisamente da credibilidade dessas ameaças.

Por isso, neste registo, esses números nunca entram na ficha técnica de um
incidente. Ficam na secção de versões em confronto, com indicação de quem os
afirmou. Ver a [metodologia](/metodologia/#disputas).
