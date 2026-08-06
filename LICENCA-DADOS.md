# Licença dos dados

O **registo de incidentes** deste projeto — a organização dos factos, a classificação,
os resumos e a atribuição de grau de confiança — está licenciado sob
[Creative Commons Atribuição 4.0 Internacional (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/deed.pt).

Pode copiar, redistribuir e adaptar o material, incluindo para fins comerciais, desde
que atribua a origem a **ciberataques.pt**.

## O que a licença não abrange

As **fontes citadas** não estão abrangidas: pertencem aos respetivos editores. De cada
fonte guardamos apenas título, publicador, data, ligação e, no máximo, 200 caracteres de
excerto com atribuição visível. Nunca reproduzimos o corpo dos artigos, e as exportações
de dados abertos também não o incluem.

O que licenciamos é o nosso trabalho: reunir, verificar, datar e estruturar.

## Como citar

Cada incidente tem um identificador estável que nunca muda:

```
ciberataques.pt (consultado em AAAA-MM-DD).
Registo de ciberataques em Portugal. Incidente 2022-vodafone-portugal.
https://ciberataques.pt/incidentes/2022-vodafone-portugal/
```

O **código** do projeto está sob licença MIT. Ver [LICENSE](LICENSE).

## Dados de terceiros incorporados

O mapa da página inicial usa o contorno de Portugal continental do **Natural
Earth** (`ne_50m_admin_0_countries`), que é **domínio público (CC0)** e não exige
atribuição — damo-la à mesma, porque um arquivo que insiste em saber de onde vem
cada facto não pode ser opaco quanto ao que incorpora.

A geometria foi simplificada por Douglas-Peucker e projetada em equirretangular
com correção do meridiano, e está em `site/src/lib/contorno-portugal.ts` com o
processo descrito no cabeçalho do ficheiro. Nada mais de terceiros é servido por
este site: não há tipos de letra, folhas de estilo, scripts nem imagens externas.
