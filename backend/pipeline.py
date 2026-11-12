"""Runs fetch -> clean -> charts in one go."""
import json
from pathlib import Path

import fetch_data, clean_data, charts

META_FILE = Path(__file__).resolve().parent.parent / "data" / "clean" / "meta.json"


def run_pipeline():
    _, source = fetch_data.get_raw_data()
    df, report = clean_data.run()
    report["source"] = source
    report["charts"] = charts.make_all(df)
    META_FILE.write_text(json.dumps(report, indent=2))
    return report


if __name__ == "__main__":
    print(json.dumps(run_pipeline(), indent=2))
