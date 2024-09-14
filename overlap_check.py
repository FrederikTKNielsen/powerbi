import pandas as pd
import os

# Ensure output directory exists
output_dir = "output"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Load the data from xlsx files (dropping the last two rows)
budget_data_path = "data/facts_budgetpost.xlsx"
financial_data_path = "data/facts_financialpost.xlsx"

facts_budgetpost = pd.read_excel(budget_data_path).iloc[:-2]
facts_financialpost = pd.read_excel(financial_data_path).iloc[:-2]

# List of columns to check for overlapping IDs
columns_to_check = ['DelregnskabID', 'Fast_AktivitetID', 'Fast_ProjektID', 'Fast_StedID', 'Regnskabsnr', 'SBS_BudgetartID']

# Create a dictionary to store results of overlap checks
overlap_results = {}

# Check for overlapping IDs in each column
for column in columns_to_check:
    budget_ids = set(facts_budgetpost[column].dropna().unique())
    financial_ids = set(facts_financialpost[column].dropna().unique())
    
    # Find intersection of IDs
    common_ids = budget_ids.intersection(financial_ids)
    
    # Store the result
    overlap_results[column] = common_ids
    print(f"Overlap found in {column}: {len(common_ids)} common IDs")

# Output the results to a text file for documentation
with open(os.path.join(output_dir, "overlapping_ids_report.txt"), "w") as f:
    for column, common_ids in overlap_results.items():
        f.write(f"Overlapping IDs between facts_budgetpost and facts_financial_post\n\n")
        f.write(f"Overlap found in {column}: {len(common_ids)} common IDs\n")
        f.write(f"Common IDs: {list(common_ids)}\n\n")

print(f"\nCheck complete. Overlapping IDs between facts_budgetpost and facts_financial_post report is saved in {output_dir}/overlapping_ids_report.txt")