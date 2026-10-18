import csv
import tempfile
import unittest
from pathlib import Path

from scripts.generate_dataset import generate_dataset
from scripts.validate_dataset import validate_dataset


class DatasetTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name)
        generate_dataset(self.directory)

    def change_ratings(self, transform):
        path = self.directory / "ratings.csv"
        with path.open(encoding="utf-8", newline="") as stream:
            reader = csv.DictReader(stream)
            header = reader.fieldnames
            rows = list(reader)
        transform(rows)
        with path.open("w", encoding="utf-8", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=header)
            writer.writeheader()
            writer.writerows(rows)

    def test_valid_dataset(self):
        self.assertEqual(validate_dataset(self.directory)["ratings"], 120)

    def test_missing_reference(self):
        self.change_ratings(lambda rows: rows[0].update(movie_id="movie_missing"))
        with self.assertRaisesRegex(ValueError, "referência inexistente"):
            validate_dataset(self.directory)

    def test_duplicate_rating(self):
        self.change_ratings(lambda rows: rows.append(dict(rows[0])))
        with self.assertRaisesRegex(ValueError, "relacionamento duplicado"):
            validate_dataset(self.directory)

    def test_invalid_rating(self):
        for value in ("-0.1", "5.1", "nan", "inf"):
            with self.subTest(value=value):
                self.change_ratings(lambda rows: rows[0].update(rating=value))
                with self.assertRaisesRegex(ValueError, "fora do intervalo"):
                    validate_dataset(self.directory)

    def test_deterministic_generation(self):
        before = {path.name: path.read_bytes() for path in self.directory.glob("*.csv")}
        generate_dataset(self.directory)
        after = {path.name: path.read_bytes() for path in self.directory.glob("*.csv")}
        self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()
