#!/usr/bin/env bash
#
# Recolha diária, para correr no cron do VPS.
#
#   15 6 * * *   /caminho/para/ciberataques.pt/scripts/recolha_agendada.sh
#   0  7 * * 0   /caminho/.../.venv/bin/python ingestao/instantaneo.py --verificar-fontes
#
# NÃO PUBLICA NADA. Enche a fila de candidatos, e mais nada. A promoção de um
# candidato a incidente é feita à mão com curar.py, e a publicação é um commit.
# Esta separação é a garantia estrutural de revisão humana do projeto: não há
# caminho automático entre uma notícia e o site.
#
set -uo pipefail

RAIZ="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$RAIZ"

CARIMBO="$(date -u +%Y%m%dT%H%M%SZ)"
DIR_REGISTO="data/instantaneos/registo"
mkdir -p "$DIR_REGISTO"
REGISTO="$DIR_REGISTO/${CARIMBO}.log"

exec > >(tee -a "$REGISTO") 2>&1

echo "=== recolha ${CARIMBO} ==="

# Segredos fora do repositório. Ver ingestao/extrair.py.
SEGREDOS="$HOME/.config/ciberataques/segredos.env"
[[ -f "$SEGREDOS" ]] && set -a && source "$SEGREDOS" && set +a

.venv/bin/python ingestao/recolher.py
ESTADO=$?

# Preservar as fontes citadas enquanto ainda existem.
#
# Corre a seguir à recolha e não antes: as fontes acrescentadas hoje são as que
# mais urgem arquivar, porque uma notícia recente é a que ainda ninguém preservou.
# O Save Page Now aplica limites por endereço e recusa parte dos pedidos — não é
# erro, e a passagem seguinte retoma o que ficou.
.venv/bin/python ingestao/arquivo.py --submeter || true

NOVOS=$(find data/fila/candidatos -name '*.json' 2>/dev/null | wc -l)
echo "candidatos por rever: ${NOVOS}"

# Notificação por ntfy self-hosted. Sem serviços de terceiros: o que recolhemos e
# quando o recolhemos não tem de passar por infraestrutura de mais ninguém.
if [[ -n "${NTFY_URL:-}" && "$NOVOS" -gt 0 ]]; then
  curl -s -H "Title: ciberataques.pt" \
       -d "${NOVOS} candidatos por rever" "$NTFY_URL" >/dev/null || true
fi

# Rotação: guardamos os últimos 60 registos de execução.
ls -1t "$DIR_REGISTO"/*.log 2>/dev/null | tail -n +61 | xargs -r rm --

echo "=== fim (estado ${ESTADO}) ==="
exit "$ESTADO"
