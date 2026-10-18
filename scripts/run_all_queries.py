"""Executa os dez exemplos de leitura e exporta seus resultados reais."""

import io
import json
from contextlib import redirect_stdout

try:
    from .run_query import ROOT, main as run_query, validate_params
except ImportError:
    from run_query import ROOT, main as run_query, validate_params


EXAMPLES = (
    ("01", {"genre_name": "Aventura", "limit": 10}, "01-filmes-por-genero.json"),
    ("02", {"person_id": "person_001", "limit": 10}, "02-filmografia-ator.json"),
    ("03", {"person_id": "person_004", "limit": 10}, "03-filmes-diretor.json"),
    ("04", {"min_ratings": 3, "limit": 10}, "04-melhores-avaliados.json"),
    ("05", {"user_id": "user_001", "limit": 8}, "05-generos-favoritos.json"),
    ("06", {"user_id": "user_001", "min_rating": 4, "limit": 10}, "06-recomendacoes-generos.json"),
    ("07", {"user_id": "user_001", "min_rating": 4, "limit": 10}, "07-recomendacoes-colaborativas.json"),
    ("08", {"movie_id": "movie_001", "limit": 10}, "08-filmes-semelhantes.json"),
    ("09", {"limit": 10}, "09-pares-atores.json"),
    ("10", {"source_id": "person_001", "target_id": "person_008", "limit": 1},
     "10-caminho-mais-curto.json"),
)


def main():
    directory = ROOT / "docs" / "results"
    try:
        directory.mkdir(parents=True, exist_ok=True)
    except OSError:
        print("Falha: não foi possível preparar docs/results/ para a consulta 01.")
        return 1

    print("Consulta | Quantidade de resultados")
    for query_id, params, filename in EXAMPLES:
        try:
            validate_params(query_id, params)
        except ValueError as error:
            print(f"Consulta {query_id}: {error}")
            return 1
        captured = io.StringIO()
        try:
            # Reutiliza integralmente conexão, leitura, validações e exportação.
            with redirect_stdout(captured):
                code = run_query([
                    query_id, "--params", json.dumps(params, ensure_ascii=False),
                    "--output", str(directory / filename),
                ])
        except Exception:
            # Não expor exceções inesperadas que possam incluir autenticação.
            print(f"Consulta {query_id}: falha inesperada no executor; execução interrompida.")
            return 1
        if code != 0:
            # O executor fornece mensagens sanitizadas, sem valores de conexão.
            print(f"Consulta {query_id}: {captured.getvalue().strip()}")
            return 1
        try:
            results = json.loads(captured.getvalue())
            if not isinstance(results, list):
                raise ValueError("Resultado não é uma lista")
        except ValueError:
            print(f"Consulta {query_id}: formato de resultado inválido; execução interrompida.")
            return 1
        print(f"{query_id} | {len(results)}")
    print("Sucesso: dez consultas concluídas; JSONs exportados em docs/results/.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
