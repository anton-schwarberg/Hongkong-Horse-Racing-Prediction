# Hong Kong Horse Racing Prediction

<p align="center">
  <img src="assets/horse_race.gif" alt="Hong Kong HJC Demo" width="700" />
</p>

An end-to-end machine learning pipeline that forecasts Hong Kong horse race
outcomes: from scraping 16 seasons of historical results off the HKJC
website, through feature engineering and leak-free preprocessing, to a
calibrated probability model evaluated on a held-out future season.

## Why I built this

In May 2025 I spent an afternoon at Sha Tin, one of Hong Kong's two race
courses. What struck me wasn't the scale, though the scale is striking;
the 2024-25 season drew over 1.7 million attendees with billions in betting
handle. What struck me was how *embedded* the sport is in the local culture.
The Hong Kongers around me weren't tourists doing it for fun. They were
animated, opinionated, intensely engaged. This was their thing.

That same week I came across the story of [Bill Benter](https://en.wikipedia.org/wiki/Bill_Benter),
an American mathematician who, in the 1980s, decided that a notoriously hard
form of gambling could be made calculable. He'd been blacklisted from Las
Vegas casinos for card counting, so he packed up, moved to Hong Kong, and
spent years building a statistical model of horse racing. Together with a
small syndicate, he ran what's reportedly one of the most profitable betting
operations in history, close to a billion dollars in winnings over the
following decades.

Three things hooked me about the story. First, that horse racing, *the*
archetype of dumb luck, turned out to be partially modellable, given enough
data and enough patience. Second, that the work was effectively pioneering
applied ML decades before "data scientist" was a job title. Third, that the
path to doing it ran through being an outsider, a Vegas outlaw rebuilding
from scratch on the other side of the world, rather than through any
established institution.

I'm not Bill Benter. But the combination of "real-world data", "messy
domain", "honest difficulty", and "you can probably do better than random"
was the kind of problem I wanted to spend time on. This repo is that.

## What this project does

End-to-end ML pipeline that:

1. **Scrapes** 16 seasons of historical race results (2009 to 2025) from
   the official HKJC website.
2. **Cleans and engineers features**: rolling form statistics, weight
   trends, race-aware percentile ranks, expanding (leak-free) target
   encodings for horses, jockeys, and trainers.
3. **Trains and compares four models** (logistic regression, LightGBM
   classifier, LightGBM ranker, and XGBoost ranker) on a strict
   time-based train / validation / test split (seasons 1 to 14 / 15 / 16).
4. **Selects a chosen model** with explicit reasoning, based on calibration
   quality and Top-1 / Top-3 hit rates rather than raw accuracy.
5. **Surfaces diagnostics**: feature importance, calibration curves,
   SHAP values, and per-field-size performance breakdowns.

Imputation statistics, target encodings, and validation splits are all
computed in ways that prevent look-ahead bias: at no point does the model
see information that wouldn't have been available before the race.

## Pipeline

The full data flow is split across five notebooks in `notebooks/`. Each
stage reads from `data/` and writes its output back to `data/`:

| Stage | Notebook | Input | Output |
|-------|----------|-------|--------|
| 1 | `01_Combining.ipynb` | `data/HKHJC_{2009..2025}.csv` | `data/HKHJC_FINAL.csv` |
| 2 | `02_Preprocessing.ipynb` | `HKHJC_FINAL.csv` | `data/HKHJ_Dataset_Prepared.csv` |
| 3 | `03_Feature_Engineering.ipynb` | `HKHJ_Dataset_Prepared.csv` | `data/HKHJ_Dataset_Feature_Engineered.csv` |
| 4 | `04_Prepare_Data.ipynb` | `HKHJ_Dataset_Feature_Engineered.csv` | `data/HKHJ_Dataset_After_MV.parquet` |
| 5 | `05_Modelling.ipynb` | `HKHJ_Dataset_After_MV.parquet` | (model evaluation) |

Mappings (location, going, race class) and other shared code live in `src/`.

## Results

The test set is the most recent season, data the model has never seen
during training or tuning. Chosen model: **`LGBMClassifier`**.

| Metric | Test |
|---|---|
| ROC-AUC | 0.726 |
| PR-AUC | 0.450 |
| Top-1 hit rate | 52.9 % |
| Top-3 hit rate | 87.1 % |

**Reading the numbers:**

- **Top-1 hit rate (52.9 %)**: in 53 % of races, the model's single
  highest-rated horse actually finished in the top 3 (place, not win).
  The random baseline for a ~12-horse field is roughly 25 %.
- **Top-3 hit rate (87.1 %)**: in 87 % of races, at least one of the
  model's three highest-rated horses placed.
- **ROC-AUC (0.726)**: competitive with published academic work on horse
  racing without odds data (typical range 0.65 to 0.75).

The model is deliberately *not* trained on betting odds, which would
normally be the single strongest predictor in a horse racing model. The
performance reported here is honest signal extracted from horse, jockey,
trainer, weight, draw, form, and race-condition features alone.

### Why LightGBM Classifier and not a Ranker?

Two of the four candidate models were learning-to-rank models
(`LGBMRanker`, `XGBRanker`), architecturally a better fit for "which horse
wins a race". They appeared to win on Brier and LogLoss but lost on
calibration: the softmax-within-race normalisation that gives the rankers
their probability interpretation mechanically compresses predictions into
the ~0.05 to 0.55 range and never reaches the high-confidence region. If
the model is ever used for bet sizing (Kelly criterion), what matters is
that "65 % probability" actually means 65 %. The classifier delivers that;
the rankers don't.

The full justification, including a four-model comparison table,
calibration plot, and SHAP analysis, lives in `notebooks/05_Modelling.ipynb`.

## How could you actually use this?

Realistic answer: **not yet, but the remaining work is well-defined.**

The model itself is sound, but it currently lives inside a batch pipeline
that processes the full historical dataset at once. To use it on race day,
four pieces are still missing:

1. **A live feature-engineering path.** Stages 3 and 4 are written to
   process the full dataset in one pass. Real-time use needs a function
   `compute_features(history, race_card) -> X` that produces the same 87
   features from (a) each participating horse's full history and (b)
   today's race card, without re-running the entire pipeline.

2. **A race-card scraper.** Every input the model needs is published on
   the HKJC race card *before* the race: draw, jockey weight, declared
   horse weight, going, distance, class, gear changes. This data needs to
   be pulled minutes before the off.

3. **Persisted artefacts.** The trained classifier, the train-set
   imputation medians, and the categorical mappings need to be saved
   (`joblib.dump(...)`) and loaded by the inference path.

4. **The biggest missing feature: per-horse rating.** The current dataset
   only captures the *race* rating band (e.g. "60-40"), not each horse's
   individual official rating. The `Rtg.` column on the race card,
   classically *the* strongest predictor in horse racing, is not yet in
   the dataset. Adding it would likely push test ROC-AUC past 0.78.

With all four in place, the workflow would be: pick a race the morning of,
run inference, get per-horse Top-3 probabilities, compare those against
the market's implied probabilities (`1 / odds`, corrected for the
bookmaker's overround), and bet only when the model's estimate exceeds
the market's by a margin large enough to cover the bookmaker's edge.

Bill Benter's syndicate ran exactly that loop for thirty years. They had
better data, a much larger feature set including form ratings and odds
movements, and a serious feedback loop. This project is one Python
package and a scraper away from being a teaching version of the same
idea, not a billion-dollar machine.

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

## Running the pipeline

```bash
python run_pipeline.py            # all five stages, ~5 min on a laptop
python run_pipeline.py --from 03  # skip earlier stages
python run_pipeline.py --only 05  # rerun just the model
```

Each stage is idempotent: running it again with the same input produces
the same output.
