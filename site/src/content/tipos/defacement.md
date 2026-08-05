---
tipo: defacement
titulo: O que é a desfiguração de um sítio
resumo: >-
  A substituição do conteúdo visível de uma página por outro, escolhido por quem
  entrou. É o ataque mais visível de todos e, quase sempre, o menos grave — o que
  não significa que não haja um problema sério por trás dele.
revisto_em: "2026-08-05"
referencias:
  - autores: "Maggi, F., Balduzzi, M., Flores, R., Gu, L., Ciancaglini, V."
    ano: 2018
    titulo: "Investigating Web Defacement Campaigns at Large"
    publicacao: "Proceedings of the 2018 ACM Asia Conference on Computer and Communications Security (ASIACCS)"
    doi: "10.1145/3196494.3196542"
    nota: >-
      Análise de mais de treze milhões de desfigurações registadas ao longo de uma
      década. Mostra que a atividade é sobretudo campanhas organizadas com motivação
      declarada, e não atos isolados.
  - autores: "Masango, M., Mouton, F., Antony, P., Mangoale, B."
    ano: 2017
    titulo: "Web Defacement and Intrusion Monitoring Tool: WDIMT"
    publicacao: "2017 International Conference on Cyberworlds (CW)"
    doi: "10.1109/cw.2017.55"
    nota: >-
      Descreve o problema da deteção: uma desfiguração só é reparada depois de
      alguém dar por ela, e é frequente que quem dá por ela seja um visitante.
  - autores: "Cho, Y."
    ano: 2019
    titulo: "Intelligent On-Off Web Defacement Attacks and Random Monitoring-Based Detection Algorithms"
    publicacao: "Electronics, 8(11)"
    doi: "10.3390/electronics8111338"
    nota: >-
      Documenta a variante intermitente, em que a página alterada só é mostrada a
      parte dos visitantes ou durante parte do tempo, precisamente para escapar à
      monitorização periódica.
---

## O que é

Desfiguração é a substituição do conteúdo visível de um sítio na Internet por
outro, escolhido por quem conseguiu entrar. A página inicial passa a mostrar uma
mensagem, uma imagem ou uma assinatura de quem o fez.

É o único tipo de ataque desta taxonomia cuja característica definidora é **ser
visto**. Todos os outros procuram passar despercebidos o máximo de tempo possível;
este só cumpre o seu objetivo se alguém olhar.

## Porque quase sempre é menos grave do que parece

A desfiguração atinge tipicamente o servidor que aloja o sítio público, que na
generalidade das organizações está separado dos sistemas onde estão os dados de
clientes, a faturação ou os processos internos. Alterar a página inicial de uma
câmara municipal não é o mesmo que aceder ao seu sistema de gestão documental.

Daí que a resposta correta a uma desfiguração seja quase sempre desproporcionada em
relação ao alarme que causa: repõe-se o conteúdo a partir de uma cópia, corrige-se a
falha que permitiu a entrada, e o serviço volta ao normal em horas.

## Porque, ainda assim, importa

Duas razões.

A primeira é que a desfiguração é **prova de entrada**. Quem conseguiu escrever na
página conseguiu autorização para escrever em alguma coisa, e a pergunta que
interessa nunca é "o que mudaram na página", mas "o que mais poderiam ter feito com
o mesmo acesso". Um sítio desfigurado é o sintoma, não a doença.

A segunda é que a visibilidade é o objetivo. A literatura que analisou campanhas de
grande escala mostra que a maior parte destes atos tem motivação declarada e
pertence a campanhas organizadas — o que aproxima este tipo do
[hacktivismo](/tipos/hacktivismo/), com que frequentemente se sobrepõe.

## A variante que engana a monitorização

Há uma forma de desfiguração que só mostra a página alterada a parte dos
visitantes, ou apenas durante certos períodos. O objetivo é sobreviver à
monitorização automática, que verifica o sítio de tempos a tempos e o encontra
normal.

O efeito prático é que a duração declarada de uma desfiguração é quase sempre um
limite inferior: mede-se desde que alguém reparou, não desde que começou.

## Como este registo o trata

Este tipo não tem, à data, nenhum incidente registado em Portugal. Não é por não
acontecerem — acontecem, sobretudo em sítios de autarquias e de escolas — mas
porque raramente são noticiados e quase nunca dão origem a comunicado, o que os
deixa abaixo do limiar de fontes que este arquivo exige.

É uma lacuna de cobertura conhecida, e está assumida como tal na
[metodologia](/metodologia/): a ausência de casos aqui diz mais sobre o que a
imprensa cobre do que sobre o que se passa.
