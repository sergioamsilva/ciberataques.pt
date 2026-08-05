/**
 * Revelação por scroll, com observers que se auto-libertam.
 *
 * Único JavaScript próprio do site. Não é necessário para ler nada: sem ele, as
 * regras de `html.js` no CSS nunca se aplicam e tudo aparece visível de imediato.
 */
const alvos = document.querySelectorAll<HTMLElement>(".revelar");

function revelarTudo() {
  alvos.forEach((alvo) => alvo.classList.add("visivel"));
}

const semMovimento = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

if (semMovimento || !alvos.length || !("IntersectionObserver" in window)) {
  revelarTudo();
} else {
  const observador = new IntersectionObserver(
    (entradas, obs) => {
      for (const entrada of entradas) {
        if (!entrada.isIntersecting) continue;
        entrada.target.classList.add("visivel");
        obs.unobserve(entrada.target);
      }
    },
    { rootMargin: "200px 0px 0px 0px", threshold: 0 },
  );

  alvos.forEach((alvo, i) => {
    // Cascata curta dentro de cada grupo: escalonar demasiado dá a sensação de
    // página lenta em vez de composta.
    alvo.style.transitionDelay = `${Math.min(i % 8, 7) * 55}ms`;
    observador.observe(alvo);
  });

  /*
   * Salvaguarda: ao fim de 3 segundos, revelar tudo o que ainda esteja escondido.
   *
   * Este é um arquivo documental. Se o observer falhar por qualquer razão (motor de
   * renderização invulgar, captura automatizada, extensão do navegador), o resultado
   * seria conteúdo permanentemente invisível, o que é muito pior do que perder uma
   * animação. Quem já viu o elemento não nota nada; quem não viu, vê.
   */
  window.setTimeout(revelarTudo, 3000);
  window.addEventListener("beforeprint", revelarTudo);
}
