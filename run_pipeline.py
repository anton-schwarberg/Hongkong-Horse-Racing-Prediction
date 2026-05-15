"""End-to-end pipeline runner.

Executes every notebook top-to-bottom in the correct order. Each notebook
reads from `data/` and writes its output back to `data/`:

    01_Combining            → data/HKHJC_FINAL.csv
    02_Preprocessing        → data/HKHJ_Dataset_Prepared.csv
    03_Feature_Engineering  → data/HKHJ_Dataset_Feature_Engineered.csv
    04_Prepare_Data         → data/HKHJ_Dataset_After_MV.parquet
    05_Modelling            → (trains model, no file output)

Usage:
    python run_pipeline.py            # run all stages
    python run_pipeline.py --from 03  # skip earlier stages
    python run_pipeline.py --only 05  # run a single stage
"""

import argparse
import subprocess
import sys
import time
from pathlib import Path

STAGES = [
    "01_Combining.ipynb",
    "02_Preprocessing.ipynb",
    "03_Feature_Engineering.ipynb",
    "04_Prepare_Data.ipynb",
    "05_Modelling.ipynb",
]


def stage_key(filename: str) -> str:
    """'01_Combining.ipynb' -> '01', '05_Modelling.ipynb' -> '05'."""
    stem = Path(filename).stem
    return stem.split("_", 1)[0] if "_" in stem else stem


def run_one(nb_dir: Path, notebook: str, timeout: int) -> None:
    nb_path = nb_dir / notebook
    print(f"\n▶ {notebook}")
    start = time.perf_counter()
    result = subprocess.run(
        [
            sys.executable, "-m", "jupyter", "nbconvert",
            "--to", "notebook",
            "--execute",
            "--inplace",
            f"--ExecutePreprocessor.timeout={timeout}",
            str(nb_path),
        ],
        check=False,
    )
    elapsed = time.perf_counter() - start
    if result.returncode != 0:
        sys.exit(f"✗ {notebook} failed after {elapsed:.1f}s")
    print(f"✓ {notebook} done in {elapsed:.1f}s")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--from", dest="start", help="stage key to start from (e.g. '03')")
    parser.add_argument("--only", help="run a single stage")
    parser.add_argument("--timeout", type=int, default=1800, help="per-cell timeout in seconds (default 1800)")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parent
    nb_dir = repo_root / "notebooks"

    stages = STAGES
    if args.only:
        stages = [s for s in STAGES if stage_key(s) == args.only]
        if not stages:
            sys.exit(f"unknown stage: {args.only}")
    elif args.start:
        keys = [stage_key(s) for s in STAGES]
        if args.start not in keys:
            sys.exit(f"unknown stage: {args.start}")
        stages = STAGES[keys.index(args.start):]

    total_start = time.perf_counter()
    for nb in stages:
        run_one(nb_dir, nb, args.timeout)
    total_elapsed = time.perf_counter() - total_start
    print(f"\nAll stages complete in {total_elapsed:.1f}s")


if __name__ == "__main__":
    main()
