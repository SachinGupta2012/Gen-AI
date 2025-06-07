# GenAI-Template-Filler

A Python-based automation tool to intelligently populate structured Excel/CSV templates using AI mapping and placeholder logic. Designed for structured reporting tasks such as aged care expenditure templates.

---

## 🔧 Features

* Reads multiple CSV data sources (employee costs, labour hours, bed days, etc.)
* Uses Groq AI (e.g., LLaMA3 model) to suggest mappings between source and template
* Populates the template with placeholder values (like `$0.00`, `0.00`, `-`)
* Automatically corrects encoding and formatting issues (like `â—¦`, `-  `)
* Supports both CSV and Excel (`.xlsx`) export formats

---

## 📁 Folder Structure

```
GenAI-Template-Filler/
├── main.py
├── .venv
├── requirements.txt                      # Main script
├── template/
│   └── template.csv            # Input template file
├── source/
│   ├── agency_staff_costs.csv
│   ├── bed_days.csv
│   ├── employee_labour_costs.csv
│   ├── hourly_rates.csv
│   ├── labour_hours.csv
│   └── outbreak_management_costs.csv
├── output/
│   └── populated_template.xlsx # Output file (Excel)
```

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

## 📌 Sample Output

| Field                              | ACH Valley View | ACH Riverbank | ACH Meadowfield |
| ---------------------------------- | --------------- | ------------- | --------------- |
| ◦ Registered nurses                | \$0.00          | \$0.00        | \$0.00          |
| ◦ Infection Prevention and Control | -               | -             | -               |

---

## 🤝 Credits

Built with using Python and Groq AI.

---
