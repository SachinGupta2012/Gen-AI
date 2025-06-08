import os
import requests

from glob import glob

GROQ_API_KEY = "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"
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL = "llama3-70b-8192"

TEMPLATE_PATH = "template/template.csv"
SOURCE_DIR = "MultipleFiles"
OUTPUT_PATH = "output/output.csv"

def call_groq_api(template_text, source_texts):
    joined_sources = "\n\n".join(source_texts)

    prompt = f"""
You are a data assistant. Below is a CSV template used for aged care financial reporting. It includes labels such as '◦ Registered nurses', '◦ Enrolled nurses', etc., each followed by placeholder values ($0.00 or 0.00).

Your task is to:
1. Extract actual numeric values from the source CSVs provided below.
2. Fill the values into the correct rows in the template.
3. Do NOT change the structure, formatting, or headings.

=== TEMPLATE START ===
{template_text}
=== TEMPLATE END ===

=== SOURCE FILES START ===
{joined_sources}
=== SOURCE FILES END ===

Return ONLY the updated CSV content.
""".strip()

    response = requests.post(
        GROQ_API_URL,
        headers={
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": MODEL,
            "messages": [
                {"role": "system", "content": "You extract and populate structured financial data into a predefined template."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.2
        }
    )
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]

def main():
    # Read the template as raw text
    with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
        template_text = f.read()

    # Read all source CSVs as raw text
    source_csv_texts = []
    for filepath in glob(os.path.join(SOURCE_DIR, "*.csv")):
        with open(filepath, "r", encoding="utf-8") as f:
            source_csv_texts.append(f.read())

    # Call Groq to populate template
    updated_csv = call_groq_api(template_text, source_csv_texts)

    # Save the output
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write(updated_csv)

    print(f"✅ Populated CSV saved to: {OUTPUT_PATH}")

if __name__ == "__main__":
    main()
