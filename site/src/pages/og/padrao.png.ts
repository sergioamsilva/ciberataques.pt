import type { APIRoute } from "astro";
import { manifesto, formatarNumero } from "../../lib/dados";
import { pngDoCartao, respostaPng } from "../../lib/og";

export const GET: APIRoute = async () => {
  const m = manifesto();
  return respostaPng(
    await pngDoCartao({
      sobretitulo: `Registo público desde ${Math.min(...m.anos)}`,
      titulo: "Ciberataques a entidades portuguesas, com as fontes à vista",
      campos: [
        { rotulo: "Incidentes", valor: formatarNumero(m.total_incidentes) },
        { rotulo: "Fontes citadas", valor: formatarNumero(m.total_fontes) },
        { rotulo: "Entidades", valor: formatarNumero(m.total_entidades) },
      ],
    }),
  );
};
