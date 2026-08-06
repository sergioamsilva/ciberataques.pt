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
    /*
     * Duas a quatro afirmações que ensinam alguma coisa, escritas para aparecerem
     * na ficha de um incidente.
     *
     * Existem porque o bloco de referência da ficha era uma bibliografia disfarçada
     * de explicador: uma definição de uma linha seguida de três citações académicas.
     * Quem chega à ficha das Águas de Portugal não quer uma lista de DOI — quer
     * perceber o que é uma intrusão e porque é que estas coisas se descobrem tarde.
     * As fontes continuam lá, a seguir, e mais compactas.
     */
    pontos_chave: z.array(z.string()).min(2).max(4).optional(),

    /*
     * As fases por que o ataque passa, por ordem. Opcional: só faz sentido nos
     * tipos que têm uma sequência reconhecida na literatura, e é preferível não
     * ter nenhuma a inventar uma.
     *
     * `visivel_a_partir_de` é o índice, começado em 1, da fase a partir da qual a
     * organização atacada tipicamente dá por ela. É o número que explica porque a
     * data de divulgação de um incidente é quase sempre posterior à do ataque.
     */
    fases: z.array(z.string()).min(3).optional(),
    visivel_a_partir_de: z.number().int().min(1).optional(),
    nota_fases: z.string().optional(),
    revisto_em: z.string(),
  }),
});

export const collections = { tipos };
