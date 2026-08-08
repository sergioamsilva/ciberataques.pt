/**
 * Leitura do registo canónico em tempo de compilação.
 *
 * O site não faz um único pedido de rede em runtime: tudo o que mostra vem daqui,
 * lido de ../data/out durante o build. Segue o padrão de snsRadar/site/src/lib/dados.ts.
 */
import fs from "node:fs";
import path from "node:path";

// A partir de process.cwd(), que é sempre site/ durante o build, e não de
// import.meta.url: este módulo é compilado para dist/.prerender/chunks/, onde um
// caminho relativo ao ficheiro deixaria de apontar para a raiz do repositório.
const RAIZ = path.resolve(process.cwd(), "..");
const OUT = path.join(RAIZ, "data", "out");
const REFERENCIA = path.join(RAIZ, "referencia");

function lerJson<T>(...partes: string[]): T {
  return JSON.parse(fs.readFileSync(path.join(...partes), "utf-8")) as T;
}

export type EstadoConfirmacao =
  | "confirmado_pela_entidade"
  | "confirmado_por_regulador"
  | "reportado_por_media"
  | "noticiado_por_uma_fonte"
  | "alegado_pelo_atacante"
  | "desmentido";

export type TipoFonte =
  | "comunicado"
  | "regulador"
  | "noticia"
  | "relatorio"
  | "leak_site"
  | "dre";

export interface Fonte {
  tipo: TipoFonte;
  url: string;
  url_arquivo: string | null;
  publicador: string;
  data: string;
  titulo: string;
  excerto: string | null;
  estado_ligacao?: "viva" | "alterada" | "morta";
  contem_declaracao_da_entidade?: boolean;
  contem_declaracao_de_autoridade?: boolean;
}

export interface Evento {
  data: string;
  tipo: string;
  texto: string;
  fonte: number;
}

export interface Disputa {
  afirmacao: string;
  segundo: string;
  fonte_afirmacao: number;
  contestado_por: string | null;
  fonte_contestacao: number | null;
  nota: string | null;
}

export interface Incidente {
  id: string;
  titulo: string;
  resumo: string;
  entidades_afetadas: string[];
  entidades_afetadas_em_cascata?: string[];
  setor: string;
  tipos_ataque: string[];
  data: {
    inicio: string;
    precisao: string;
    fim?: string;
    detecao?: string;
    divulgacao?: string;
  };
  estado_confirmacao: EstadoConfirmacao;
  ator?: {
    grupo: string | null;
    atribuicao_por: string | null;
    confianca: string | null;
    nota?: string | null;
  };
  dados_pessoais?: {
    afetados: boolean | null;
    categorias: string[];
    titulares_declarados: number | null;
    nota: string | null;
  };
  impacto?: {
    servicos_afetados?: string[];
    duracao_horas?: number | null;
    pessoas_afetadas_declaradas?: number | null;
    custo_declarado_eur?: number | null;
    resgate_pedido_eur?: number | null;
    resgate_pedido_nota?: string | null;
    resgate_pago?: boolean | null;
  };
  notificacoes?: Record<string, boolean | null>;
  consequencias_regulatorias?: Array<{
    autoridade: string;
    data: string;
    tipo?: string;
    valor_eur?: number | null;
    processo?: string | null;
    descricao: string;
    fonte: number;
  }>;
  cronologia?: Evento[];
  fontes: Fonte[];
  disputas?: Disputa[];
  relacionados?: string[];
  etiquetas?: string[];
  revisao: { curador: string; data: string; versao: number; nota?: string | null };
  correcoes?: Array<{ data: string; descricao: string; origem?: string }>;
}

export interface ResumoIncidente {
  id: string;
  titulo: string;
  data: string;
  precisao_data: string;
  ano: number;
  /** Todos os anos que o incidente atravessa. Um só, exceto nas vagas plurianuais. */
  anos: number[];
  setor: string;
  tipos_ataque: string[];
  entidades_afetadas: string[];
  estado_confirmacao: EstadoConfirmacao;
  ator: string | null;
  n_fontes: number;
  tem_disputas: boolean;
}

