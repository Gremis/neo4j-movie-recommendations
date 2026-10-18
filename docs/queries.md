# Consultas de negócio

As consultas são somente de leitura, sem APOC. Execute os comandos abaixo na raiz
do projeto, com `.env`, schema e dataset já carregados. Os exemplos usam chaves
e nomes dos CSVs locais e foram escolhidos para encontrar dados nesse dataset.
As dez consultas foram executadas com sucesso no terminal local do usuário.
As contagens e a inspeção local dos JSONs estão registradas ao final desta
documentação.

O executor aceita somente os identificadores `01` a `10` e os parâmetros
documentados. `limit` é um inteiro positivo, padrão 10, em todas as consultas.
Strings obrigatórias devem ser não vazias. Parâmetros desconhecidos são rejeitados.
Nas consultas 06 e 07, `min_rating` é numérico, finito, entre 0 e 5, padrão 4.
Para executar os arquivos diretamente em outro cliente, forneça também os
parâmetros que recebem valores padrão no executor Python.

## 01 — Filmes de um gênero

Pergunta: quais filmes pertencem ao gênero escolhido? Filtra por `genre_name` e
retorna filmes distintos, ordenados por título e ID. `Aventura` existe nos CSVs
e está associado aos filmes do primeiro bloco.

```sh
.venv/bin/python scripts/run_query.py 01 --params '{"genre_name":"Aventura","limit":10}'
```

## 02 — Filmografia de um ator

Pergunta: em quais filmes uma pessoa atuou? Usa `person_id` e apenas `ACTED_IN`,
com filmes distintos ordenados por ano e ID. `person_001` aparece no elenco local.

```sh
.venv/bin/python scripts/run_query.py 02 --params '{"person_id":"person_001","limit":10}'
```

## 03 — Filmes de um diretor

Pergunta: quais filmes uma pessoa dirigiu? Usa `person_id` e apenas `DIRECTED`,
ordenando por ano e ID. `person_004` dirige `movie_001` nos CSVs.

```sh
.venv/bin/python scripts/run_query.py 03 --params '{"person_id":"person_004","limit":10}'
```

## 04 — Filmes mais bem avaliados

Pergunta: quais filmes têm maior média e ao menos `min_ratings` avaliações?
Esse parâmetro é um inteiro positivo obrigatório. Primeiro agrega por usuário e
filme, depois calcula a média e conta usuários. Não há junção com gêneros ou
elenco. Desempata pela quantidade de avaliações e pelo ID. O mínimo 3 permite
incluir os favoritos compartilhados dos grupos do dataset.

```sh
.venv/bin/python scripts/run_query.py 04 --params '{"min_ratings":3,"limit":10}'
```

## 05 — Gêneros favoritos de um usuário

Pergunta: quais gêneros recebem as maiores médias deste usuário? Usa `user_id`.
Cada filme avaliado contribui uma vez para cada um dos seus gêneros. Retorna a
média e a quantidade de filmes avaliados por gênero, ordenando por média,
quantidade e nome. Considera todas as notas, inclusive as baixas; um filme com
dois gêneros contribui para ambos. `user_001` possui oito avaliações locais.

```sh
.venv/bin/python scripts/run_query.py 05 --params '{"user_id":"user_001","limit":8}'
```

## 06 — Recomendações por gêneros favoritos

Pergunta: quais filmes ainda não avaliados combinam com os gêneros preferidos
do usuário? Usa `user_id` e `min_rating`. Calcula a média de todas as avaliações
do usuário por gênero e seleciona os gêneros cuja média atinge o limiar.

A pontuação `score` é a soma dessas médias para os gêneros distintos que o
candidato compartilha com os favoritos do usuário. Assim, dois gêneros compatíveis
podem superar um único gênero com média maior. `matched_genres` mostra quantos
gêneros contribuíram. Não usa a média global do candidato. Ordena por pontuação,
quantidade de gêneros e ID. Exclui todos os filmes já avaliados, qualquer que
seja a nota. `user_001` tem notas positivas em Aventura e filmes desse gênero
ainda não avaliados no dataset local.

