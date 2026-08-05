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
  - autores: "Kharraz, A., Robertson, W., Balzarotti, D., Bilge, L., Kirda, E."
    ano: 2015
    titulo: "Cutting the Gordian Knot: A Look Under the Hood of Ransomware Attacks"
    publicacao: "Detection of Intrusions and Malware, and Vulnerability Assessment (DIMVA), Lecture Notes in Computer Science 9148"
    doi: "10.1007/978-3-319-20550-2_1"
    nota: >-
      Análise técnica de mil e trezentas amostras ao longo de cinco anos. Mostra que
      uma minoria das famílias faz destruição irreversível — o que é a base do
      argumento de que pagar não é a única via de recuperação.
  - autores: "Huang, D., Aliapoulios, M., Li, V., Invernizzi, L., Bursztein, E., et al."
    ano: 2018
    titulo: "Tracking Ransomware End-to-end"
    publicacao: "2018 IEEE Symposium on Security and Privacy (SP)"
    doi: "10.1109/sp.2018.00047"
    nota: >-
      Segue os pagamentos na cadeia de blocos e estima o volume real de resgates
      pagos. É a fonte que permite falar de dinheiro sem depender de números
      avançados pelos próprios grupos.
  - autores: "Dameff, C., Tully, J., Chan, T., Castillo, E., Savage, S., et al."
    ano: 2023
    titulo: "Ransomware Attack Associated With Disruptions at Adjacent Emergency Departments in the US"
    publicacao: "JAMA Network Open, 6(5)"
    doi: "10.1001/jamanetworkopen.2023.12270"
    nota: >-
      Demonstra que o dano de um ataque a um hospital não fica no hospital atacado:
      as urgências vizinhas registaram mais chegadas, mais tempo de espera e mais
      casos de acidente vascular cerebral. É a evidência empírica do efeito em
      cascata.
  - autores: "Neprash, H., McGlave, C., Cross, D., Virnig, B., Puskarich, M., et al."
    ano: 2022
    titulo: "Trends in Ransomware Attacks on US Hospitals, Clinics, and Other Health Care Delivery Organizations"
    publicacao: "JAMA Health Forum, 3(12)"
    doi: "10.1001/jamahealthforum.2022.4873"
    nota: >-
      Quantifica a subida dos ataques a prestadores de cuidados de saúde e a
      proporção que envolve exposição de dados de doentes.
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

## O que a literatura diz sobre pagar

A questão que qualquer leitor faz é se as vítimas pagam. O trabalho que seguiu
pagamentos na cadeia de blocos permite responder com dados em vez de impressões: uma
minoria paga, mas os montantes concentram-se num pequeno número de casos de valor
elevado.

Neste registo o campo de resgate é preenchido com o que a entidade declarou ou com o
que se deduz de facto observável — a publicação dos ficheiros na data anunciada
indica que não houve pagamento, como aconteceu na
[Trust in News](/incidentes/2022-trust-in-news/) e nos
[SMTUC](/incidentes/2022-smtuc/). Nunca registamos como facto um valor avançado pelo
grupo atacante.

## Quando a vítima é um hospital, o dano não fica no hospital

Há evidência empírica de que um ataque a uma unidade de saúde se propaga às
unidades vizinhas: mais chegadas às urgências em redor, mais tempo de espera, mais
casos de acidente vascular cerebral confirmados. O hospital atacado deixa de receber
e os doentes vão para o lado.

É a razão pela qual este arquivo regista **entidades afetadas em cascata** como
campo próprio, e não apenas a entidade atacada. Nos casos do
[Hospital Garcia de Orta](/incidentes/2022-hospital-garcia-de-orta/) e do
[SESARAM](/incidentes/2023-sesaram/), o efeito sobre a rede é parte do incidente, não
contexto dele.
