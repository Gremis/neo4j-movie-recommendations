"""Compara o dataset local com o Neo4j usando somente consultas de leitura."""

import csv
import os
from collections import Counter
from pathlib import Path

from dotenv import load_dotenv
from neo4j import GraphDatabase, READ_ACCESS

try:
    from .generate_dataset import HEADERS
    from .validate_dataset import validate_dataset
except ImportError:
    from generate_dataset import HEADERS
    from validate_dataset import validate_dataset


ROOT = Path(__file__).resolve().parents[1]
ENTITIES = {
    "movies": ("Movie", "id"),
    "people": ("Person", "id"),
    "genres": ("Genre", "name"),
    "users": ("User", "id"),
}
RELATIONS = {
    "acted_in": ("people", "movies", "person_id", "movie_id", "ACTED_IN"),
    "directed": ("people", "movies", "person_id", "movie_id", "DIRECTED"),
    "movie_genres": ("movies", "genres", "movie_id", "genre_name", "IN_GENRE"),
    "ratings": ("users", "movies", "user_id", "movie_id", "RATED"),
}


def load_dataset():
    validate_dataset(ROOT / "data")
    tables = {}
    for name in HEADERS:
        with (ROOT / "data" / f"{name}.csv").open(encoding="utf-8", newline="") as stream:
            tables[name] = list(csv.DictReader(stream))
    for row in tables["movies"]:
        row["released"] = int(row["released"])
    for row in tables["ratings"]:
        row["rating"] = float(row["rating"])
    return tables


def verify(tx, tables):
    """Retorna resumos; não imprime dentro do callback sujeito a repetição."""
    summaries = []
    for name, (label, key) in ENTITIES.items():
        expected = {row[key]: row for row in tables[name]}
        # Labels e propriedades vêm apenas das constantes acima.
        query = (
            f"MATCH (n:{label}) WHERE n.{key} IN $keys "
            f"RETURN n.{key} AS key, properties(n) AS props"
        )
        actual = {}
        for record in tx.run(query, keys=list(expected)):
            actual.setdefault(record["key"], []).append(record["props"])
        missing = sum(key_value not in actual for key_value in expected)
        duplicates = sum(max(0, len(nodes) - 1) for nodes in actual.values())
        mismatches = sum(
            any(any(props.get(column) != value or type(props.get(column)) is not type(value)
                    for column, value in row.items()) for props in actual.get(key_value, []))
            for key_value, row in expected.items()
        )
        summaries.append((name, len(expected), missing, duplicates, mismatches, 0))

    for name, (source, target, source_column, target_column, relation) in RELATIONS.items():
        source_label, source_key = ENTITIES[source]
        target_label, target_key = ENTITIES[target]
        expected = {(row[source_column], row[target_column]): row for row in tables[name]}
        query = (
            f"MATCH (a:{source_label})-[r:{relation}]->(b:{target_label}) "
            f"WHERE a.{source_key} IN $sources AND b.{target_key} IN $targets "
            f"RETURN a.{source_key} AS source, b.{target_key} AS target, r.rating AS rating"
        )
        counts = Counter()
        mismatches = 0
        for record in tx.run(
            query,
            sources=[row[source_key] for row in tables[source]],
            targets=[row[target_key] for row in tables[target]],
        ):
            pair = (record["source"], record["target"])
            counts[pair] += 1
            if name == "ratings" and pair in expected:
                rating = record["rating"]
                if type(rating) not in (int, float) or rating != expected[pair]["rating"]:
                    mismatches += 1
        missing = sum(pair not in counts for pair in expected)
        duplicates = sum(count - 1 for count in counts.values())
        unexpected = sum(count for pair, count in counts.items() if pair not in expected)
        summaries.append((name, len(expected), missing, duplicates, mismatches, unexpected))
    return summaries


def main() -> int:
    try:
        tables = load_dataset()
    except (ValueError, OSError, csv.Error):
        print("Falha: dataset local inválido ou inacessível. Execute scripts/validate_dataset.py.")
        return 1

    load_dotenv(ROOT / ".env")
    required = ("NEO4J_URI", "NEO4J_USERNAME", "NEO4J_PASSWORD", "NEO4J_DATABASE")
    missing = [name for name in required if not os.getenv(name, "").strip()]
    if missing:
        print("Falha: configure as variáveis obrigatórias: " + ", ".join(missing))
        return 1
    try:
        with GraphDatabase.driver(
            os.environ["NEO4J_URI"],
            auth=(os.environ["NEO4J_USERNAME"], os.environ["NEO4J_PASSWORD"]),
        ) as driver:
            with driver.session(
                database=os.environ["NEO4J_DATABASE"], default_access_mode=READ_ACCESS
            ) as session:
                summaries = session.execute_read(verify, tables)
    except Exception:
        print("Falha na verificação: confira a configuração, a rede e as permissões de leitura.")
        return 1

    for name, expected, missing, duplicates, mismatches, unexpected in summaries:
        print(
            f"{name}: esperados={expected}, ausentes={missing}, duplicados={duplicates}, "
            f"valores divergentes={mismatches}, inesperados={unexpected}"
        )
    failed = any(any(summary[2:]) for summary in summaries)
    print("Falha: foram encontradas divergências." if failed else
          "Sucesso: entidades, propriedades, relacionamentos e notas conferem com os CSVs.")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
