import type { APIRoute, GetStaticPaths } from "astro";
import { incidentes, incidente, formatarData, nome } from "../../../lib/dados";
import { pngDoCartao, respostaPng, COR_CONFIANCA } from "../../../lib/og";

export const getStaticPaths: GetStaticPaths = () =>
  incidentes().map((r) => ({ params: { id: r.id } }));

export const GET: APIRoute = async ({ params }) => {
  const inc = incidente(params.id!);
  const n = inc.fontes.length;
  return respostaPng(
    await pngDoCartao({
      sobretitulo: `Registo · ${nome("setores", inc.setor)}`,
      titulo: inc.titulo,
      corBarra: COR_CONFIANCA[inc.estado_confirmacao],
      campos: [
        { rotulo: "Confirmação", valor: nome("estados_confirmacao", inc.estado_confirmacao) },
        { rotulo: "Data", valor: formatarData(inc.data.inicio, inc.data.precisao) },
        { rotulo: "Fontes", valor: n === 1 ? "1 fonte" : `${n} fontes` },
      ],
    }),
  );
};
