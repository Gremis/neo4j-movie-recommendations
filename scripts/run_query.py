"""Executa apenas as consultas de negócio permitidas, em modo de leitura."""

import argparse
import json
import math
import os
from pathlib import Path

from dotenv import load_dotenv
from neo4j import GraphDatabase, READ_ACCESS


ROOT = Path(__file__).resolve().parents[1]
QUERIES = {
    "01": ("01_movies_by_genre.cypher", {"genre_name": str}),
    "02": ("02_actor_filmography.cypher", {"person_id": str}),
    "03": ("03_director_movies.cypher", {"person_id": str}),
    "04": ("04_top_rated.cypher", {"min_ratings": int}),
    "05": ("05_favorite_genres.cypher", {"user_id": str}),
    "06": ("06_genre_recommendations.cypher", {"user_id": str}),
    "07": ("07_collaborative_recommendations.cypher", {"user_id": str}),
    "08": ("08_similar_movies.cypher", {"movie_id": str}),
    "09": ("09_actor_pairs.cypher", {}),
    "10": ("10_shortest_path.cypher", {"source_id": str, "target_id": str}),
}


def validate_params(query_id, params):
    if not isinstance(params, dict):
        raise ValueError("Os parâmetros devem ser um objeto JSON.")
    schema = dict(QUERIES[query_id][1], limit=int)
    defaults = {"limit": 10}
    if query_id in ("06", "07"):
        schema["min_rating"] = float
        defaults["min_rating"] = 4
    if set(params) - set(schema):
        raise ValueError("Há parâmetros desconhecidos para esta consulta.")
    values = {**defaults, **params}
    for name, expected in schema.items():
        if name not in values:
            raise ValueError(f"Parâmetro obrigatório: {name}.")
        value = values[name]
        if expected is float:
            valid = type(value) in (int, float) and math.isfinite(value) and 0 <= value <= 5
        elif expected is int:
            valid = type(value) is int and value > 0
        else:
            valid = isinstance(value, str) and bool(value.strip())
        if not valid:
            raise ValueError(f"Tipo ou valor inválido para {name}.")
    if query_id == "10" and values["source_id"] == values["target_id"]:
        raise ValueError("Informe duas pessoas distintas.")
    return values


def read_results(tx, query, params):
    return [record.data() for record in tx.run(query, parameters=params)]


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("query_id", choices=QUERIES)
    parser.add_argument("--params", default="{}", help="Objeto JSON com os parâmetros")
    parser.add_argument("--output", type=Path, help="Arquivo de exportação JSON em UTF-8")
    args = parser.parse_args(argv)
    try:
        params = validate_params(args.query_id, json.loads(args.params))
    except (ValueError, OverflowError) as error:
        # Mensagens da validação não incluem os valores recebidos.
        if isinstance(error, json.JSONDecodeError):
            print("Falha: JSON de parâmetros inválido.")
        else:
            print(f"Falha: {error}")
        return 1
    try:
        query = (ROOT / "cypher" / "queries" / QUERIES[args.query_id][0]).read_text(encoding="utf-8")
    except OSError:
        print("Falha: arquivo de consulta inacessível.")
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
            with driver.session(database=os.environ["NEO4J_DATABASE"],
                                default_access_mode=READ_ACCESS) as session:
                results = session.execute_read(read_results, query, params)
    except Exception:
        print("Falha ao executar a consulta. Confira configuração, rede e permissões de leitura.")
        return 1
    try:
        output = json.dumps(results, ensure_ascii=False, indent=2, allow_nan=False)
        if args.output:
            args.output.write_text(output + "\n", encoding="utf-8")
        print(output)
    except (OSError, ValueError, TypeError):
        print("Falha ao serializar ou exportar os resultados.")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
