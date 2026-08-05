import type { APIRoute } from "astro";
import { todosOsIncidentes, manifesto } from "../../lib/dados";

export const GET: APIRoute = () =>
  new Response(
    JSON.stringify(
      {
        ...manifesto(),
        fonte: "https://ciberataques.pt/",
        licenca: "https://creativecommons.org/licenses/by/4.0/deed.pt",
        atribuicao: "ciberataques.pt",
        incidentes: todosOsIncidentes(),
      },
      null,
      2,
    ),
    { headers: { "Content-Type": "application/json; charset=utf-8" } },
  );
