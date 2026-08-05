# Política editorial

Este documento manda no código. Quando uma regra daqui colidir com uma decisão técnica,
muda a decisão técnica.

O ciberataques.pt regista ciberataques a entidades portuguesas. Nomeia organizações que
foram atacadas, o que tem consequências reais para essas organizações. A única coisa que
justifica fazê-lo é o rigor com que o fazemos. Estas regras existem para que o rigor não
dependa da disposição de quem cura num dado dia.

## 1. O que somos e o que não somos

Somos uma **base de dados documental e um arquivo**. Não somos um órgão de comunicação
social: não fazemos reportagem própria, não temos periodicidade informativa, não publicamos
notícias. Registamos o que outros apuraram, com a fonte à vista.

Daí decorrem duas consequências práticas:

- O `schema.org` das fichas declara `Article`, nunca `NewsArticle`.
- Não escrevemos texto que acrescente factos aos das fontes. O `resumo` de um incidente é
  uma síntese do que as fontes dizem, não uma interpretação nossa.

## 2. Nada é afirmado sem fonte

Todo o facto publicado tem de apontar para uma fonte concreta. Não há exceções, e a regra
é imposta por código: `ingestao/verificar.py` recusa construir um incidente cujos campos de
impacto, notificações, cronologia ou consequências regulatórias citem uma fonte inexistente.
Um incidente sem `fontes` não é publicável.

Quando uma informação circula sem fonte identificável, não entra. É preferível um registo
incompleto a um registo que não se consegue defender.

## 3. A escala de confiança

Cada incidente exibe, no topo da ficha e em texto legível, o grau de confirmação. Nunca
apenas uma cor: uma cor não se lê em voz alta nem sobrevive a um leitor de ecrã.

1. **Confirmado pela entidade** — a organização reconheceu publicamente.
2. **Confirmado por autoridade** — CNCS, CNPD, ANACOM, CMVM, Polícia Judiciária ou tribunal.
3. **Reportado por vários órgãos** — pelo menos dois órgãos independentes.
4. **Noticiado por uma única fonte** — sem corroboração.
5. **Alegado pelo atacante** — vem de um site de extorsão, sem confirmação.
6. **Desmentido** — a entidade negou.

Três regras sobre este campo:

- **O modelo de linguagem nunca o escreve.** É derivado em Python a partir dos tipos de
  fonte presentes. O texto que analisamos é, no caso dos sites de extorsão, literalmente
  escrito por adversários; se um deles pudesse influenciar a classificação através do que
  escreve, a escala não valeria nada.
- **Um curador pode baixá-lo, nunca subi-lo** acima do que as fontes sustentam.
- **Nada sobe a "confirmado" por repetição.** Cinco órgãos a citar o mesmo comunicado do
  atacante continuam a ser uma alegação do atacante.

## 4. Pessoas singulares

**Não nomeamos pessoas singulares.** Três exceções, e só três:

- Titulares de cargo a falar publicamente em nome da entidade, no exercício dessa função.
- Pessoas condenadas por decisão judicial pública, e apenas quanto ao que a decisão declara.
- Pessoas cuja identidade é o próprio objeto público do caso e já foi tornada pública por
  autoridade judicial.

Nunca nomeamos alegados atacantes não condenados. Nunca nomeamos vítimas individuais.
Nunca nomeamos trabalhadores da entidade atacada. A presunção de inocência não é uma
formalidade, e uma base de dados pesquisável e permanente amplifica um erro de identificação
muito para lá do que uma notícia isolada amplificaria.

## 5. Dados comprometidos

**Nunca republicamos dados vazados.** Nem o conteúdo, nem amostras, nem capturas de ecrã,
nem contagens que só se possam obter lendo-os. Não ligamos a endereços `.onion` nem a
espelhos de fugas. Quando citamos um site de extorsão, a ligação aponta para a página do
tracker público, nunca para o site do grupo.

Registamos **categorias** de dados (identificação, contacto, financeiros, saúde) e o número
de titulares **declarado pela entidade ou por autoridade**. Números avançados pelo atacante
não entram no campo de impacto: vão para `disputas[]`, identificados como tal.

## 6. Texto de terceiros

Nunca reproduzimos artigos. De cada fonte guardamos título, publicador, data, ligação e, no
máximo, um excerto de **200 caracteres** com atribuição visível.

O limite decorre do direito de citação (CDADC art. 75.º/2 g) e art. 76.º) e do direito conexo
dos editores de imprensa (DL 47/2023), que exclui expressamente "excertos muito curtos" e as
hiperligações. Se um editor reclamar, removemos o excerto e mantemos a ligação: o registo
perde cor, não perde utilidade.

A cópia arquivada de cada fonte é **privada**, vive fora do repositório e nunca é servida
pelo site. Existe para provarmos internamente o que a fonte dizia numa data, e para detetarmos
edições silenciosas. O arquivo público que oferecemos ao leitor é a Wayback Machine.

O feed do Google News proíbe contratualmente o uso não pessoal. Usamo-lo, quando muito, como
sinal privado de descoberta. Nunca é citado como fonte, nunca aparece no registo, nunca sai
nas exportações.

## 7. Uma notícia é uma prova, não um facto

O incidente é a unidade canónica. A notícia é uma fonte dentro de um incidente e não tem
página própria neste site. Cinco notícias sobre o mesmo ataque produzem um incidente com
cinco fontes.

Não é uma escolha de arrumação. É o que nos impede de transformar cobertura repetida em
aparente corroboração, e o que faz de nós mais úteis do que uma pesquisa num motor de busca.

## 8. Correções

Erramos. O que distingue um arquivo de um blogue é corrigir em público.

- Cada correção fica registada em `correcoes[]` na própria ficha, com data e descrição.
- A página `/correcoes/` lista todas as correções do site.
- **Não apagamos incidentes publicados.** Um incidente que se revele infundado passa a
  `desmentido`, com a explicação, e continua acessível na mesma URL. Apagar deixaria as
  citações a apontar para o vazio e seria pior do que ter errado.
- Os identificadores nunca mudam. Se um tiver de mudar, o antigo passa a redirecionar.

## 9. Direito de resposta

Qualquer entidade referida pode pedir correção ou publicação da sua versão, através da página
`/direito-de-resposta/`. Comprometemo-nos a:

- Responder em **72 horas**.
- Publicar o desmentido ou a versão da entidade **na própria ficha**, não numa página à parte.
- Corrigir de imediato o que se demonstre errado, com registo da correção.

Não retiramos um incidente confirmado por pedido da entidade. Corrigimos o que estiver errado
e publicamos o que a entidade tiver a dizer.

## 10. Viés de cobertura

Este registo herda o viés da imprensa: a Vodafone é notícia, a empresa de vinte pessoas em
Guimarães não é. Um leitor que conte incidentes por setor está a contar **incidentes
noticiados**, não incidentes ocorridos.

Dizemo-lo em `/metodologia/` e publicamos, nos dados abertos, a contagem de fontes por
incidente, para que o viés seja mensurável a partir dos próprios dados em vez de ficar
implícito.

## 11. Privacidade de quem nos lê

Sem cookies, sem analytics, sem serviços de terceiros, sem registo de endereços IP no
servidor. A pesquisa corre no navegador, contra um índice estático: não sabemos o que
qualquer pessoa procurou, e não queremos saber.

Quem consulta um registo de ciberataques pode estar a investigar o seu próprio empregador,
o seu hospital ou a sua câmara municipal. Essa consulta não deve deixar rasto connosco.
