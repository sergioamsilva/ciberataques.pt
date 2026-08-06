---
tipo: exposicao_credenciais
titulo: O que é exposição de credenciais
resumo: >-
  Palavras-passe de utilizadores a circular publicamente, recolhidas nos
  equipamentos dessas pessoas ou em serviços de terceiros. Não implica que a
  organização cujo serviço se acede tenha sido invadida — e a distinção é
  frequentemente perdida.
revisto_em: "2026-08-05"
pontos_chave:
  - >-
    Não implica que a organização tenha sido invadida. As palavras-passe são recolhidas nos computadores das pessoas ou em serviços de terceiros, e só depois usadas.
  - >-
    É a reutilização que transforma uma fuga num sítio em risco noutro: uma proporção elevada de pessoas repete a palavra-passe, e boa parte das restantes usa variações adivinháveis.
  - >-
    As credenciais roubadas por software de recolha valem mais do que as de fugas antigas, porque trazem o contexto — máquina, localização, sessões abertas — que contorna as defesas adicionais.
referencias:
  - autores: "Madarie, R., Ruiter, S., Steenbeek, W., Kleemans, E."
    ano: 2019
    titulo: "Stolen account credentials: an empirical comparison of online dissemination on different platforms"
    publicacao: "Journal of Crime and Justice, 43(2)"
    doi: "10.1080/0735648X.2019.1692418"
    nota: >-
      Estudo empírico sobre como as credenciais roubadas circulam nas diferentes
      plataformas onde são disseminadas.
  - autores: "ENISA"
    ano: 2025
    titulo: "ENISA Threat Landscape 2025"
    publicacao: "Agência da União Europeia para a Cibersegurança"
    url: "https://www.enisa.europa.eu/publications/enisa-threat-landscape-2025"
    nota: >-
      Documenta o crescimento do software de recolha de credenciais como vetor
      dominante de acesso inicial.
  - autores: "Thomas, K., Li, F., Zand, A., Barrett, J., Ranieri, J., et al."
    ano: 2017
    titulo: "Data Breaches, Phishing, or Malware? Understanding the Risks of Stolen Credentials"
    publicacao: "Proceedings of the 2017 ACM SIGSAC Conference on Computer and Communications Security (CCS)"
    doi: "10.1145/3133956.3134067"
    nota: >-
      Mede, durante um ano, a origem das credenciais que circulam: fugas de dados,
      phishing e software de recolha. Conclui que o phishing e os recolhedores são os
      que mais risco real representam para a conta, por trazerem também o contexto que
      permite passar a autenticação.
  - autores: "Das, A., Bonneau, J., Caesar, M., Borisov, N., Wang, X."
    ano: 2014
    titulo: "The Tangled Web of Password Reuse"
    publicacao: "Proceedings 2014 Network and Distributed System Security Symposium (NDSS)"
    doi: "10.14722/ndss.2014.23357"
    nota: >-
      Demonstra empiricamente a reutilização de palavras-passe entre serviços e a
      facilidade com que pequenas variações são adivinhadas. É o mecanismo que
      transforma a fuga num serviço num problema em todos os outros.
---

## O que é

Exposição de credenciais é a circulação pública de pares de utilizador e
palavra-passe. A origem habitual é **software de recolha de credenciais**, os
chamados *infostealers*: código malicioso instalado no computador de uma pessoa,
que recolhe silenciosamente tudo o que esteja guardado no navegador.

## A distinção que se perde

Este é o tipo de incidente mais mal contado da cobertura noticiosa, e a razão pela
qual existe uma categoria própria nesta taxonomia.

Quando circulam credenciais do Portal das Finanças, o título natural é "fuga de
dados nas Finanças". Mas no [caso de outubro de 2024](/incidentes/2024-portal-das-financas/)
**não houve intrusão nos sistemas da Autoridade Tributária**. As credenciais foram
recolhidas nos equipamentos dos próprios contribuintes, ou exfiltradas de serviços
de terceiros onde tinham reutilizado a mesma palavra-passe.

O Centro Nacional de Cibersegurança teve de esclarecer publicamente duas coisas: que
não havia intrusão, e que o caso não tinha relação com o
[ciberataque à AMA](/incidentes/2024-ama/), ocorrido nos mesmos dias.

A distinção não é técnica: muda quem tem o problema e quem o pode resolver.

## Porque a organização responde na mesma

Ainda que não tenha sido invadida, a organização cujo serviço se acede tem de agir
— e agiu. A Autoridade Tributária revogou as senhas comprometidas, obrigando os
visados a definir novas, e viria a reforçar as regras de palavra-passe e a
introduzir autenticação com código por mensagem escrita.

Isto é o padrão: quem sofre a exposição não é quem pode remediá-la sozinho.

## Quando a credencial é de dentro

Há um caso mais grave: quando a credencial comprometida pertence a alguém com
acesso privilegiado. No [caso do SNS 24](/incidentes/2026-sns24-dados-de-utentes/),
as credenciais de um médico foram usadas para aceder a registos de mais de cem mil
utentes, adultos e crianças.

Este registo não identifica o profissional. As autoridades tratam-no como vítima
de roubo de credenciais e não como autor, e a
[política editorial](/metodologia/#limites) não nomeia pessoas singulares.

## O que isto significa para quem lê

Se as suas credenciais aparecem numa lista, o problema não está necessariamente no
serviço a que elas dão acesso. Está, com maior probabilidade, num equipamento
comprometido ou na reutilização da mesma palavra-passe em vários sítios.

## Porque a fuga num sítio é um problema noutro

A reutilização de palavras-passe está medida: uma proporção elevada de pessoas usa a
mesma em vários serviços, e boa parte das restantes usa variações pequenas o
suficiente para serem adivinhadas automaticamente a partir da primeira.

É este mecanismo que faz com que uma exposição de credenciais recolhidas nos
computadores das pessoas se torne um risco para o serviço a que essas credenciais
dão acesso, **sem que esse serviço tenha tido qualquer falha**. Foi exatamente o que
aconteceu no [Portal das Finanças](/incidentes/2024-portal-das-financas/), e é a
razão pela qual este registo insiste na distinção.

## Nem todas as credenciais roubadas valem o mesmo

A medição da origem das credenciais em circulação mostra que as que vêm de
phishing e de software de recolha são muito mais perigosas do que as que vêm de
fugas antigas: trazem consigo o contexto — a máquina, a localização, as sessões
abertas — que permite contornar as defesas adicionais.