```sh
.venv/bin/python scripts/run_query.py 06 --params '{"user_id":"user_001","min_rating":4,"limit":10}'
```

## 07 — Recomendações colaborativas

Pergunta: quais favoritos de pessoas com gostos em comum o usuário ainda não
avaliou? Usa `user_id` e `min_rating`. Um colega é elegível quando ambos deram
nota a partir do limiar a pelo menos um mesmo filme.

Para cada colega, conta filmes positivos distintos em comum (`shared_positive`).
Cada candidato deve ter avaliação positiva desse colega e nenhuma avaliação do
usuário-alvo. A pontuação `score` soma `shared_positive` dos colegas que apoiam
o candidato, uma vez por colega e candidato. `supporting_users` conta esses
colegas e `average_peer_rating` é a média das suas notas para o candidato.
Desempates usam esses dois valores, nessa ordem, e depois o ID. A agregação dos
filmes em comum ocorre antes de buscar candidatos, evitando multiplicar votos.
O grupo de `user_001` compartilha quatro favoritos e possui outros favoritos
não avaliados por todos, oferecendo candidatos para este exemplo.

```sh
.venv/bin/python scripts/run_query.py 07 --params '{"user_id":"user_001","min_rating":4,"limit":10}'
```

## 08 — Filmes semelhantes

Pergunta: quais filmes compartilham mais gêneros com um filme? Usa `movie_id`,
exclui o próprio filme e conta gêneros distintos compartilhados. Desempata pelo
ID. `movie_001` compartilha Aventura com outros filmes do primeiro bloco.

```sh
.venv/bin/python scripts/run_query.py 08 --params '{"movie_id":"movie_001","limit":10}'
```

## 09 — Pares de atores

Pergunta: quais pares atuaram juntos no maior número de filmes? Usa a condição
`a.id < b.id` para excluir pares invertidos e a mesma pessoa nos dois lados.
Conta filmes distintos e desempata pelos dois IDs. O dataset contém pares que
se repetem em diferentes filmes. Apenas `limit` é aceito como parâmetro.

```sh
.venv/bin/python scripts/run_query.py 09 --params '{"limit":10}'
```

## 10 — Caminho mais curto entre pessoas

Pergunta: como duas pessoas se conectam por atuação e direção? Recebe `source_id`
e `target_id`, strings distintas. Percorre exclusivamente `ACTED_IN` e `DIRECTED`
nos dois sentidos, com limite fixo de 10 saltos. Busca todos os caminhos mínimos
para ordenar empates pelas listas de IDs e tipos de relacionamento antes de
aplicar `limit`. Sem caminho nesse limite, retorna uma lista vazia.

Retorna `nodes`, uma lista de mapas com `id`, `name` e `title` (a propriedade
inaplicável é nula), `relationship_types` na ordem do percurso e `hops`.
Não retorna objetos Neo4j `Node` ou `Path`. `person_001` e `person_008` atuam
juntas em `movie_001` nos CSVs, oferecendo uma conexão para o exemplo.

```sh
.venv/bin/python scripts/run_query.py 10 --params '{"source_id":"person_001","target_id":"person_008","limit":1}'
```

## Exportação JSON

Todas as consultas imprimem um array JSON com os resultados. A opção `--output`
também grava o mesmo conteúdo em UTF-8, preservando acentos. O diretório de
destino precisa existir; um arquivo existente nesse caminho será substituído.

```sh
.venv/bin/python scripts/run_query.py 07 --params '{"user_id":"user_001","min_rating":4,"limit":10}' --output /tmp/recomendacoes.json
```

IDs e limites tornam os desempates determinísticos para o modelo validado.
As consultas consideram os labels do modelo no banco selecionado; não filtram
por prefixo de projeto caso outros dados compartilhem esses labels.

## Tentativa de validação pelo Codex em 18/10/2026

Foi executado neste ambiente o comando:

```sh
mkdir -p docs/results
.venv/bin/python scripts/run_query.py 01 --params '{"genre_name":"Aventura","limit":10}' --output docs/results/01-filmes-por-genero.json
```

