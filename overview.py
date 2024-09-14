import pandas as pd
import os

# Ensure output directory exists
output_dir = "output"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Paths to the datasets
budget_data_path = "data/facts_budgetpost.xlsx"
financial_data_path = "data/facts_financialpost.xlsx"
dim_sted_path = "data/dim_sted.xlsx"
dim_kontoplan_path = "data/dim_kontoplan.xlsx"
dim_delregnskab_path = "data/dim_delregnskab.xlsx"

# Load the datasets
tables = {
    "facts_budgetpost": pd.read_excel(budget_data_path).iloc[:-2],
    "facts_financialpost": pd.read_excel(financial_data_path).iloc[:-2],
    "dim_sted": pd.read_excel(dim_sted_path).iloc[:-2],
    "dim_kontoplan": pd.read_excel(dim_kontoplan_path).iloc[:-2],
    "dim_delregnskab": pd.read_excel(dim_delregnskab_path).iloc[:-2],
}

# Function to generate overview for a dataframe
def generate_overview(df, table_name):
    overview = []
    
    overview.append(f"--- Overview of {table_name} ---\n")
    overview.append(f"Shape: {df.shape[0]} rows, {df.shape[1]} columns\n")
    overview.append(f"\nColumn Information:\n")
    
    for col in df.columns:
        dtype = df[col].dtype
        missing = df[col].isna().sum()
        unique = df[col].nunique()
        overview.append(f"Column: {col}\n")
        overview.append(f"  - Type: {dtype}\n")
        overview.append(f"  - Missing Values: {missing}\n")
        overview.append(f"  - Unique Values: {unique}\n")
    
    overview.append("\n" + "-"*40 + "\n\n")
    
    return "\n".join(overview)

# Write overview of each table to a file
output_file = os.path.join(output_dir, "tables_overview.txt")
with open(output_file, "w") as f:
    for table_name, df in tables.items():
        overview = generate_overview(df, table_name)
        f.write(overview)

print(f"Overview of tables has been saved to {output_file}.")
