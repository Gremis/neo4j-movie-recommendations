# Recomendação de Filmes com Neo4j

Projeto para explorar recomendações de filmes usando relacionamentos em um
banco de dados em grafo Neo4j.

## Configuração inicial

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

Crie um `.env` na raiz do projeto com `NEO4J_URI`, `NEO4J_USERNAME`,
`NEO4J_PASSWORD` e `NEO4J_DATABASE`. Não compartilhe esse arquivo
nem arquivos de credenciais baixados do Aura.

## Testar a conexão

Na raiz do projeto, execute:

```sh
.venv/bin/python scripts/check_connection.py
```

O teste verifica a conectividade e executa `RETURN 1 AS ok` no banco configurado,
sem criar datasets nem alterar dados. Em caso de falha, termina com código 1
sem exibir dados de autenticação.

O usuário verificou com sucesso a conexão real ao Neo4j Aura e a execução da
consulta `RETURN 1 AS ok` no banco configurado.

## Modelo

O grafo contém filmes (`Movie`), pessoas (`Person`), gêneros (`Genre`) e usuários
(`User`). Pessoas atuam e dirigem filmes; filmes pertencem a gêneros; usuários
avaliam filmes com `rating` numérico entre 0 e 5. Uma pessoa pode atuar e dirigir.

Consulte as propriedades, direções e cardinalidades em [docs/model.md](docs/model.md).

## Criar o schema

Com o `.env` configurado, execute na raiz do projeto:

```sh
.venv/bin/python scripts/create_schema.py
```

O script executa cada arquivo de `cypher/schema/` individualmente, em ordem de
nome, no banco indicado por `NEO4J_DATABASE`. Cria apenas as quatro constraints
de unicidade com `IF NOT EXISTS`, sem criar nós ou relacionamentos. As regras
de tipos, cardinalidades e intervalo de avaliação estão documentadas no modelo
e deverão ser validadas pelos fluxos de escrita de dados.

O usuário executou `scripts/create_schema.py` duas vezes no Aura, ambas com
sucesso.

## Dataset sintético

Os oito CSVs em `data/` são inteiramente fictícios, gerados localmente com a
biblioteca padrão do Python. Não foram extraídos de pessoas, filmes ou avaliações
reais. IDs e conteúdo são determinísticos, sem dependência de rede ou do Aura.
Os arquivos usam UTF-8 e o módulo `csv` preserva acentos e vírgulas nos títulos.

Execute na raiz do projeto:

```sh
.venv/bin/python scripts/generate_dataset.py
.venv/bin/python scripts/validate_dataset.py
.venv/bin/python -m unittest discover -s tests -v
```

| Arquivo | Registros (sem cabeçalho) |
| --- | ---: |
| `data/movies.csv` | 30 |
| `data/people.csv` | 20 |
| `data/genres.csv` | 8 |
| `data/users.csv` | 15 |
| `data/acted_in.csv` | 60 |
| `data/directed.csv` | 30 |
| `data/movie_genres.csv` | 45 |
| `data/ratings.csv` | 120 |

Cada filme tem dois atores distintos, um diretor e um ou dois gêneros distintos.
As mesmas pessoas podem atuar e dirigir. Cada usuário avalia oito filmes e deixa
22 sem avaliar. Três grupos de cinco usuários compartilham quatro favoritos por
grupo, com notas de 4 a 5, além de favoritos individuais que permitem recomendar
filmes ainda não avaliados pelos colegas. Duas avaliações por usuário fora do
bloco favorito recebem notas de 0 a 3.

O validador confere cabeçalhos, campos obrigatórios, chaves, referências,
duplicatas, anos inteiros, notas finitas de 0 a 5, quantidades e cobertura.
Para a cobertura colaborativa, cada usuário deve compartilhar ao menos dois
filmes com nota a partir de 4 com outro usuário e ter um favorito desse colega
ainda não avaliado.

A validação local e os cinco testes passaram. Uma segunda geração produziu
conteúdo idêntico nos oito arquivos. Os testes usam diretórios temporários e
não modificam os CSVs do projeto. Nenhum dado foi importado no Aura nesta etapa.
