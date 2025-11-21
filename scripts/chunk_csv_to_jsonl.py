import os
import csv
import json

# Config
INPUT_CSV = "data/raw/bmw_sales_data.csv"
OUTPUT_JSONL = "data/processed/bmw_chunks.jsonl"

# Read the CSV and convert each row into a flattened chunk
def process_csv(input_path):
    chunks = []
    with open(input_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for i, row in enumerate(reader):
            chunk_text = "; ".join([f"{k}: {v}" for k, v in row.items()])
            chunk = {
                "id": f"bmw-{i}",
                "text": chunk_text,
                "metadata": {
                    "row_number": i
                }
            }
            chunks.append(chunk)
    return chunks

# Save to JSONL file (one JSON object per line)
def save_chunks_to_jsonl(chunks, output_path):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)  # ✅ Create folders if needed
    with open(output_path, 'w', encoding='utf-8') as f:
        for chunk in chunks:
            f.write(json.dumps(chunk) + '\n')

# Run ETL
if __name__ == "__main__":
    chunks = process_csv(INPUT_CSV)
    save_chunks_to_jsonl(chunks, OUTPUT_JSONL)
    print(f"✅ Processed {len(chunks)} chunks into {OUTPUT_JSONL}")
