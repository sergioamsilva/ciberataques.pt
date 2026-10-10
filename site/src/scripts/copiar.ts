/*
 * Botões "Copiar": copiam o texto do elemento cujo id está em data-copiar.
 * Sem JavaScript o botão nem aparece (só é visível sob .js), e o texto continua
 * selecionável à mão.
 */
for (const botao of document.querySelectorAll<HTMLButtonElement>("[data-copiar]")) {
  const original = botao.textContent?.trim() ?? "Copiar";
  botao.addEventListener("click", async () => {
    const alvo = document.getElementById(botao.dataset.copiar!);
    if (!alvo) return;
    try {
      await navigator.clipboard.writeText(alvo.textContent?.trim() ?? "");
      botao.textContent = "Copiado";
    } catch {
      botao.textContent = "Selecione e copie";
    }
    setTimeout(() => (botao.textContent = original), 2000);
  });
}
