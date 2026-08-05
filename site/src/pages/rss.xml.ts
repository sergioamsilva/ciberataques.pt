import type { APIRoute } from "astro";
import { todosOsIncidentes, entidades, nome } from "../lib/dados";

function escapar(texto: string): string {
  return texto
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

export const GET: APIRoute = () => {
  const nomes = entidades();

  /* Ordenado pela data de revisão, não pela data do incidente: o feed serve para
     saber o que mudou no registo, incluindo correções a incidentes antigos. */
  const itens = todosOsIncidentes()
    .sort((a, b) => b.revisao.data.localeCompare(a.revisao.data))
    .slice(0, 50)
    .map((i) => {
      const url = `https://ciberataques.pt/incidentes/${i.id}/`;
      const alvos = i.entidades_afetadas.map((e) => nomes[e]?.nome ?? e).join(", ");
      const descricao = [
        i.resumo,
        `Entidades: ${alvos}.`,
        `Estado: ${nome("estados_confirmacao", i.estado_confirmacao)}.`,
        `Fontes: ${i.fontes.length}.`,
      ].join(" ");
      return `    <item>
      <title>${escapar(i.titulo)}</title>
      <link>${url}</link>
      <guid isPermaLink="true">${url}</guid>
      <pubDate>${new Date(`${i.revisao.data}T12:00:00Z`).toUTCString()}</pubDate>
      <description>${escapar(descricao)}</description>
      <category>${escapar(nome("setores", i.setor))}</category>
    </item>`;
    })
    .join("\n");

  const xml = `<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>ciberataques.pt</title>
    <link>https://ciberataques.pt/</link>
    <description>Registo público de ciberataques a entidades portuguesas. Incidentes novos e atualizados.</description>
    <language>pt-PT</language>
${itens}
  </channel>
</rss>
`;

  return new Response(xml, {
    headers: { "Content-Type": "application/rss+xml; charset=utf-8" },
  });
};
