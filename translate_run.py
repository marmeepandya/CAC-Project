import pandas as pd
import requests
import time
import os

INPUT_CSV  = "dataset/all_multi_paragraphs_2022_2026.csv"
OUTPUT_CSV = "dataset/all_multi_paragraphs_2022_2026_translated.csv"
MODEL      = "llama3.1:8b"
OLLAMA_URL = "http://localhost:11434/api/chat"
TEXT_COL   = "text_block"
START_ROW  = 21334
STOP_ROW   = 30000

def translate(text, retries=3):
    for attempt in range(retries):
        try:
            resp = requests.post(OLLAMA_URL, json={
                "model": MODEL,
                "messages": [
                    {
                        "role": "user",
                        "content": f"Translate the following German text to English. Preserve names, numbers, quotes, and masked entities like [Gruppe 1] and [andere Gruppe] exactly. Maintain paragraph structure. Output only the translation, nothing else:\n\n{text}"
                    }
                ],
                "stream": False
            }, timeout=120)
            return resp.json()["message"]["content"].strip()
        except Exception as e:
            print(f"  [attempt {attempt+1}] Error: {e}")
            time.sleep(5)
    return None

df = pd.read_csv(INPUT_CSV)
chunk = df.iloc[START_ROW:STOP_ROW].copy().reset_index(drop=True)
print(f"Processing rows {START_ROW} → {STOP_ROW} ({len(chunk)} rows)")

if os.path.exists(OUTPUT_CSV) and os.path.getsize(OUTPUT_CSV) == 0:
    os.remove(OUTPUT_CSV)

if os.path.exists(OUTPUT_CSV):
    done = pd.read_csv(OUTPUT_CSV)
    local_start = max(0, len(done) - START_ROW)
    print(f"Resuming from row {local_start}")
else:
    local_start = 0
    print("Starting fresh")

for i in range(local_start, len(chunk)):
    text = chunk.at[i, TEXT_COL]
    chunk.at[i, TEXT_COL + "_en"] = "" if pd.isna(text) or str(text).strip() == "" else translate(str(text))
    row_out = chunk.iloc[[i]]
    write_header = not os.path.exists(OUTPUT_CSV)
    row_out.to_csv(OUTPUT_CSV, mode="a", header=write_header, index=False)
    print(f"  [{i+1}/{len(chunk)}] row {START_ROW + i + 1} done")

print(f"\n✓ Done! Saved to {OUTPUT_CSV}")