O executor retornou código 1 e a mensagem: "Falha ao executar a consulta.
Confira configuração, rede e permissões de leitura." Não há diagnóstico
detalhado da exceção, portanto não foi possível determinar a causa neste
ambiente. As tentativas foram interrompidas após essa falha, conforme solicitado.

Nenhum resultado JSON foi exportado nesta tentativa. As consultas 02 a 10 não
foram executadas pelo Codex nessa tentativa; naquele momento, a comparação dos
resultados com os CSVs e a verificação das recomendações ficaram pendentes.
A evidência anterior da consulta 01
no README foi fornecida pelo usuário e não representa sucesso desta tentativa.

Para continuar localmente, execute o comando acima na raiz do projeto. Os
comandos das demais consultas estão nas respectivas seções; acrescente
`--output docs/results/02-filmografia-ator.json`, por exemplo, para preservar
cada resultado em seu próprio arquivo.

## Sucesso da consulta 01 no terminal do usuário

Após a tentativa do Codex, o usuário informou ter executado com sucesso no seu
terminal local a consulta 01, com os mesmos parâmetros e comando de exportação
acima. Foram retornados 10 filmes e exportado o arquivo
`docs/results/01-filmes-por-genero.json`. Esse sucesso é distinto da tentativa
anterior neste ambiente, cuja causa da falha não foi determinada.

## Executar os dez exemplos localmente

```sh
.venv/bin/python scripts/run_all_queries.py
```

O script executa os mesmos parâmetros de exemplo das seções 01 a 10, em ordem,
reutilizando o executor e as validações de `run_query.py`. Cria `docs/results/`
se necessário e exporta um JSON por consulta, com prefixos `01` a `10`.
Arquivos de resultados existentes com os mesmos nomes são substituídos em caso
de sucesso; uma falha não torna arquivos antigos evidência da execução atual.

O terminal mostra identificador e quantidade de resultados de cada consulta.
Na primeira falha, identifica a consulta, mostra uma mensagem sem credenciais
e encerra com código 1. As exportações já concluídas permanecem disponíveis.
Todas as consultas são de leitura; o script não modifica o banco. O Codex não
executou esse script contra o Aura; a execução foi realizada pelo usuário.

## Execução completa pelo usuário e inspeção dos arquivos

O usuário informou ter executado `.venv/bin/python scripts/run_all_queries.py`
com sucesso no terminal local. Separadamente, o Codex inspecionou os dez JSONs
em `docs/results/`, sem conectar ao Aura: todos são listas válidas de objetos,
com contagens iguais às informadas pelo usuário.

| Consulta | Resultados no JSON |
| --- | ---: |
| 01 — Filmes por gênero | 10 |
| 02 — Filmografia de ator | 3 |
| 03 — Filmes de diretor | 2 |
| 04 — Filmes mais bem avaliados | 10 |
| 05 — Gêneros favoritos | 5 |
| 06 — Recomendações por gênero | 8 |
| 07 — Recomendações colaborativas | 4 |
| 08 — Filmes semelhantes | 10 |
| 09 — Pares de atores | 10 |
| 10 — Caminho mais curto | 1 |

Os parâmetros das consultas 06 e 07 em `run_all_queries.py` correspondem aos
exemplos documentados: `user_id="user_001"`, `min_rating=4`, `limit=10`.
Os arquivos JSON contêm os resultados, não um registro próprio dos parâmetros;
essa conferência usa a configuração do executor informado pelo usuário.

A comparação dos IDs recomendados com `data/ratings.csv` e `data/movies.csv`
confirmou, nas duas listas:

- Nenhum filme já avaliado por `user_001`, independentemente da nota.
- Nenhum ID repetido dentro de cada lista.
- Todos os IDs existem no catálogo local de filmes.

A consulta 06 contém `movie_007`, `movie_008`, `movie_009`, `movie_010`,
`movie_015`, `movie_019`, `movie_021` e `movie_017`. A consulta 07 contém
`movie_007`, `movie_009`, `movie_008` e `movie_010`, nessa ordem nos JSONs.
A presença de filmes em ambas as listas é permitida; a unicidade foi verificada
separadamente em cada uma. Nenhuma inconsistência foi encontrada nesta revisão.
