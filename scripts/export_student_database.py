"""Export the four Annex C student tables from an existing team database, without modifying it."""
import argparse
import csv
import sqlite3
from pathlib import Path
from scripts.load_students import TABLES


def export(database, output):
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(Path(database).resolve().as_uri() + "?mode=ro", uri=True) as connection:
        for table, columns in TABLES.items():
            with (output / f"{table}.csv").open("w", newline="", encoding="utf-8") as handle:
                writer = csv.writer(handle)
                writer.writerow(columns)
                writer.writerows(connection.execute(f"SELECT {','.join(columns)} FROM {table}"))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--database", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    export(args.database, args.output)
