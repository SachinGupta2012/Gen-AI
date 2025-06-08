# GenAI-Template-Filler

A Python-based automation tool to intelligently populate structured Excel/CSV templates using AI mapping and placeholder logic. Designed for structured reporting tasks such as aged care expenditure templates.

---

## 📌 Assignment Overview

The system:
- Reads a complex CSV template with structured financial categories.
- Extracts matching financial values from multiple source CSVs.
- Uses the **Groq AI model** to map and populate correct values into the template.
- Outputs the result into a new CSV file, preserving structure, indentation, comments, and formatting.

---
## 📁 Folder Structure

```
GenAI-Template-Filler/
│
├── main.py # Main script to extract & populate data
├── template.csv # Target CSV structure to be populated
├── source_csvs/ # Folder with raw input CSVs
│ ├── source1.csv
│ ├── source2.csv
│ └── ...
├── output.csv # Final structured & populated output
└── README.md

---

## 🚀 How to Run

1. Install dependencies:

```bash
pip install pandas openpyxl groq
```

2. Set your Groq API key in `main.py`:

```python
self.client = Groq(api_key="YOUR_API_KEY")
```

3. Run the script:

```bash
python main.py
```

4. Outputs will be saved in the `output/` folder.

---

## 📝 Notes

* This project is intended for demonstration/assignment use.
* The populated values are placeholders (`$0.00`, `-`) and not calculated from source data.
* Special character cleanup and UTF-8 normalization are included.

---

Built with using Python and Groq AI.

---
