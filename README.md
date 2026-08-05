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
referencia/     A autoridade: esquema, taxonomia, entidades. Ler primeiro.
ingestao/       Pipeline Python. Não vai à rede em condições normais.
data/out/       O registo canónico. Um ficheiro JSON por incidente, versionado.
site/           Astro 7 + Tailwind v4. Lê data/out em tempo de compilação.
testes/         Validação do esquema e das invariantes editoriais.
deploy/         nginx e o guião de publicação.
```

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

python atualizar.py          # valida e reconstrói os índices
python atualizar.py --site   # + build do Astro e índice de pesquisa
.venv/bin/python -m pytest   # só a validação
```

Pré-visualizar: `cd site && npx astro preview`.

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
