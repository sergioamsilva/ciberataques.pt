/**
 * Contagem animada dos números do registo.
 *
 * O valor final está no HTML e é o que se lê sem JavaScript: só o substituímos
 * enquanto anima, e repomo-lo no fim. Um número que não aparece sem JS seria pior
 * do que um número que não anima.
 */
const alvos = document.querySelectorAll<HTMLElement>("[data-contar]");

function animar(elemento: HTMLElement) {
  const destino = Number(elemento.dataset.contar || "0");
  if (!Number.isFinite(destino) || destino <= 0) return;

  const duracao = 900;
  const inicio = performance.now();
  const formatar = (n: number) => n.toLocaleString("pt-PT");

  function passo(agora: number) {
    const t = Math.min((agora - inicio) / duracao, 1);
    // easeOutExpo: arranca depressa e assenta, em vez de chegar a acelerar.
    const eased = t === 1 ? 1 : 1 - Math.pow(2, -10 * t);
    elemento.textContent = formatar(Math.round(destino * eased));
    if (t < 1) requestAnimationFrame(passo);
  }
  requestAnimationFrame(passo);
}

if (
  alvos.length &&
  "IntersectionObserver" in window &&
  !window.matchMedia("(prefers-reduced-motion: reduce)").matches
) {
  const observador = new IntersectionObserver(
    (entradas, obs) => {
      for (const entrada of entradas) {
        if (!entrada.isIntersecting) continue;
        animar(entrada.target as HTMLElement);
        obs.unobserve(entrada.target);
      }
    },
    { threshold: 0.4 },
  );
  alvos.forEach((alvo) => observador.observe(alvo));
}
