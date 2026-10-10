/**
 * A marca do site, numa só fonte: um "c" de tinta aberto sobre papel e o ponto
 * carmim do ".pt" do cabeçalho. Sem texto no SVG, para não depender de fontes
 * instaladas em quem o desenha.
 *
 * Daqui saem o favicon.svg, o favicon.ico e o apple-touch-icon.png, gerados em
 * tempo de compilação, para que as três versões nunca divirjam.
 */
import { Resvg } from "@resvg/resvg-js";

export const MARCA_SVG = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
  <rect width="64" height="64" rx="12" fill="#1a1815"/>
  <path d="M41.5 21.5A14 14 0 1 0 41.5 42.5" fill="none" stroke="#fbfaf8" stroke-width="7" stroke-linecap="round"/>
  <rect x="44" y="40" width="9" height="9" fill="#a4243b"/>
</svg>`;

export function pngDaMarca(lado: number): Uint8Array {
  return new Resvg(MARCA_SVG, { fitTo: { mode: "width", value: lado } }).render().asPng();
}

/**
 * Um .ico com um PNG lá dentro. O formato aceita-o desde o Windows Vista, e todos
 * os navegadores o leem; é só um cabeçalho de 22 bytes à frente do PNG.
 */
export function icoDaMarca(lado = 32): Uint8Array {
  const png = pngDaMarca(lado);
  const cab = new DataView(new ArrayBuffer(22));
  cab.setUint16(2, 1, true); // tipo: ícone
  cab.setUint16(4, 1, true); // uma imagem
  cab.setUint8(6, lado);
  cab.setUint8(7, lado);
  cab.setUint16(10, 1, true); // planos
  cab.setUint16(12, 32, true); // bits por pixel
  cab.setUint32(14, png.length, true);
  cab.setUint32(18, 22, true); // posição dos dados
  const ico = new Uint8Array(22 + png.length);
  ico.set(new Uint8Array(cab.buffer), 0);
  ico.set(png, 22);
  return ico;
}