export interface Entidade {
  id: string;
  nome: string;
  nome_curto?: string;
  setor: string;
  tipo: string;
  distrito?: string;
  url?: string;
  nota?: string;
  /** Formas alternativas pelas quais a entidade aparece; alimentam a pesquisa. */
  chaves?: string[];
  incidentes: string[];
  incidentes_em_cascata: string[];
}

export interface Agregados {
  total: number;
  por_ano: Record<string, number>;
  por_setor: Record<string, number>;
  por_tipo_ataque: Record<string, number>;
  por_estado_confirmacao: Record<string, number>;
  por_ator: Record<string, number>;
  distribuicao_fontes_por_incidente: Record<string, number>;
  incidentes_com_disputas: number;
}

interface EntradaTaxonomia {
  nome: string;
  descricao?: string;
  peso?: number;
  explicacao?: string;
}

let _taxonomia: Record<string, Record<string, EntradaTaxonomia>> | null = null;

/** A taxonomia é YAML; convertemo-la a JSON no build via ingestao/construir.py. */
export function taxonomia(): Record<string, Record<string, EntradaTaxonomia>> {
  if (!_taxonomia) {
    _taxonomia = lerJson(REFERENCIA, "taxonomia.json");
  }
  return _taxonomia;
}

export function incidentes(): ResumoIncidente[] {
  return lerJson<ResumoIncidente[]>(OUT, "incidentes.json");
}

export function incidente(id: string): Incidente {
  return lerJson<Incidente>(OUT, "incidentes", `${id}.json`);
}

export function todosOsIncidentes(): Incidente[] {
  return incidentes().map((r) => incidente(r.id));
}

export function entidades(): Record<string, Entidade> {
  return lerJson<Record<string, Entidade>>(OUT, "entidades.json");
}

export function agregados(): Agregados {
  return lerJson<Agregados>(OUT, "agregados.json");
}

export function manifesto(): {
  construido_em: string;
  total_incidentes: number;
  total_fontes: number;
  total_entidades: number;
  anos: number[];
  licenca_dados: string;
} {
  return lerJson(OUT, "manifesto.json");
}

/** Nome legível de um termo da taxonomia. Nunca mostramos o identificador ao leitor. */
export function nome(grupo: string, chave: string): string {
  return taxonomia()[grupo]?.[chave]?.nome ?? chave;
}

export function explicacaoEstado(estado: EstadoConfirmacao): string {
  return taxonomia().estados_confirmacao?.[estado]?.explicacao ?? "";
}

const MESES = [
  "janeiro", "fevereiro", "março", "abril", "maio", "junho",
  "julho", "agosto", "setembro", "outubro", "novembro", "dezembro",
];

/**
 * Formata uma data respeitando a precisão declarada.
 *
 * Um incidente de que só se conhece o mês não deve aparecer com um dia inventado.
 * É a diferença entre um arquivo e uma coleção de palpites.
 */
export function formatarData(iso: string, precisao = "dia"): string {
  const [ano, mes, dia] = iso.split("-").map(Number);
  if (precisao === "ano") return `${ano}`;
  if (precisao === "mes") return `${MESES[mes - 1]} de ${ano}`;
  if (precisao === "semana") return `semana de ${dia} de ${MESES[mes - 1]} de ${ano}`;
  /*
   * "data desconhecida (2026)" era literalmente verdade e lia-se como uma falha
   * nossa, logo na primeira linha de dezenas de cartões da listagem. O que não se
   * sabe destes casos é o DIA em que o ataque começou — o ano sabe-se, e é o que
   * interessa a quem percorre um arquivo cronológico. Dizemos o que se sabe
   * primeiro e a ressalva a seguir.
   */
  if (precisao === "desconhecida") return `${ano} · dia por apurar`;
  return `${dia} de ${MESES[mes - 1]} de ${ano}`;
}

export function formatarNumero(n: number): string {
  return n.toLocaleString("pt-PT");
}

