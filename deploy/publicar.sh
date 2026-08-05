#!/usr/bin/env bash
#
# Publica o ciberataques.pt no VPS.
#
# Executar a partir da raiz do repositório, com o registo já revisto e comprometido
# em git. Publicar sem commit é publicar algo que não se consegue provar depois.
#
#   ./deploy/publicar.sh
#
set -uo pipefail

RAIZ="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$RAIZ"

# Ajustar ao VPS antes da primeira publicação.
DESTINO="${CIBERATAQUES_DESTINO:-utilizador@vps:/var/www/ciberataques/}"
PORTA_SSH="${CIBERATAQUES_PORTA_SSH:-22}"
CHAVE_SSH="${CIBERATAQUES_CHAVE_SSH:-$HOME/.ssh/ciberataques_deploy}"

falhar() { echo -e "\033[31mFALHOU:\033[0m $1" >&2; exit 1; }

if [[ -n "$(git status --porcelain data/ referencia/)" ]]; then
  falhar "há alterações não comprometidas no registo. Rever o diff e fazer commit antes de publicar."
fi

echo "==> Validar e construir"
python atualizar.py --site || falhar "a construção não passou"

echo "==> Enviar para o VPS"
rsync -avz --delete --chmod=D755,F644 \
  -e "ssh -p ${PORTA_SSH} -i ${CHAVE_SSH}" \
  site/dist/ "${DESTINO}" || falhar "o rsync não terminou"

echo "==> Verificar cabeçalhos"
curl -sI https://ciberataques.pt \
  | grep -iE 'strict-transport|content-security|x-frame|x-content|referrer' \
  || echo "AVISO: cabeçalhos de segurança não confirmados"

echo "==> Verificar que a pesquisa é servida corretamente"
tipo=$(curl -sI https://ciberataques.pt/pagefind/wasm.pt-pt.pagefind | grep -i '^content-type' || true)
echo "  ${tipo:-AVISO: wasm do Pagefind inacessível — a pesquisa vai falhar em silêncio}"

echo -e "\033[32mPublicado.\033[0m"
