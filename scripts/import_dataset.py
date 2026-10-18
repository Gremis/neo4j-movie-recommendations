"""Importa CSVs locais validados em uma única transação gerenciada."""

import csv
import os
from pathlib import Path

from dotenv import load_dotenv
from neo4j import GraphDatabase

try:
    from .validate_dataset import validate_dataset
except ImportError:
    from validate_dataset import validate_dataset


ROOT = Path(__file__).resolve().parents[1]
IMPORTS = (
    ("movies", "01_movies.cypher"),
    ("people", "02_people.cypher"),
    ("genres", "03_genres.cypher"),
    ("users", "04_users.cypher"),
    ("acted_in", "05_acted_in.cypher"),
    ("directed", "06_directed.cypher"),
    ("movie_genres", "07_movie_genres.cypher"),
    ("ratings", "08_ratings.cypher"),
)


def prepare_import(root=ROOT):
    """Valida todo o dataset e prepara consultas e parâmetros antes da escrita."""
    data = root / "data"
    validate_dataset(data)
    batches = []
    for name, filename in IMPORTS:
        with (data / f"{name}.csv").open(encoding="utf-8", newline="") as stream:
            rows = list(csv.DictReader(stream))
        if name == "movies":
            for row in rows:
                row["released"] = int(row["released"])
        elif name == "ratings":
            for row in rows:
                row["rating"] = float(row["rating"])
        query = (root / "cypher" / "import" / filename).read_text(encoding="utf-8")
        if not query.strip():
            raise ValueError("Arquivo de importação vazio")
        batches.append((query, rows))
    return batches


def import_batches(tx, batches):
    # O callback pode ser repetido pelo driver. Não emitir mensagens aqui.
    for query, rows in batches:
        tx.run(query, rows=rows).consume()


def main() -> int:
    try:
        batches = prepare_import()
    except (ValueError, OSError, csv.Error):
        print(
            "Falha: dataset inválido ou arquivos locais de importação inacessíveis. "
            "Execute scripts/validate_dataset.py e confira cypher/import/."
        )
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
            with driver.session(database=os.environ["NEO4J_DATABASE"]) as session:
                session.execute_write(import_batches, batches)
    except Exception:
        # Não exibir exceções que possam incluir dados de autenticação.
        print(
            "Falha na importação. Verifique a configuração, a rede, as permissões "
            "e o schema. A carga é transacional e pode ser repetida."
        )
        return 1

    print("Sucesso: transação de importação do dataset confirmada.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
