"""Gera dados inteiramente fictícios e determinísticos, sem acesso à rede."""

import csv
from pathlib import Path


DATA_DIR = Path(__file__).resolve().parents[1] / "data"
HEADERS = {
    "movies": ("id", "title", "released"),
    "people": ("id", "name"),
    "genres": ("name",),
    "users": ("id", "name"),
    "acted_in": ("person_id", "movie_id"),
    "directed": ("person_id", "movie_id"),
    "movie_genres": ("movie_id", "genre_name"),
    "ratings": ("user_id", "movie_id", "rating"),
}


def generate_dataset(directory=DATA_DIR):
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    genres = ["Aventura", "Comédia", "Drama", "Fantasia", "Ficção científica",
              "Mistério", "Animação", "Romance"]
    places = ["Aurora", "Névoa", "Maré", "Órbita", "Memória", "Floresta"]
    rows = {name: [] for name in HEADERS}
    rows["genres"] = [(name,) for name in genres]
    rows["people"] = [(f"person_{i:03d}", f"Pessoa Fictícia {i:02d}")
                      for i in range(1, 21)]
    rows["users"] = [(f"user_{i:03d}", f"Usuário Fictício {i:02d}")
                     for i in range(1, 16)]
    for i in range(30):
        movie = f"movie_{i + 1:03d}"
        rows["movies"].append((movie, f"Crônicas de {places[i % 6]}, capítulo {i + 1}",
                               1995 + i))
        rows["acted_in"].extend((f"person_{actor + 1:03d}", movie)
                                for actor in (i % 20, (i + 7) % 20))
        rows["directed"].append((f"person_{(i + 3) % 20 + 1:03d}", movie))
        rows["movie_genres"].append((movie, genres[(i // 10 * 2) % 8]))
        if i % 2 == 0:
            rows["movie_genres"].append((movie, genres[(i // 2 + 1) % 8]
                                         if (i // 2 + 1) % 8 != (i // 10 * 2) % 8
                                         else genres[(i // 2 + 2) % 8]))

    # Três grupos de cinco usuários. Cada grupo gosta de um bloco de dez filmes.
    # Todos compartilham quatro favoritos; cada usuário avalia outros dois filmes
    # do bloco e dois de outro bloco. Sobram favoritos de colegas para recomendar.
    for i in range(15):
        group, member = divmod(i, 5)
        favorites = [group * 10 + j for j in range(4)]
        favorites += [group * 10 + 4 + member, group * 10 + 4 + (member + 1) % 6]
        for j in favorites:
            rows["ratings"].append((f"user_{i + 1:03d}", f"movie_{j + 1:03d}",
                                    4.0 + ((i + j) % 3) * 0.5))
        for offset in range(2):
            j = ((group + 1) % 3) * 10 + (member + offset) % 10
            rows["ratings"].append((f"user_{i + 1:03d}", f"movie_{j + 1:03d}",
                                    float((i + offset) % 4)))

    for name, header in HEADERS.items():
        with (directory / f"{name}.csv").open("w", encoding="utf-8", newline="") as stream:
            writer = csv.writer(stream, lineterminator="\n")
            writer.writerow(header)
            writer.writerows(rows[name])
    return {name: len(values) for name, values in rows.items()}


if __name__ == "__main__":
    for name, count in generate_dataset().items():
        print(f"{name}: {count}")
