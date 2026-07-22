# Computational Analysis of Communication
## Framing Analysis of Ethnic and Racial Bias in German News Media

**Course:** Exercise: Computational Analysis of Communication (FSS 2026)  
**Focus:** Benefit and Threat Framing Dimension in German News 

---

## Project Overview

This project is part of a seminar Project at the University of Mannheim that operationalizes ethnic and racial bias in German news communication using computational methods. Each research group focuses on one dimension of bias; this group focuses on **framing** — specifically how different ethnic and social groups are portrayed in news multiparagraphs.

The dataset consists of German newspaper articles from 2022, spanning national media (e.g. FAZ, Süddeutsche Zeitung), regional outlets, and alternative media (left- and right-wing). Group identities in the data are masked as `[Gruppe 1]` and `[andere Gruppe]` for anonymization purposes.

The theoretical foundation comes from Freudenthaler, Ludwig & Müller (under review), *Fragmented Racism in Public Discourse*, which establishes dimensions of interest including the Stereotype Content Model and Immigration and Crime Frames.

---

## Research Question
```text
Can large language models, guided by iteratively refined natural-language annotation instructions, reliably and validly identify group-related crime framing in German news coverage, and how does their performance compare with that of human annotators?
```
---

## Repository Structure
```text
CAC/
├── dataset/                                      # Local datasets, generally not tracked in Git
│   ├── all_multi_paragraphs_2022_2026.RDS        # Raw German source dataset
│   ├── all_multi_paragraphs_2022_2026.csv        # Dataset converted from RDS to CSV
│   └── all_multi_paragraphs_2022_2026_translated.csv
│                                                  # English-translated dataset
│
├── Reads/                                        # Reference material and project literature
├── Report/                                       # Project reports and written documentation
├── results/                                      # Generated annotation and analysis outputs
│
├── annotation_setup.py                           # Annotation environment and data setup
│
├── framing_annotation_step2.ipynb                # Framing annotation step 2
├── framing_annotation_step2.1.ipynb              # Revised framing annotation step 2
├── framing_annotation_step_3.ipynb               # Framing annotation step 3
├── framing_annotation_step4.ipynb                # Framing annotation step 4
├── framing_reannotation.ipynb                    # Reannotation workflow
├── framing_step2_validation.ipynb                 # Validation of step 2 annotations
├── framing_step3_4_confidence.ipynb               # Confidence analysis for steps 3 and 4
├── framing_step3_4_two_llm.ipynb                  # Two-LLM workflow for steps 3 and 4
├── framing_step4_new250.ipynb                     # Step 4 workflow for 250 new observations
├── framing_step4_new250_updated.ipynb             # Updated workflow for 250 new observations
├── framing_step4_updated.ipynb                    # Updated framing annotation step 4
│
├── rescore_pydi.py                                # Rescoring script
├── translate_run.py                              # German-to-English translation script
├── translate.ipynb                               # Interactive translation workflow
├── run_translation.sh                            # Cluster job script for translation
├── test.ipynb                                    # API and workflow testing
│
├── requirements.txt                              # Python dependencies
├── .env                                          # API credentials, not tracked in Git
├── .gitattributes                                # Git attribute configuration
├── .gitignore                                    # Files excluded from Git
└── readme.md                                     # Project documentation
```
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
