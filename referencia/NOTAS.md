# Notas de curadoria

Armadilhas encontradas, verificações que falharam, e casos que ficaram de fora. Existe
para que ninguém repita trabalho já feito, sobretudo o trabalho que deu em nada.

## Casos verificados e NÃO semeados

Estes casos aparecem em listagens e resumos, mas a verificação contra fontes primárias
falhou. Não entram no registo enquanto não houver fonte que os sustente.

| Caso | Estado da verificação |
|---|---|
| **Altice Portugal / HIVE, agosto de 2022** | Procura em publico.pt, eco.sapo.pt, observador.pt, tek.sapo.pt, dn.pt e jornaldenegocios.pt não devolveu cobertura datada deste incidente. O que aparece é o caso **Altice de abril de 2020** (associado ao CyberTeam, no mesmo período do ataque à EDP) e a condenação do autor em janeiro de 2022. Existe um artigo do Tek sobre uma "aplicação departamental" da Altice, mas sem data no URL. **Reverificar antes de semear, e separar cuidadosamente 2020 de 2022.** |
| **Altice / Benfica 2020, caso "Zambrius"** | Pista forte e por explorar: autor condenado em janeiro de 2022 a seis anos de prisão por 28 crimes, com referência a acesso a dados de mais de 155 mil clientes. Fonte seria uma **decisão judicial**, o tipo de fonte mais forte de que dispomos. Falta datar os artigos do DN, que não trazem data no URL. Atenção à política editorial: não nomear a pessoa condenada sem confirmar que a decisão é pública e transitada. |
| **Grupo Cofina, fevereiro de 2022** | Os próprios títulos usam "suspeita", "eventual" e "alegado". O Lapsus$ destacou uma publicação do Correio da Manhã no seu canal, mas **não reivindicou**. A ocorrência de ataque nunca foi confirmada. Se for semeado, tem de ser com estado `noticiado_por_uma_fonte` ou inferior, e a incerteza tem de estar no resumo. |
| **Centro Hospitalar de Setúbal, 2021** | A informação provém de agregadores e referências secundárias, não de comunicado nem de cobertura nacional de referência. **Não semear sem fonte primária.** |
| ~~**Millennium BCP, DDoS 2022**~~ | **RESOLVIDO.** Data confirmada: 3 de outubro de 2022, a partir das 14h. Registado em `2022-millennium-bcp`. |
| **Câmara Municipal de Setúbal** | A coima de 170.000 € da CNPD (novembro de 2022) é por tratamento de dados de refugiados ucranianos. **Não é um ciberataque.** Se entrar no site, entra como deliberação regulatória, nunca como incidente. |
| **Auchan, novembro de 2024** | A fuga é atribuída à casa-mãe francesa. O impacto em Portugal não está confirmado. |
| **Nabeiro/Delta, EMEL, ANA, Fidelidade, DECO, Trivalor, ONI, ISCTE, IST, Novo Banco, Banco de Portugal, Jerónimo Martins** | Procura dedicada não encontrou qualquer incidente. Ausência de fonte não é prova de que nada aconteceu, mas também não é registo. |

## Casos que NÃO são incidentes próprios

- **SIBS / rede Multibanco** e **INEM**, fevereiro de 2022: não foram atacados. Sofreram o
  impacto por serem clientes da Vodafone. Registados em `entidades_afetadas_em_cascata`
  no incidente `2022-vodafone-portugal`. Contá-los como incidentes inflacionaria o registo.
- **Worten**, março de 2022: o comunicado é da Sonae MC e refere Continente e Wells. A
  Worten não foi confirmada como afetada.
- **INE / Censos 2021**: a coima de 4.300.000 € da CNPD (Deliberação/2022/1072, dezembro de
  2022) é a maior alguma vez aplicada em Portugal, mas sanciona **tratamento ilícito de dados**
  (dados de saúde e religião, dever de informação, escolha do subcontratante Cloudflare,
  transferências internacionais, ausência de avaliação de impacto). **Não houve ciberataque.**
  Fora do registo, pela mesma regra que exclui a coima de Setúbal. O sítio chama-se
  ciberataques.pt, não protecaodedados.pt. Deliberações da CNPD entram como
  `consequencias_regulatorias` de um incidente, nunca como incidente.
