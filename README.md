# Hong Kong Horse Racing Prediction

An end-to-end machine learning project to forecast Hong Kong horse race
outcomes. It starts by scraping historical race results from the official HKJC
website, then cleans and enriches the data. With the prepared dataset, it
trains and evaluates ML models to estimate win/place probabilities and rank
runners, using time-based splits to avoid look-ahead bias and metrics such as
log loss, Brier score, AUC, and race-level top-k hit rate.

## Pipeline

The full data flow is split across five notebooks in `notebooks/`. Each stage
reads from `data/` and writes its output back to `data/`:

| Stage | Notebook | Input | Output |
|-------|----------|-------|--------|
| 1 | `01_Combining.ipynb` | `data/HKHJC_{2009..2025}.csv` | `data/HKHJC_FINAL.csv` |
| 2 | `02_Preprocessing.ipynb` | `HKHJC_FINAL.csv` | `data/HKHJ_Dataset_Prepared.csv` |
| 3 | `03_Feature_Engineering.ipynb` | `HKHJ_Dataset_Prepared.csv` | `data/HKHJ_Dataset_Feature_Engineered.csv` |
| 4 | `04_Prepare_Data.ipynb` | `HKHJ_Dataset_Feature_Engineered.csv` | `data/HKHJ_Dataset_After_MV.parquet` |
| 5 | `05_Modelling.ipynb` | `HKHJ_Dataset_After_MV.parquet` | (model evaluation) |

Mappings (location, going, race class) and other shared code live in `src/`.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

On macOS, LightGBM also needs the OpenMP runtime:

```bash
brew install libomp
```

The yearly raw CSVs (`data/HKHJC_YYYY.csv`) are produced by `src/01_Webscraper.py`.

## Running the full pipeline

```bash
python run_pipeline.py            # all five stages, ~5 min on a laptop
python run_pipeline.py --from 03  # skip earlier stages
python run_pipeline.py --only 05  # rerun just the model
```

Each stage is idempotent — running it again with the same input produces the
same output.
