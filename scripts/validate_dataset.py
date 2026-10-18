"""Valida os CSVs locais sem carregar credenciais ou conectar a bancos."""

import csv
import math
from pathlib import Path

try:
    from .generate_dataset import DATA_DIR, HEADERS
except ImportError:
    from generate_dataset import DATA_DIR, HEADERS


def require(condition, message):
    if not condition:
        raise ValueError(message)


def validate_dataset(directory=DATA_DIR):
    tables = {}
    for name, header in HEADERS.items():
        with (Path(directory) / f"{name}.csv").open(encoding="utf-8", newline="") as stream:
            reader = csv.DictReader(stream)
            require(reader.fieldnames == list(header), f"{name}: cabeçalho inválido")
            rows = list(reader)
        for row in rows:
            require(None not in row and all(isinstance(value, str) and value.strip()
                                           for value in row.values()),
                    f"{name}: campos obrigatórios ausentes ou extras")
        tables[name] = rows

    keys = {}
    for name, count, prefix in (("movies", 30, "movie_"), ("people", 20, "person_"),
                                ("genres", 8, ""), ("users", 15, "user_")):
        column = "name" if name == "genres" else "id"
        values = [row[column] for row in tables[name]]
        require(len(values) == count, f"{name}: quantidade deve ser {count}")
        require(len(set(values)) == len(values), f"{name}: chave duplicada")
        require(all(value.startswith(prefix) and len(value) > len(prefix)
                    for value in values), f"{name}: prefixo de ID inválido")
        keys[name] = set(values)

    for row in tables["movies"]:
        try:
            int(row["released"])
        except ValueError:
            raise ValueError("movies: ano deve ser inteiro") from None

    relations = {
        "acted_in": (("person_id", "people"), ("movie_id", "movies")),
        "directed": (("person_id", "people"), ("movie_id", "movies")),
        "movie_genres": (("movie_id", "movies"), ("genre_name", "genres")),
        "ratings": (("user_id", "users"), ("movie_id", "movies")),
    }
    for name, endpoints in relations.items():
        seen = set()
        for row in tables[name]:
            pair = tuple(row[column] for column, _ in endpoints)
            require(pair not in seen, f"{name}: relacionamento duplicado")
            seen.add(pair)
            for column, target in endpoints:
                require(row[column] in keys[target], f"{name}: referência inexistente")

    for movie in keys["movies"]:
        for name, minimum, maximum in (("acted_in", 2, 20), ("directed", 1, 1),
                                       ("movie_genres", 1, 2)):
            count = sum(row["movie_id"] == movie for row in tables[name])
            require(minimum <= count <= maximum, f"{name}: cobertura inválida de filme")

    require(len(tables["ratings"]) >= 100, "ratings: mínimo de 100 avaliações")
    positive = {user: set() for user in keys["users"]}
    rated = {user: set() for user in keys["users"]}
    for row in tables["ratings"]:
        try:
            rating = float(row["rating"])
        except ValueError:
            raise ValueError("ratings: avaliação deve ser numérica") from None
        require(math.isfinite(rating) and 0 <= rating <= 5,
                "ratings: avaliação fora do intervalo ou não finita")
        rated[row["user_id"]].add(row["movie_id"])
        if rating >= 4:
            positive[row["user_id"]].add(row["movie_id"])
    for user in keys["users"]:
        require(0 < len(rated[user]) < len(keys["movies"]),
                "ratings: usuário deve ter filmes avaliados e não avaliados")
        # Cada usuário deve compartilhar ao menos dois positivos com um colega,
        # e ter ao menos um positivo desse colega ainda não avaliado.
        require(any(other != user and len(positive[user] & positive[other]) >= 2
                    and positive[other] - rated[user] for other in positive),
                "ratings: falta de cobertura colaborativa")
    return {name: len(rows) for name, rows in tables.items()}


def main():
    try:
        counts = validate_dataset()
    except (ValueError, OSError, csv.Error) as error:
        print(f"Dataset inválido: {error}")
        return 1
    print("Dataset válido.")
    for name, count in counts.items():
        print(f"{name}: {count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
