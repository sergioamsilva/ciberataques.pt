import type { APIRoute } from "astro";
import { todosOsIncidentes, entidades } from "../../lib/dados";

/** Uma linha por incidente. Achatado de propósito: tem de abrir num Excel sem trabalho. */
const COLUNAS = [
  "id", "titulo", "data_inicio", "precisao_data", "data_divulgacao",
  "entidades_afetadas", "setor", "tipos_ataque", "estado_confirmacao",
  "ator", "ator_atribuicao_por", "dados_pessoais_afetados",
  "categorias_dados", "titulares_declarados", "pessoas_afetadas_declaradas",
  "resgate_pago", "notificou_cncs", "notificou_cnpd", "n_fontes",
  "tem_disputas", "url",
] as const;

function celula(valor: unknown): string {
  if (valor === null || valor === undefined) return "";
  const texto = Array.isArray(valor) ? valor.join("; ") : String(valor);
  return /[",\n;]/.test(texto) ? `"${texto.replace(/"/g, '""')}"` : texto;
}

export const GET: APIRoute = () => {
  const nomes = entidades();
  const linhas = todosOsIncidentes().map((i) => [
    i.id,
    i.titulo,
    i.data.inicio,
    i.data.precisao,
    i.data.divulgacao ?? "",
    i.entidades_afetadas.map((e) => nomes[e]?.nome ?? e),
    i.setor,
    i.tipos_ataque,
    i.estado_confirmacao,
    i.ator?.grupo ?? "",
    i.ator?.atribuicao_por ?? "",
    i.dados_pessoais?.afetados ?? "",
    i.dados_pessoais?.categorias ?? [],
    i.dados_pessoais?.titulares_declarados ?? "",
    i.impacto?.pessoas_afetadas_declaradas ?? "",
    i.impacto?.resgate_pago ?? "",
    i.notificacoes?.cncs ?? "",
    i.notificacoes?.cnpd ?? "",
    i.fontes.length,
    (i.disputas?.length ?? 0) > 0,
    `https://ciberataques.pt/incidentes/${i.id}/`,
  ]);

  // BOM UTF-8: sem ele o Excel em Windows estraga os acentos, e este é um ficheiro
  // feito para ser aberto por jornalistas, não por engenheiros.
  const csv =
    "﻿" +
    [COLUNAS.join(","), ...linhas.map((l) => l.map(celula).join(","))].join("\n") +
    "\n";

  return new Response(csv, {
    headers: {
      "Content-Type": "text/csv; charset=utf-8",
      "Content-Disposition": 'attachment; filename="ciberataques-pt-incidentes.csv"',
    },
  });
};
