import csv
import io


def parse_csv(content):
    reader = csv.DictReader(io.StringIO(content.decode("utf-8-sig", errors="replace")))
    return [
        {key.strip(): (value or "").strip() for key, value in row.items() if key}
        for row in reader
    ]