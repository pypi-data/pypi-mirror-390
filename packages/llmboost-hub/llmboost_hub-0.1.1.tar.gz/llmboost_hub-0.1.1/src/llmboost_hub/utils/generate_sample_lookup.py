#!/usr/bin/env python3
import argparse
import os
import re
from itertools import product, islice
from typing import Iterable, List

import pandas as pd


def _infer_backend(gpu: str) -> str:
    """
    Infer the docker backend from a GPU family string.

    Rules:
        - AMD families starting with 'MI' -> 'rocm'
        - otherwise -> 'cuda'

    Args:
        gpu: GPU family label (e.g., 'A100', 'MI300X').

    Returns:
        'rocm' or 'cuda'.
    """
    return "rocm" if re.match(r"^MI", gpu, re.IGNORECASE) else "cuda"


def _default_models() -> List[str]:
    """Return a small pool of representative model ids for sampling."""
    return [
        "llama2-7b",
        "llama2-13b",
        "mistral-7b",
        "mixtral-8x7b",
        "gemma-2b",
        "gemma-7b",
    ]


def _default_gpus() -> List[str]:
    """Return a small set of common GPU family labels."""
    return ["A100", "A10", "RTX4090", "V100", "T4", "MI300X", "MI250"]


def _cycle_version(i: int, versions: List[str]) -> str:
    """Return the version at i modulo the number of given versions."""
    return versions[i % len(versions)]


def generate_df(rows: int, repo: str, versions: List[str]) -> pd.DataFrame:
    """
    Generate a sample lookup DataFrame with columns: model, gpu, docker_image.

    The docker_image naming convention produced:
        <repo>/mb-llmboost-<rocm|cuda>:<version>

    Args:
        rows: Maximum number of rows to generate (cartesian product is truncated).
        repo: Docker repository name (e.g., 'mangollm').
        versions: Versions to cycle through across generated rows.

    Returns:
        A pandas DataFrame with fields: model, gpu, docker_image.
    """
    models = _default_models()
    gpus = _default_gpus()

    # Cartesian product in stable order; truncate to the requested number of rows
    combos: Iterable = islice(product(models, gpus), rows)

    records = []
    for i, (model, gpu) in enumerate(combos):
        backend = _infer_backend(gpu)
        version = _cycle_version(i, versions)
        docker_image = f"{repo}/mb-llmboost-{backend}:{version}"
        records.append({"model": model, "gpu": gpu, "docker_image": docker_image})

    return pd.DataFrame.from_records(records, columns=["model", "gpu", "docker_image"])


def main():
    """
    CLI entrypoint to generate sample CSV/JSON lookup files.

    Flags:
        --csv, --json, --rows, --repo, --versions
    """
    parser = argparse.ArgumentParser(
        description="Generate sample LLMBoost lookup data (CSV/JSON) with columns: model,gpu,docker_image"
    )
    parser.add_argument("--csv", type=str, default="lookup_sample.csv", help="Output CSV file path")
    parser.add_argument(
        "--json", type=str, default="lookup_sample.json", help="Output JSON file path"
    )
    parser.add_argument(
        "--rows",
        type=int,
        default=15,
        help="Number of rows to generate (default: 15). Rows are sampled from the cartesian product.",
    )
    parser.add_argument(
        "--repo", type=str, default="mangollm", help="Docker repo (default: mangollm)"
    )
    parser.add_argument(
        "--versions",
        type=str,
        default="1.1.0,1.1.1,1.2.0",
        help="Comma-separated list of versions to cycle through (default: 1.1.0,1.1.1,1.2.0)",
    )

    args = parser.parse_args()
    versions = [v.strip() for v in args.versions.split(",") if v.strip()]
    if not versions:
        # Default to a single version if the list is empty after parsing
        versions = ["1.1.0"]

    df = generate_df(rows=args.rows, repo=args.repo, versions=versions)

    # Ensure output directories exist (support relative or bare filenames)
    os.makedirs(os.path.dirname(os.path.abspath(args.csv)) or ".", exist_ok=True)
    os.makedirs(os.path.dirname(os.path.abspath(args.json)) or ".", exist_ok=True)

    # Write outputs
    df.to_csv(args.csv, index=False)
    df.to_json(args.json, orient="records")

    print(f"Wrote CSV:  {os.path.abspath(args.csv)}")
    print(f"Wrote JSON: {os.path.abspath(args.json)}")


if __name__ == "__main__":
    main()
