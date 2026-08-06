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
 * A separação entre o que está documentado e o que é apenas uma alegação.
 *
 * Um caso de nível 5 tem uma única fonte, e essa fonte é o próprio atacante. Não
 * há cronologia, não há impacto apurado, não há confirmação — há uma listagem.
 * Durante algum tempo cada um destes teve página própria, permanente e indexável,
 * com um título do género "X listada em site de extorsão" construído inteiramente
 * a partir do que um criminoso publicou. Tudo o que essas páginas continham era ou
 * a alegação, ou um aviso sobre a alegação.
 *
 * O critério de interesse público que as justificava respondia à pergunta errada:
 * respondia a "vale a pena escrever sobre esta entidade?", quando a pergunta é
 * "há aqui alguma coisa para escrever?". Não há.
 *
 * Continuam no registo, nos dados abertos e nas contagens — esconder o que
 * recolhemos seria pior. Deixam é de ter página por entidade, e passam a viver
 * numa lista única em /alegacoes/, onde o que são está explicado uma vez e bem.
 */
export function ehAlegacao(inc: { estado_confirmacao: EstadoConfirmacao }): boolean {
  return inc.estado_confirmacao === "alegado_pelo_atacante";
}

/** Os incidentes com página própria: tudo o que não é só a palavra do atacante. */
export function documentados(): ResumoIncidente[] {
  return incidentes().filter((i) => !ehAlegacao(i));
}

/** As listagens em sites de extorsão sem qualquer confirmação independente. */
export function alegacoes(): ResumoIncidente[] {
  return incidentes().filter(ehAlegacao);
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