/*
 * A cor de cada grau de confirmação, num só sítio.
 *
 * Estava repetida em três componentes. Além do risco óbvio de divergirem, a
 * repetição escondia o problema maior: a rampa existia e quase não se via. Numa
 * listagem, "confirmado pela entidade" e "alegado pelo atacante" liam-se como duas
 * etiquetas cinzentas iguais, e o campo que distingue este registo de todos os
 * outros era o elemento menos visível da página.
 */
export function corDeConfianca(estado: EstadoConfirmacao): string {
  const cores: Record<EstadoConfirmacao, string> = {
    confirmado_pela_entidade: "var(--color-conf-entidade)",
    confirmado_por_regulador: "var(--color-conf-regulador)",
    reportado_por_media: "var(--color-conf-media)",
    noticiado_por_uma_fonte: "var(--color-conf-unica)",
    alegado_pelo_atacante: "var(--color-conf-atacante)",
    desmentido: "var(--color-conf-desmentido)",
  };
  return cores[estado];
}

/*
 * Uma listagem em site de extorsão nunca sustenta, sozinha, uma entrada neste
 * arquivo.
 *
 * Houve vinte e sete assim, publicadas com o argumento de que subiriam a incidente
 * documentado quando aparecesse fonte independente. Verificou-se em 2026-08-08:
 * nenhuma alguma vez subiu. A justificação não se sustentava, e foram retiradas para
 * data/fila/alegacoes-retiradas/, que é versionado e auditável.
 *
 * As fontes de sites de extorsão continuam a existir no registo — dez incidentes
 * confirmados pelas próprias entidades citam-nas como corroboração, e isso é útil.
 * O que deixou de haver é um incidente que assente só nelas.
 */
export function incidentesDocumentados(): ResumoIncidente[] {
  return incidentes();
}


export interface ContextoAno {
  incidentes: number;
  variacao_percentual?: number;
  edicao: string;
  url: string;
  citacao: string;
  nota?: string;
}

export interface Contexto {
  fonte: { nome: string; serie: string; url: string; nota: string };
  anos: Record<string, ContextoAno>;
  comparacao: Record<string, { cert_pt: number; neste_registo: number }>;
}

/*
 * O denominador oficial, do CERT.PT.
 *
 * Lê-se de contexto.json e não de agregados.json, e a separação é deliberada:
 * são contagens de outra entidade, com outro universo, e a única coisa que não
 * podem sofrer é serem somadas às nossas por distração.
 */
export function contexto(): Contexto {
  return lerJson<Contexto>(OUT, "contexto.json");
}

export interface RefMitre {
  id: string;
  tipo: "grupo" | "software";
  nome: string;
  url: string;
  aliases: string[];
}

/*
 * A ligação de um ator ao MITRE ATT&CK, quando existe.
 *
 * Devolve null quando o grupo não está documentado pela MITRE, o que é o caso da
 * maioria — e é informação, não falha: as marcas de ransomware que atingem
 * municípios e PME portuguesas estão em boa parte abaixo do limiar de documentação
 * do ATT&CK.
 *
 * Isto NÃO diz que o incidente usou as técnicas que a MITRE associa ao grupo. Ver
 * o cabeçalho de referencia/atores.yaml para a razão de não atribuirmos técnicas
 * por incidente.
 */
export function mitreDoAtor(ator: string | null | undefined): RefMitre | null {
  if (!ator) return null;
  const dados = lerJson<{ atores: Record<string, { mitre: RefMitre | null }> }>(
    OUT,
    "atores.json",
  );
  /*
   * Insensível a maiúsculas de propósito: os sites de extorsão escrevem "akira" e
   * "lockbit3", a MITRE escreve "Akira". É o mesmo ator, e resolver só pela forma
   * exata faria a ligação desaparecer justamente nos casos vindos do tracker.
   */
  const chave = Object.keys(dados.atores).find(
    (k) => k.toLowerCase() === ator.toLowerCase(),
  );
  return chave ? (dados.atores[chave].mitre ?? null) : null;
}

/*
 * A vista geográfica do registo.
 *
 * O arquivo tinha entradas por setor, por tipo, por ano e por entidade, e nenhuma
 * por território — apesar de 88 dos 89 registos terem distrito. Passou a fazer
 * falta quando o mapa da página inicial deixou de ser uma imagem e passou a ser
 * navegação: uma marca que se vê e não se abre é uma promessa por cumprir.
 */
