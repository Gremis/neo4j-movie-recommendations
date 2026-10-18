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
