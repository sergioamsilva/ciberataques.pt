import type { APIRoute } from "astro";
import { todosOsIncidentes } from "../../lib/dados";

/**
 * Uma linha por fonte, com o incidente a que pertence.
 *
 * É a exportação que serve jornalistas e investigadores: permite ver que órgãos
 * cobriram o quê, e identificar os incidentes que uma única fonte sustenta. Sem
 * isto, o viés de cobertura ficaria implícito em vez de mensurável.
 */
const COLUNAS = [
  "incidente_id", "indice", "tipo", "publicador", "data", "titulo",
  "url", "url_arquivo", "estado_ligacao", "contem_declaracao_da_entidade",
] as const;

function celula(valor: unknown): string {
  if (valor === null || valor === undefined) return "";
  const texto = String(valor);
  return /[",\n;]/.test(texto) ? `"${texto.replace(/"/g, '""')}"` : texto;
}

export const GET: APIRoute = () => {
  const linhas = todosOsIncidentes().flatMap((i) =>
    i.fontes.map((f, indice) => [
      i.id, indice, f.tipo, f.publicador, f.data, f.titulo,
      f.url, f.url_arquivo ?? "", f.estado_ligacao ?? "",
      f.contem_declaracao_da_entidade ?? false,
    ]),
  );

  const csv =
    "﻿" +
    [COLUNAS.join(","), ...linhas.map((l) => l.map(celula).join(","))].join("\n") +
    "\n";

  return new Response(csv, {
    headers: {
      "Content-Type": "text/csv; charset=utf-8",
      "Content-Disposition": 'attachment; filename="ciberataques-pt-fontes.csv"',
    },
  });
};
