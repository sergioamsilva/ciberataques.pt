---
tipo: exfiltracao_dados
titulo: O que é exfiltração de dados
resumo: >-
  Copiar informação para fora de uma organização sem autorização. Ao contrário da
  encriptação, não se vê: os dados continuam lá, e a organização pode demorar
  semanas a saber o que saiu — ou nunca chegar a sabê-lo.
revisto_em: "2026-08-05"
referencias:
  - autores: "Nikkhah, H. R., Grover, V."
    ano: 2022
    titulo: "An Empirical Investigation of Company Response to Data Breaches"
    publicacao: "MIS Quarterly, 46(4)"
    doi: "10.25300/MISQ/2022/16609"
    nota: >-
      Analisa como 204 empresas cotadas responderam publicamente a fugas de dados,
      e classifica as estratégias adotadas, incluindo a de não fazer nada.
  - autores: "Liu, C., Babar, M. A."
    ano: 2024
    titulo: "Corporate cybersecurity risk and data breaches: A systematic review of empirical research"
    publicacao: "Australian Journal of Management"
    doi: "10.1177/03128962241293658"
    nota: >-
      Revisão sistemática de 203 estudos empíricos sobre determinantes e
      consequências do risco de cibersegurança nas organizações.
  - autores: "Romanosky, S."
    ano: 2016
    titulo: "Examining the costs and causes of cyber incidents"
    publicacao: "Journal of Cybersecurity, 2(2)"
    doi: "10.1093/cybsec/tyw001"
    nota: >-
      Analisa doze mil incidentes e conclui que o custo mediano é muito inferior ao
      que a cobertura mediática sugere, e representa uma fração pequena da receita
      anual das empresas afetadas.
  - autores: "Romanosky, S., Telang, R., Acquisti, A."
    ano: 2011
    titulo: "Do data breach disclosure laws reduce identity theft?"
    publicacao: "Journal of Policy Analysis and Management, 30(2)"
    doi: "10.1002/pam.20567"
    nota: >-
      Avalia o efeito das leis de notificação obrigatória. O efeito existe mas é
      modesto, o que é relevante para julgar o valor de arquivos como este: a
      notificação sozinha muda pouco se ninguém agregar o que é notificado.
---

## O que é

Exfiltração é a cópia não autorizada de informação para fora de uma organização.
Distingue-se da encriptação por uma característica que muda tudo: **não deixa
marca visível**. Os dados continuam onde estavam e a funcionar. O que mudou foi
existirem agora noutro sítio.

## Porque a extensão demora a apurar-se

É a consequência prática mais importante, e este registo documenta-a repetidamente.
Uma organização que perde o acesso aos sistemas percebe-o em minutos. Uma
organização de que copiaram dados pode levar semanas a estabelecer o que saiu, ou
não chegar a estabelecê-lo.

O caso da [Segurança Social](/incidentes/2022-seguranca-social/) mostra o percurso
típico: a posição inicial, a 21 de novembro de 2022, foi a de que não fora apurado
acesso indevido a dados; a 11 de janeiro seguinte confirmava-se a exposição de
nomes de catorze mil trabalhadores. Quase dois meses entre uma leitura e a outra.

Na [Universidade de Aveiro](/incidentes/2026-universidade-de-aveiro/), o reitor
indicou ter havido cópia de informação e não perda, e que a extensão era
desconhecida. Registamos essa incerteza em vez de a resolver.

## O problema dos números

Quando há exfiltração, os primeiros números públicos vêm quase sempre de quem
atacou — e servem um propósito: tornar a ameaça credível para que seja paga.

No caso da [TAP](/incidentes/2022-tap/), os valores avançados pelo Ragnar Locker
foram 400 mil clientes a 31 de agosto, cerca de 115 mil nos ficheiros efetivamente
publicados a 13 de setembro, e 1,5 milhões anunciados a 20 de setembro. Três
números diferentes em três semanas, todos da mesma fonte interessada.

Por isso, neste registo, esses valores nunca entram na ficha técnica: ficam nas
[versões em confronto](/metodologia/#disputas), com indicação de quem os afirmou e
quando.

## O que sai, importa

Nem todos os dados têm o mesmo peso. A distinção entre dados administrativos e
dados sensíveis é material para quem é afetado, e nem sempre está esclarecida.

O registo tem casos nos dois extremos. Em [Gondomar](/incidentes/2023-camara-municipal-de-gondomar/)
foram divulgados cartões de cidadão e passaportes — documentos de identificação,
que não se substituem como se substitui uma palavra-passe. Na
[Universidade do Algarve](/incidentes/2024-universidade-do-algarve/) saíram nomes,
contactos e números de identificação bancária. No [caso do SNS 24](/incidentes/2026-sns24-dados-de-utentes/),
a própria natureza do que foi acedido — clínico ou administrativo — é objeto de
divergência pública, e está registada como tal.

## Como as organizações respondem

O estudo de Nikkhah e Grover classifica as respostas públicas a fugas de dados em
categorias que se reconhecem na cobertura portuguesa: ação corretiva, pedido de
desculpa, compensação, e a ausência de resposta. Este registo documenta o espectro
todo, incluindo comunicados que reconhecem o incidente sem esclarecer natureza,
extensão nem autoridades notificadas — como o de
[Santa Comba Dão](/incidentes/2024-camara-municipal-de-santa-comba-dao/).

## Quanto custa, na verdade

A cobertura noticiosa de uma fuga de dados tende a números grandes. A literatura que
analisou dezenas de milhares de incidentes encontra um custo mediano bastante
modesto e muito assimétrico: a distribuição tem uma cauda longa, e é essa cauda que
dá as manchetes.

Este registo regista custo apenas quando **declarado pela entidade** ou por
autoridade. É por isso que o campo está vazio na esmagadora maioria das fichas — não
por não haver custo, mas por não haver quem o declare.

## Porque um arquivo como este faz diferença

O estudo do efeito das leis de notificação obrigatória encontra um efeito real mas
pequeno. A leitura útil é que notificar não basta: se cada notificação vive isolada
num comunicado que desaparece do sítio ao fim de um ano, a informação existe e não
serve a ninguém.

O caso de [Barrancos](/incidentes/2023-camara-municipal-de-barrancos/) é a
ilustração disto neste arquivo: os dois comunicados originais devolvem hoje 404 e
não existe cópia no Internet Archive.
