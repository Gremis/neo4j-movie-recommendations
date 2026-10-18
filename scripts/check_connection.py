"""Verifica a conexão com o Neo4j sem alterar dados."""

import os
from pathlib import Path

from dotenv import load_dotenv
from neo4j import GraphDatabase


def main() -> int:
    load_dotenv(Path(__file__).resolve().parents[1] / ".env")
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
        with GraphDatabase.driver(
            os.environ["NEO4J_URI"],
            auth=(os.environ["NEO4J_USERNAME"], os.environ["NEO4J_PASSWORD"]),
        ) as driver:
            driver.verify_connectivity()
            with driver.session(database=os.environ["NEO4J_DATABASE"]) as session:
                record = session.run("RETURN 1 AS ok").single(strict=True)
                if record["ok"] != 1:
                    print("Falha: o banco retornou um resultado inesperado.")
                    return 1
    except Exception:
        # Não exibir a exceção: ela pode conter dados de conexão.
        print(
            "Falha ao conectar ao Neo4j ou executar a consulta. "
            "Verifique a configuração, o acesso à rede e o estado da instância."
        )
        return 1

    print("Sucesso: conexão com o Neo4j verificada e consulta executada.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
