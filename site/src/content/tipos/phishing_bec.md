---
tipo: phishing_bec
titulo: O que é phishing e fraude no correio empresarial
resumo: >-
  Enganar uma pessoa para que entregue credenciais ou autorize um pagamento. Não
  explora falhas técnicas: explora a normalidade de uma mensagem que parece vir de
  quem devia.
revisto_em: "2026-08-05"
pontos_chave:
  - >-
    Não é distração de quem cai. Os melhores sítios fraudulentos enganaram a maioria dos participantes em estudos controlados, incluindo pessoas com formação técnica.
  - >-
    A burla ao gestor não tem artefacto malicioso nenhum: nem anexo, nem ligação, nem código. É uma mensagem de texto simples a pedir uma transferência que a empresa faz todos os dias.
  - >-
    Por isso as defesas que funcionam são de processo — dupla aprovação, confirmação por outro canal — e não de tecnologia.
referencias:
  - autores: "Lallie, H. S., Shepherd, L. A., Nurse, J. R. C., Erola, A., Epiphaniou, G., Maple, C., Bellekens, X."
    ano: 2021
    titulo: "Cyber security in the age of COVID-19: A timeline and analysis of cyber-crime and cyber-attacks during the pandemic"
    publicacao: "Computers & Security, 105"
    doi: "10.1016/j.cose.2021.102248"
    nota: >-
      Documenta a explosão de campanhas de phishing durante a pandemia e a
      correlação entre acontecimentos noticiosos e temas usados como isco.
  - autores: "ENISA"
    ano: 2025
    titulo: "ENISA Threat Landscape 2025"
    publicacao: "Agência da União Europeia para a Cibersegurança"
    url: "https://www.enisa.europa.eu/publications/enisa-threat-landscape-2025"
    nota: >-
      Mantém o phishing entre os vetores dominantes de acesso inicial na União
      Europeia.
  - autores: "Dhamija, R., Tygar, J., Hearst, M."
    ano: 2006
    titulo: "Why phishing works"
    publicacao: "Proceedings of the SIGCHI Conference on Human Factors in Computing Systems (CHI)"
    doi: "10.1145/1124772.1124861"
    nota: >-
      O estudo fundador. Demonstrou experimentalmente que os melhores sítios
      fraudulentos enganavam a maioria dos participantes, e que os indicadores de
      segurança dos navegadores passavam despercebidos.
  - autores: "Almutairi, A., Kang, B., Al Hashimy, N."
    ano: 2025
    titulo: "Business email compromise: A systematic review of understanding, detection, and challenges"
    publicacao: "Computers & Security, 155"
    doi: "10.1016/j.cose.2025.104630"
    nota: >-
      Revisão sistemática dedicada à burla ao gestor. Confirma que o traço
      distintivo é a ausência de artefactos técnicos: não há anexo nem ligação
      maliciosa a detetar.
  - autores: "Jakobsson, M."
    ano: 2016
    titulo: "Case Study: Business Email Compromise"
    publicacao: "Understanding Social Engineering Based Scams, Springer"
    doi: "10.1007/978-1-4939-6457-4_11"
    nota: >-
      Estudo de caso da mecânica da burla ao gestor, incluindo o reconhecimento
      prévio da estrutura hierárquica da organização.
---

## O que é

Phishing é o envio de mensagens que se fazem passar por legítimas para levar
alguém a entregar credenciais, abrir um anexo malicioso ou clicar numa ligação. A
variante dirigida ao contexto empresarial — conhecida por **comprometimento de
correio empresarial** — vai mais longe: assume a identidade de um responsável para
autorizar pagamentos ou desviar transferências.

## Porque funciona

Não explora uma falha de software. Explora o facto de as organizações funcionarem
à base de mensagens que pedem coisas, e de a maioria dessas mensagens ser
legítima. Um pedido de pagamento urgente vindo do endereço de um administrador é,
na maior parte dos dias, exatamente aquilo que parece.

O estudo de Lallie e colegas mostra como os temas acompanham o noticiário: durante
a pandemia, as campanhas passaram a usar como isco exatamente aquilo que as pessoas
esperavam receber por correio eletrónico nesse momento.

## Como aparece neste registo

Está subrepresentado — e isso é informação, não lacuna do arquivo.

O único caso classificado com este tipo é o do
[Sport Lisboa e Benfica](/incidentes/2017-sl-benfica/), em que o responsável pela
tecnologia do clube confirmou em tribunal a existência de várias campanhas de
phishing, a par do acesso a ficheiros internos.

A razão da subrepresentação é estrutural: o phishing é quase sempre o **meio** e
não o fim. Aparece na fase inicial de intrusões que depois se tornam ransomware ou
exfiltração, e é essa fase final que dá título à notícia. Um comunicado raramente
diz "o acesso inicial foi por correio eletrónico", ainda que tenha sido.

## O que isto significa para as contagens

Se contar os incidentes deste registo por tipo, o phishing parecerá um problema
menor em Portugal. Não é: é um problema pouco divulgado. A classificação reflete o
que as fontes afirmam, e as fontes falam do efeito, não do vetor.

É uma das razões pelas quais a [metodologia](/metodologia/#vies) insiste que estas
contagens são de incidentes noticiados, e não de incidentes ocorridos.

## Não é distração, é desenho

O estudo experimental fundador nesta área mostrou que os melhores sítios
fraudulentos enganavam a larga maioria dos participantes — incluindo pessoas com
formação técnica — e que os indicadores de segurança do navegador simplesmente não
eram vistos.

Vale a pena reter isto ao ler qualquer caso deste registo que tenha começado por uma
mensagem: a explicação de que "alguém foi distraído" é confortável e está errada. O
engano é desenhado por quem estuda como as pessoas decidem, e funciona contra
pessoas atentas.

## Porque a burla ao gestor não é detetável por meios técnicos

A revisão sistemática da literatura sobre burla ao gestor confirma o traço que a
torna singular: **não há artefacto malicioso**. Não há anexo, não há ligação, não há
código. Há uma mensagem de texto simples, muitas vezes enviada de uma conta
legítima previamente comprometida, a pedir uma transferência que a organização faz
todos os dias.

Nenhum filtro de correio pode marcar isso como perigoso sem marcar também o
trabalho normal. Daí que as defesas eficazes sejam de processo — dupla aprovação,
confirmação por canal distinto — e não de tecnologia, como se explica também em
[fraude](/tipos/fraude/).
