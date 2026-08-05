import { defineCollection, z } from "astro:content";
import { glob } from "astro/loaders";

/**
 * Explicadores por tipo de ataque.
 *
 * São material de referência, não registo. A distinção é editorial e importa: o
 * registo diz o que aconteceu e cita quem o apurou; um explicador diz o que é um
 * ransomware e cita literatura revista por pares. Misturá-los faria o site parecer
 * que opina sobre os incidentes, e não opina.
 *
 * Por tipo e não por incidente: o que é ransomware é o mesmo para o Hospital Garcia
 * de Orta e para Gondomar. Doze textos mantêm-se; quarenta e cinco não.
 */
const tipos = defineCollection({
  loader: glob({ base: "./src/content/tipos", pattern: "**/*.md" }),
  schema: z.object({
    /** Tem de corresponder a uma chave de referencia/taxonomia.yaml. */
    tipo: z.string(),
    titulo: z.string(),
    resumo: z.string().max(300),
    referencias: z
      .array(
        z.object({
          autores: z.string(),
          ano: z.number(),
          titulo: z.string(),
          publicacao: z.string(),
          /* DOI verificado no CrossRef. Uma referência académica inventada é o erro
             mais destrutivo que este projeto pode cometer, por isso o campo é
             obrigatório sempre que exista, e testes/teste_explicadores.py confirma
             que cada um resolve. */
          doi: z.string().optional(),
          url: z.string().optional(),
          nota: z.string().optional(),
        }),
      )
      .min(1),
    revisto_em: z.string(),
  }),
});

export const collections = { tipos };
