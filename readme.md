# Computational Analysis of Communication
## Framing Analysis of Ethnic and Racial Bias in German News Media

**Course:** Exercise: Computational Analysis of Communication (FSS 2026)  
**Instructor:** Dr. Rainer Freudenthaler, University of Mannheim  
**Focus:** Framing dimension of ethnic and racial bias in news coverage

---

## Project Overview

This project is part of a seminar exercise at the University of Mannheim that operationalizes ethnic and racial bias in German news communication using computational methods. Each research group focuses on one dimension of bias; this group focuses on **framing** — specifically how different ethnic and social groups are portrayed in news multiparagraphs.

The dataset consists of German newspaper articles from 2022, spanning national media (e.g. FAZ, Süddeutsche Zeitung), regional outlets, and alternative media (left- and right-wing). Group identities in the data are masked as `[Gruppe 1]` and `[andere Gruppe]` for anonymization purposes.

The theoretical foundation comes from Freudenthaler, Ludwig & Müller (under review), *Fragmented Racism in Public Discourse*, which establishes dimensions of interest including the Stereotype Content Model and Immigration and Crime Frames.

---

## Research Question

How are different ethnic and social groups framed in German news multiparagraphs, and does framing differ systematically across media outlets and group identities?

---

## Repository Structure

```
CAC/
├── dataset/                                        # ← not tracked in git, generate locally
│   ├── all_multi_paragraphs_2022_2026.RDS          # Raw German dataset (source file)
│   ├── all_multi_paragraphs_2022_2026.csv          # Converted CSV (generated from RDS)
│   └── all_multi_paragraphs_2022_2026_translated.csv  # Translated dataset (EN, generated)
├── test.ipynb                                      # API testing & framing annotation notebook
├── translate_run.py                                # Translation script (German → English)
├── run_translation.sh                              # sbatch job script for bwUniCluster
├── .env                                            # API key (not tracked in git)
├── .gitignore
└── README.md
```

---

## Getting Started

### Step 0: Convert RDS to CSV

The raw dataset is provided as an `.RDS` file. Before running anything else, convert it to CSV using R:

```r
# In R or RStudio
df <- readRDS("dataset/all_multi_paragraphs_2022_2026.RDS")
write.csv(df, "dataset/all_multi_paragraphs_2022_2026.csv", row.names = FALSE)
```

Or from the R command line on the cluster:

```bash
Rscript -e 'df <- readRDS("dataset/all_multi_paragraphs_2022_2026.RDS"); write.csv(df, "dataset/all_multi_paragraphs_2022_2026.csv", row.names = FALSE)'
```

This generates `all_multi_paragraphs_2022_2026.csv` (~660k rows) which is required by the translation and annotation scripts.

---

## Dataset

| Column | Description |
|--------|-------------|
| `article_id` | Unique article identifier |
| `pub` | Publication source |
| `par_index` | Paragraph index within article |
| `text_block` | German multiparagraph text |
| `group` | Group label (masked) |
| `length` | Character length of text block |
| `text_block_en` | English translation (generated) |

---

## Pipeline

### Step 1: Translation (German → English)

The raw dataset is in German. We translate it to English using `llama3.1:8b` via Ollama running on the bwUniCluster GPU (NVIDIA A100 80GB).

**Script:** `translate_run.py`

Configure the row range at the top of the script:
```python
START_ROW  = 0       # ← start row (inclusive)
STOP_ROW   = 10000   # ← end row (exclusive)
```

Run on the cluster (interactive GPU session):
```bash
salloc -p gpu_a100_il --nodes=1 --ntasks=1 --gres=gpu:1 --time=12:00:00
module load cs/ollama/0.5.11
ollama serve &
sleep 15
source ~/CAC/.venv/bin/activate
cd ~/CAC
python translate_run.py
```

Or submit as a background job:
```bash
sbatch run_translation.sh
```

The script resumes automatically from where it left off if interrupted — every row is saved immediately to the output CSV.

### Step 2: Framing Annotation

Using the `bacchuss` R package and the university's LLM API, we annotate translated multiparagraphs for framing dimensions following the routine described in [Freudenthaler's annotation guide](https://github.com/Rainer-Freudenthaler/bacchuss/blob/main/vignettes/routine.md).

The annotation routine follows these steps:

1. **Draft annotation instructions** — define role, context, labels, decision rules, output format
2. **Test and improve coverage** — run on small samples, identify hard cases using `briseus()`
3. **Test on curated hard/soft case sample** — measure against human labels using F-score, Precision, Recall
4. **Representative human validation** — intercoder reliability (Krippendorff's Alpha) + LLM validity
5. **Report results** — include annotation instructions in appendix

---

## Environment Setup

### Python (Translation)

```bash
python3.12 -m venv ~/cac
source ~/cac/bin/activate
pip install pandas requests python-dotenv
```

### API Key

Create a `.env` file in the project root:
```
CAC_API_KEY=your_key_here
```

Add `.env` to `.gitignore`:
```
.env
dataset/
```

### bwUniCluster

This project runs on [bwUniCluster 3.0](https://wiki.bwhpc.de/e/BwUniCluster3.0). Available GPU partition: `gpu_a100_il` (NVIDIA A100 80GB PCIe).

Ollama module: `cs/ollama/0.5.11`  
Models used: `llama3.1:8b`, `mistral-nemo`

---

## Models

| Model | Use | Endpoint |
|-------|-----|----------|
| `llama3.1:8b` | Translation (DE → EN) | `http://localhost:11434/api/chat` |
| `mistral-nemo` | Framing annotation | University API `/v1/chat/completions` |

---

## Progress Tracking

Check translation progress on the cluster:
```bash
wc -l ~/CAC/dataset/all_multi_paragraphs_2022_2026_translated.csv
squeue -u ma_mpandya
tail -f ~/CAC/translation_<jobid>.out
```

---

## References

- Freudenthaler, R., Ludwig, K., Müller, P. (under review). *Fragmented Racism in Public Discourse*
- Neuendorf, K. A. (2016). *The Content Analysis Guidebook* (2nd ed.). Sage Publications
- Weber, M., & Reichardt, M. (2023). Evaluation is all you need. *arXiv:2401.00284*
- Lin et al. (2025). ollamar: An R package for running large language models. *JOSS, 10*(105)
- Van Atteveldt, W., Trilling, D., & Calderón, C. A. (2022). *Computational Analysis of Communication*. Wiley Blackwell
- bacchuss R package: https://github.com/Rainer-Freudenthaler/bacchuss

---

## Notes

- Group names in the dataset are anonymized as `[Gruppe 1]` and `[andere Gruppe]` — these are preserved as-is in translations and annotations
- The dataset contains ~660,000 multiparagraphs; translation is done in batches with automatic resume on interruption
- Report due: January 19 — submit to rfreuden@mail.uni-mannheim.de (CC: rainer@freudenthaler-schwaigern.de)
- Format: 10–12 pages, APA 7th edition, clearly indicate who wrote which section