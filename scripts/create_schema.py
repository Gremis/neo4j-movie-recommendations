"""Cria as constraints do schema, sem criar nós ou relacionamentos."""

import os
from pathlib import Path

from dotenv import load_dotenv
from neo4j import GraphDatabase


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    load_dotenv(root / ".env")
    required = (
        "NEO4J_URI",
        "NEO4J_USERNAME",
        "NEO4J_PASSWORD",
        "NEO4J_DATABASE",
    )
    missing = [name for name in required if not os.getenv(name, "").strip()]
    if missing:
        print("Falha: configure as variáveis obrigatórias: " + ", ".join(missing))
        return 1

    try:
        files = sorted((root / "cypher" / "schema").glob("*.cypher"))
        if not files:
            print("Falha: nenhum arquivo de schema encontrado.")
            return 1
        queries = [(path.name, path.read_text(encoding="utf-8")) for path in files]
        if any(not query.strip() for _, query in queries):
            print("Falha: há um arquivo de schema vazio.")
            return 1

        with GraphDatabase.driver(
            os.environ["NEO4J_URI"],
            auth=(os.environ["NEO4J_USERNAME"], os.environ["NEO4J_PASSWORD"]),
        ) as driver:
            for name, query in queries:
                driver.execute_query(query, database_=os.environ["NEO4J_DATABASE"])
                print(f"Schema aplicado: {name}")
    except Exception:
        # Não exibir exceções que possam incluir dados de autenticação.
        print(
            "Falha ao criar o schema. Verifique os arquivos, a configuração, "
            "a rede e as permissões no banco. Arquivos anteriores podem já "
            "ter sido aplicados; a execução pode ser repetida."
        )
        return 1

    print("Sucesso: todas as constraints do schema foram aplicadas.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
