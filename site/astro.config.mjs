// @ts-check
import { defineConfig } from "astro/config";
import sitemap from "@astrojs/sitemap";
import tailwindcss from "@tailwindcss/vite";

export default defineConfig({
  site: "https://ciberataques.pt",
  trailingSlash: "always",
  compressHTML: true,
  build: {
    // Sem scripts nem estilos inline, para que a CSP possa ser estrita sem hashes
    // nem nonces. Segue o padrão do siteCybers3c.
    assetsInlineLimit: 0,
    format: "directory",
  },
  integrations: [
    sitemap({
      // O lastmod sai da data de revisão do incidente, não da data do build: dizer que
      // tudo mudou porque recompilámos é ruído para quem indexa.
      serialize(item) {
        return item;
      },
    }),
  ],
  vite: {
    plugins: [tailwindcss()],
  },
});
