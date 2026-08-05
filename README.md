# ciberataques.pt

Registo público e documentado dos ciberataques a entidades portuguesas.

Cada incidente indica as fontes que o sustentam e distingue explicitamente o que a
entidade confirmou do que apenas o atacante alegou. Para cidadãos, jornalistas e
investigadores.

## Porque existe

Esta informação não estava reunida em lado nenhum. Os trackers internacionais cobrem
ransomware com site de extorsão e falham tudo o resto, incluindo os casos maiores em
Portugal. Os relatórios oficiais publicam estatística agregada e nunca nomeiam
entidades. A imprensa cobre caso a caso e segue em frente. Faltava o arquivo.

## Como está organizado

```
referencia/     A autoridade: esquema, taxonomia, entidades, fontes. Ler primeiro.
ingestao/       Pipeline. rede.py é o único ponto de saída para a internet.
data/fila/      Candidatos por rever e rejeitados. Versionado.
data/out/       O registo canónico. Um ficheiro JSON por incidente, versionado.
site/           Astro 7 + Tailwind v4. Lê data/out em tempo de compilação.
testes/         Validação do esquema, das invariantes editoriais e da rede.
deploy/         nginx e o guião de publicação.
```

O caminho de um facto até ao site:

```
fontes  →  triagem  →  dedup  →  extração  →  FILA  ⟂  curadoria  →  commit  →  site
        determinística        modelo LLM              humana
```

O símbolo ⟂ é onde o automatismo para. Não há caminho automático entre uma notícia e
o site: `ingestao/recolher.py` termina na fila e nunca escreve em `data/out`.

O ficheiro mais importante do repositório não é código: é
[POLITICA-EDITORIAL.md](POLITICA-EDITORIAL.md). Manda no resto.

## Três invariantes

1. **O pipeline nunca publica.** Produz candidatos; um humano promove. A publicação é
   um commit.
2. **Nenhum modelo de linguagem escreve o grau de confiança.** É derivado em código a
   partir dos tipos de fonte. O texto analisado é, no caso dos sites de extorsão,
   escrito por adversários.
3. **Uma notícia é uma fonte dentro de um incidente, nunca uma página.** Cinco notícias
   sobre o mesmo ataque produzem um incidente com cinco fontes.

## Trabalhar no projeto

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
cd site && npm install && cd ..

python atualizar.py                     # valida, reconstrói índices, verifica integridade
python atualizar.py --site              # + build do Astro e índice de pesquisa
python atualizar.py --recolher          # + vai à rede encher a fila (não publica)
python atualizar.py --recolher --sem-llm  # recolhe sem gastar tokens
python curar.py                         # rever a fila e promover candidatos
python curar.py --resumo                # só ver o que está por rever
.venv/bin/python -m pytest              # só a validação
```

Pré-visualizar: `cd site && npx astro preview`.

Verificar ligações citadas (semanal, no cron):
`.venv/bin/python ingestao/instantaneo.py --verificar-fontes`. Distingue três estados:
`revisto` (o artigo mudou desde que o citámos), `MORREU` (404 ou 410) e
`nao_verificavel` (o servidor recusa automatismos, como faz o Público, o que **não**
é uma ligação morta).

Preservar as fontes: `.venv/bin/python ingestao/arquivo.py --submeter` procura cópias
no Internet Archive e pede o arquivamento das que não existem. Corre no cron diário,
a seguir à recolha, porque as fontes de hoje são as que ainda ninguém preservou. Cada
ficha oferece ainda uma ligação de pesquisa no Arquivo.pt, que é gerada e nunca
consultada — o `robots.txt` deles proíbe raspagem de `/wayback`, e um `robots.txt`
regula raspagem, não hiperligações. Ver `referencia/NOTAS.md`.

O modelo corre via OpenRouter. A chave vai em `~/.config/ciberataques/segredos.env`
como `OPENROUTER_API_KEY`; o modelo escolhe-se em `LLM_MODELO` e o teto diário de
custo em `MAX_CANDIDATOS_DIA`. Sem chave, a recolha e a triagem funcionam na mesma e
os candidatos ficam por extrair.

### Acrescentar um incidente

1. Escrever `data/out/incidentes/<ano>-<entidade-slug>.json` contra
   `referencia/esquema-incidente.json`.
2. Se a entidade for nova, acrescentá-la a `referencia/entidades.yaml`, com as `chaves`
   por que aparece nas notícias — é o que faz "MEO" encontrar a Altice.
3. `python atualizar.py`. Os testes recusam factos sem fonte, estados de confirmação
   que as fontes não sustentam, excertos acima de 200 caracteres e ligações a `.onion`.
4. Rever o `git diff` e fazer commit. **O commit é a revisão editorial.**

Antes de investigar um caso, ler [referencia/NOTAS.md](referencia/NOTAS.md): já lá está
o que foi verificado e não passou.

## Publicar

`./deploy/publicar.sh` constrói, valida e faz rsync para o VPS. Recusa publicar se
houver alterações não comprometidas no registo.

## Licenças

Registo de incidentes sob **CC BY 4.0**. Código sob **MIT**. As fontes citadas
pertencem aos respetivos editores: guardamos título, publicador, data, ligação e no
máximo 200 caracteres de excerto, nunca o corpo dos artigos.
