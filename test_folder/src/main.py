import argparse
import json
from pathlib import Path

from .pipeline import run_pipeline


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--manifest", required=True)
    p.add_argument("--images", required=True)
    p.add_argument("--output", default="results.json")
    return p.parse_args()


def main():
    args = parse_args()
    results = run_pipeline(Path(args.manifest), Path(args.images))
    Path(args.output).write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {len(results)} docs -> {args.output}")


if __name__ == "__main__":
    main()
