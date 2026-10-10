/**
 * Imagens de pré-visualização (Open Graph), geradas em tempo de compilação.
 *
 * Um jornalista partilha uma ficha no Slack da redação, um investigador cola-a no
 * X: o que aparece é esta imagem, e até aqui não aparecia nada. A imagem repete o
 * que a ficha diz no topo — título, grau de confirmação em texto, data, número de
 * fontes — porque é isso que distingue o registo de uma notícia.
 *
 * satori desenha o SVG a partir de uma árvore de nós, resvg rasteriza-o para PNG.
 * Não há pedidos de rede: as fontes vêm do node_modules, em woff (o satori não lê
 * woff2), só o subconjunto latino, que cobre o português.
 */
import fs from "node:fs";
import path from "node:path";
import satori from "satori";
import { Resvg } from "@resvg/resvg-js";

const FONTES_DIR = path.resolve(process.cwd(), "node_modules", "@fontsource");
const lerFonte = (pacote: string, ficheiro: string) =>
  fs.readFileSync(path.join(FONTES_DIR, pacote, "files", ficheiro));

const FONTES = [
  { name: "Serif", data: lerFonte("source-serif-4", "source-serif-4-latin-400-normal.woff"), weight: 400 as const, style: "normal" as const },
  { name: "Serif", data: lerFonte("source-serif-4", "source-serif-4-latin-600-normal.woff"), weight: 600 as const, style: "normal" as const },
  { name: "Mono", data: lerFonte("jetbrains-mono", "jetbrains-mono-latin-500-normal.woff"), weight: 500 as const, style: "normal" as const },
];

/* Os mesmos valores dos tokens de global.css. O satori não lê CSS. */
const COR = {
  papel: "#fbfaf8",
  tinta: "#1a1815",
  suave: "#5f5a52",
  borda: "#cdc6ba",
  acento: "#a4243b",
};

export const LARGURA = 1200;
export const ALTURA = 630;

type No = { type: string; props: Record<string, unknown> };
/* O satori exige display explícito em qualquer div com mais de um filho. */
const el = (type: string, style: Record<string, unknown>, children?: unknown): No => ({
  type,
  props: { style: type === "div" ? { display: "flex", ...style } : style, children },
});

export interface CartaoOg {
  /** Linha pequena acima do título, em monoespaçada. */
  sobretitulo: string;
  titulo: string;
  /** Pares rótulo/valor no rodapé do cartão. */
  campos: { rotulo: string; valor: string }[];
  /** Cor da barra lateral: a da escala de confirmação, ou o acento. */
  corBarra?: string;
}

function tamanhoDoTitulo(titulo: string): number {
  if (titulo.length > 90) return 52;
  if (titulo.length > 60) return 60;
  return 70;
}

function arvore(c: CartaoOg): No {
  const marca = el("div", { display: "flex", fontFamily: "Mono", fontSize: 28, color: COR.tinta }, [
    el("span", {}, "ciberataques"),
    el("span", { color: COR.acento }, ".pt"),
  ]);

  const campos = el(
    "div",
    { display: "flex", gap: 56, borderTop: `2px solid ${COR.borda}`, paddingTop: 28 },
    c.campos.map((f) =>
      el("div", { display: "flex", flexDirection: "column", gap: 6 }, [
        el("span", { fontFamily: "Mono", fontSize: 18, color: COR.suave, textTransform: "uppercase", letterSpacing: 1 }, f.rotulo),
        el("span", { fontFamily: "Serif", fontWeight: 600, fontSize: 30, color: COR.tinta }, f.valor),
      ]),
    ),
  );

  return el(
    "div",
    { display: "flex", width: LARGURA, height: ALTURA, background: COR.papel },
    [
      el("div", { width: 18, height: ALTURA, background: c.corBarra ?? COR.acento }, []),
      el(
        "div",
        { display: "flex", flexDirection: "column", justifyContent: "space-between", flex: 1, padding: "56px 72px 60px 64px" },
        [
          marca,
          el("div", { display: "flex", flexDirection: "column", gap: 18 }, [
            el("span", { fontFamily: "Mono", fontSize: 22, color: COR.acento, textTransform: "uppercase", letterSpacing: 2 }, c.sobretitulo),
            el(
              "div",
              { fontFamily: "Serif", fontWeight: 600, fontSize: tamanhoDoTitulo(c.titulo), lineHeight: 1.12, color: COR.tinta, letterSpacing: -0.5 },
              c.titulo,
            ),
          ]),
          campos,
        ],
      ),
    ],
  );
}

export async function pngDoCartao(c: CartaoOg): Promise<Uint8Array> {
  const svg = await satori(arvore(c) as never, { width: LARGURA, height: ALTURA, fonts: FONTES });
  return new Resvg(svg, { fitTo: { mode: "width", value: LARGURA } }).render().asPng();
}

/* Cores literais da escala de confirmação, as mesmas de --color-conf-* em global.css. */
export const COR_CONFIANCA: Record<string, string> = {
  confirmado_pela_entidade: "#2a2621",
  confirmado_por_regulador: "#443d34",
  reportado_por_media: "#5f5648",
  noticiado_por_uma_fonte: "#7c725f",
  alegado_pelo_atacante: "#9c9179",
  desmentido: "#bdb29a",
};

export function respostaPng(png: Uint8Array): Response {
  return new Response(png as BodyInit, { headers: { "Content-Type": "image/png" } });
}
