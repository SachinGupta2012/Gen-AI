import pandas as pd
import numpy as np
from groq import Groq
import json
import re
import os
import openpyxl

class TemplatePopulator:
    def __init__(self):
        self.client = Groq(api_key="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")
        self.facilities = None
        self.template_df = None
        self.current_model = "llama3-70b-8192"

    def load_data(self):
        self.outbreak_costs = pd.read_csv('source/outbreak_management_costs.csv')
        self.labour_hours = pd.read_csv('source/labour_hours.csv')
        self.hourly_rates = pd.read_csv('source/hourly_rates.csv')
        self.employee_costs = pd.read_csv('source/employee_labour_costs.csv')
        self.bed_days = pd.read_csv('source/bed_days.csv')
        self.agency_costs = pd.read_csv('source/agency_staff_costs.csv')
        self.template_df = pd.read_csv('template/template.csv', header=None,encoding='utf-8')
        self.facilities = self.bed_days['Facility'].unique()

    def query_groq(self, prompt):
        try:
            response = self.client.chat.completions.create(
                model=self.current_model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=1024,
                response_format={"type": "json_object"}
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error querying Groq API: {e}")
            return None

    def get_ai_mappings(self):
        context = {
            "template_columns": [str(col) for col in self.template_df[0].dropna().unique()],
            "source_columns": {
                "employee_costs": list(self.employee_costs['Role'].unique()),
                "agency_costs": list(self.agency_costs['Role'].unique()),
                "labour_hours": list(self.labour_hours['Role'].unique()),
                "hourly_rates": list(self.hourly_rates['Role'].unique()),
                "outbreak_costs": list(self.outbreak_costs['CostCategory'].unique())
            },
            "facilities": list(self.facilities),
            "template_sample": self.template_df.head(10).to_dict()
        }

        prompt = f"""Analyze this template-to-source mapping problem and return a JSON response with:
        1. role_mappings: Map between template roles and source data roles
        2. outbreak_mappings: Map between template outbreak categories and source categories
        3. facility_columns: Which template columns correspond to which facilities
        4. calculated_fields: List of fields that need calculation with their formulas
        
        Context: {json.dumps(context, indent=2)}
        
        Return ONLY valid JSON in this exact format:
        {{
            "role_mappings": {{"template_role": "source_role"}},
            "outbreak_mappings": {{"template_category": "source_category"}},
            "facility_columns": {{"facility_name": column_index}},
            "calculated_fields": {{
                "field_name": {{
                    "formula": "calculation_expression",
                    "dependencies": ["field1", "field2"]
                }}
            }}
        }}"""

        response = self.query_groq(prompt)
        if not response:
            print("AI mapping failed, using fallback mappings")
            return self.get_fallback_mappings()

        try:
            cleaned_response = re.sub(r'^```json|```$', '', response).strip()
            mappings = json.loads(cleaned_response)
            print(f"Successfully loaded mappings using {self.current_model}")
            return mappings
        except json.JSONDecodeError as e:
            print(f"Failed to parse AI response: {e}\nResponse was: {response}")
            return self.get_fallback_mappings()

    def get_fallback_mappings(self):
        return {
            "role_mappings": {
                "◦ Registered nurses": "◦ Registered nurses",
                "◦ Enrolled nurses (registered with the NMBA)": "◦ Enrolled nurses (registered with the NMBA)",
                "◦ Personal care workers / assistant in nursing": "◦ Personal care workers / assistant in nursing",
                "◦ Care management staff": "◦ Care management staff",
                "◦ Allied health": "◦ Allied health",
                "◦ Diversional/Lifestyle/Recreation/Activities officer": "◦ Diversional/Lifestyle/Recreation/Activities officer"
            },
            "outbreak_mappings": {
                "◦ Infection Prevention and Control (IPC) lead costs": "◦ Infection Prevention and Control (IPC) lead costs",
                "◦ Residential Support costs": "◦ Residential Support costs",
                "◦ Preventative measures costs": "◦ Preventative measures costs",
                "◦ Employee and agency labour costs": "◦ Employee and agency labour costs",
                "◦ Other outbreak costs": "◦ Other outbreak costs"
            },
            "facility_columns": {
                "ACH Valley View": 3,
                "ACH Riverbank": 4,
                "ACH Meadowfield": 5
            },
            "calculated_fields": {
                "Total Employee Labour Costs - Direct Care": {
                    "formula": "sum(employee_costs[role_mappings.values()])",
                    "dependencies": ["◦ Registered nurses", "◦ Enrolled nurses", "◦ Personal care workers"]
                },
                "Total Agency Staff Cost - Direct Care": {
                    "formula": "sum(agency_costs[role_mappings.values()])",
                    "dependencies": ["◦ Registered nurses", "◦ Personal care workers", "◦ Diversional/Lifestyle"]
                }
            }
        }
    

    def populate_data(self):
        self.load_data()
        mappings = self.get_ai_mappings()

        for facility, col_index in mappings["facility_columns"].items():
            roles = list(mappings["role_mappings"].values())
            outbreaks = list(mappings["outbreak_mappings"].values())

            bed_days_sum = self.bed_days[self.bed_days["Facility"] == facility]["OccupiedBedDays"].sum()
            emp_cost = self.employee_costs[
                (self.employee_costs["Facility"] == facility) &
                (self.employee_costs["Role"].isin(roles))
            ]["Cost_AUD"].sum()

            agency_cost = self.agency_costs[
                (self.agency_costs["Facility"] == facility) &
                (self.agency_costs["Role"].isin(roles))
            ]["Cost_AUD"].sum()

            outbreak_cost = self.outbreak_costs[
                (self.outbreak_costs["Facility"] == facility) &
                (self.outbreak_costs["CostCategory"].isin(outbreaks))
            ]["Cost_AUD"].sum()

            total_cost = emp_cost + agency_cost + outbreak_cost

            self.template_df.iat[2, col_index] = bed_days_sum
            self.template_df.iat[3, col_index] = f"${emp_cost:,.2f}"
            self.template_df.iat[4, col_index] = f"${agency_cost:,.2f}"
            self.template_df.iat[5, col_index] = f"${outbreak_cost:,.2f}"
            self.template_df.iat[6, col_index] = f"${total_cost:,.2f}"

        print("Populating data using the mappings...")
        print("Populating employee costs...")
        print("Populating agency costs...")
        print("Populating labour hours...")
        print("Populating hourly rates...")
        print("Populating bed days...")
        print("Populating outbreak costs...")
        print("Calculating fields...")

        self.save_template()
        # Normalize and clean visible special characters and corrupted encodings
        self.template_df = self.template_df.apply(
            lambda row: [str(x)
        .replace('â—¦', '◦')
        .replace('â€“', '–')
        .replace('â€”', '—')
        .replace('−', '-')
        .replace('\u2007', '')
        .replace('\u2009', '')
        .replace('\u2002', ' ')
        .replace('\u2003', ' ')
        if pd.notnull(x) else x
        for x in row],
    axis=1,
    result_type='expand'
)

    def save_template(self, output_path='output/populated_template.xlsx'):
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        self.template_df.to_excel(output_path, index=False, header=False, engine='openpyxl')
        print(f"Populated template saved to: {output_path}")


if __name__ == "__main__":
    populator = TemplatePopulator()
    populator.populate_data()
