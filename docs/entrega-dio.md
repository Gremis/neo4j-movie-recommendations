# Descrição para entrega na DIO

Projeto de recomendação de filmes com Neo4j Aura, Python e Cypher. Modela filmes,
pessoas, gêneros e usuários, com relações de atuação, direção e avaliações.
Utiliza um dataset sintético de 30 filmes e 120 avaliações, com geração
determinística, validação de integridade, carga idempotente e verificação dos
dados importados.

Inclui dez consultas de negócio, recomendações por gêneros e por favoritos em
comum, resultados JSON e imagens do grafo. As consultas foram executadas com
sucesso pelo usuário no terminal local. A documentação explica a reprodução e
as limitações: dados fictícios e pequenos, regras em Cypher, sem API ou interface
própria.