- **Portal das Finanças**, outubro de 2024: é uma **exposição de credenciais** cuja origem
  o próprio Ministério atribui a sistemas de terceiros e a equipamentos dos utilizadores,
  não uma intrusão nos sistemas da Autoridade Tributária. Classificar como
  `exposicao_credenciais`, e dizê-lo no resumo, ou o leitor conclui o contrário.

## Lacunas de cobertura

- **2025 é o pior ano do registo.** O CNCS descreve um ransomware a uma entidade da
  administração pública central em outubro de 2025, com impacto nacional por prestar
  serviço de autenticação, e uma campanha contra o setor da educação em novembro. **Não
  nomeia nenhuma entidade.** O perfil do primeiro caso sugere fortemente a AMA, mas isso é
  inferência: não semear.
- **2017 a 2019** estão praticamente por fazer.

## O viés que quase nos escapou: a imprensa nacional

O ciberataque ao município de **Santa Comba Dão** (junho de 2024) esteve por registar
até alguém perguntar por ele. Não por falta de fontes: havia **comunicado da própria
câmara**, que é a fonte mais forte que este registo pode ter. Faltava era ter procurado
onde ele estava.

A causa é estrutural e mensurável. Nesta data, 121 das 147 fontes citadas — **82%** —
vinham de apenas três órgãos nacionais (Observador, Público, ECO). A imprensa regional
contribuía com **uma** fonte, e os comunicados diretos de entidades com **duas**.

Um município de onze mil habitantes não é notícia em Lisboa. Se a recolha só olha para
Lisboa, o registo herda essa cegueira e depois apresenta-a como se fosse o retrato do
país. É o mesmo viés que `/metodologia/#vies` assume, mas agravado por uma decisão
nossa: a lista de fontes.

**O que mudou:** `referencia/fontes.yaml` passa a incluir imprensa regional (Diário de
Coimbra, Diário de Viseu, Jornal do Centro, Região de Leiria, Notícias de Aveiro,
Cidade Hoje). Não resolve — são seis títulos para 308 municípios —, mas muda a natureza
do problema, de cego para incompleto.

**O que continua por resolver:** os comunicados publicados nos sítios das próprias
câmaras. São a melhor fonte possível e não há forma prática de os recolher sem raspar
308 sítios. Por agora, dependem de pesquisa manual e de quem nos avise.

**Regra de curadoria que daqui resulta:** ao investigar um caso local, procurar sempre
(a) no sítio da própria entidade e (b) sem restringir a pesquisa a órgãos nacionais.
Foi assim que Santa Comba Dão apareceu, à segunda tentativa.

## Armadilhas das fontes

- **Datas de publicação**: o Público, o ECO e o Observador trazem a data no próprio URL,
  o que as torna auto-verificáveis. O Tek, o DN e o Jornal de Negócios não. Para estes,
  confirmar a data no artigo antes de citar, ou não citar.
- **publico.pt devolve 403** a acessos automatizados. As datas continuam a ser legíveis
  no URL, mas o texto não. Excertos destes artigos exigem verificação manual.
- **Os números do atacante mudam.** No caso da TAP, o Ragnar Locker falou em 400 mil
  clientes a 31 de agosto, publicou ficheiros de cerca de 115 mil a 13 de setembro, e
  anunciou 1,5 milhões a 20 de setembro. Registar sempre com a data da alegação, em
  `disputas[]`, nunca como facto.
- **Uma entidade pode confirmar sem emitir comunicado.** A TAP confirmou o ataque de 2022
  por Twitter. Nestes casos, marcar `contem_declaracao_da_entidade: true` na notícia que
  reproduz a declaração, em vez de forçar o estado de confirmação para baixo.