export function identificadorDeDistrito(nome: string): string {
  return nome
    .normalize("NFD")
    .replace(/[̀-ͯ]/g, "")
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-|-$/g, "");
}

export interface Distrito {
  id: string;
  nome: string;
  incidentes: ResumoIncidente[];
}

export function distritos(): Distrito[] {
  const todas = entidades();
  const por = new Map<string, ResumoIncidente[]>();
  for (const inc of incidentes()) {
    /* Um incidente com duas entidades no mesmo distrito conta uma vez. */
    const seus = new Set(
      inc.entidades_afetadas.map((e) => todas[e]?.distrito).filter(Boolean) as string[],
    );
    for (const d of seus) {
      if (!por.has(d)) por.set(d, []);
      por.get(d)!.push(inc);
    }
  }
  return [...por.entries()]
    .map(([nome, lista]) => ({ id: identificadorDeDistrito(nome), nome, incidentes: lista }))
    .sort((a, b) => b.incidentes.length - a.incidentes.length || a.nome.localeCompare(b.nome, "pt"));
}

/*
 * Números por extenso, para texto corrido.
 *
 * Existe por causa de um título escrito à mão que os dados desmentiram: a página
 * inicial anunciou durante meses "Dez anos, marca a marca", e continuou a
 * anunciá-lo quando o registo passou a cobrir de 2012 a 2026, que são quinze.
 *
 * É o mesmo erro que o gráfico dos setores tinha e que a banda do ano de pico
 * evitou desde o início: um número escrito num sítio e os dados noutro acabam
 * sempre por divergir, e quem lê não tem como saber qual dos dois está certo.
 */
const EXTENSO = [
  "zero", "um", "dois", "três", "quatro", "cinco", "seis", "sete", "oito", "nove",
  "dez", "onze", "doze", "treze", "catorze", "quinze", "dezasseis", "dezassete",
  "dezoito", "dezanove", "vinte", "vinte e um", "vinte e dois", "vinte e três",
  "vinte e quatro", "vinte e cinco", "vinte e seis", "vinte e sete", "vinte e oito",
  "vinte e nove", "trinta",
];

export function porExtenso(n: number): string {
  return EXTENSO[n] ?? String(n);
}

/** Quantos anos o registo abrange, do primeiro incidente ao último. */
export function amplitudeEmAnos(): number {
  const anos = agregados().por_ano ? Object.keys(agregados().por_ano).map(Number) : [];
  if (anos.length === 0) return 0;
  return Math.max(...anos) - Math.min(...anos) + 1;
}

export interface SetorNoContexto {
  ano: string;
  origem: string;
  nota?: string | null;
  percentagem_oficial: number;
  neste_registo: number;
  total_do_ano_neste_registo: number;
}

/*
 * O peso de um setor na contagem oficial, contra o peso que tem aqui.
 *
 * É a medida de viés mais afiada do site. O total anual já dizia que este arquivo é
 * uma fração do que acontece; isto diz onde essa fração é mais fina — e a resposta
 * não é uniforme. A banca vale entre 10% e 23% da contagem oficial e não tem um
 * único incidente aqui, porque os ataques à banca são sobretudo phishing a clientes,
 * que ninguém comunica como incidente de uma entidade nomeada.
 */
export function setorNoContexto(setor: string): SetorNoContexto[] {
  const ctx = lerJson<{
    por_setor: Record<
      string,
      {
        origem: string;
        nota?: string | null;
        setores: Record<
          string,
          { percentagem_oficial: number; neste_registo: number; total_do_ano_neste_registo: number }
        >;
      }
    >;
  }>(OUT, "contexto.json");

  return Object.entries(ctx.por_setor ?? {})
    .filter(([, v]) => v.setores[setor])
    .map(([ano, v]) => ({ ano, origem: v.origem, nota: v.nota, ...v.setores[setor] }))
    .sort((a, b) => b.ano.localeCompare(a.ano));
}
