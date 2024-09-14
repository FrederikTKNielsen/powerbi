import pandas as pd
import os
import matplotlib.pyplot as plt

# Ensure output directory exists
output_dir = "output"
os.makedirs(output_dir, exist_ok=True)

def save_df(df, name):
    """
    Save a DataFrame to a CSV file in the output directory.
    """
    df.to_csv(os.path.join(output_dir, f"{name}.csv"), index=False)
    print(f"Saved {name}.csv to {output_dir}")

# Load the data
print("Loading data...")
facts_financialpost = pd.read_excel("data/facts_financialpost.xlsx", skipfooter=2, engine='openpyxl')
dim_kontoplan = pd.read_excel("data/dim_kontoplan.xlsx", skipfooter=2, engine='openpyxl')

# Ensure both 'SBS_BudgetartID' columns are of the same data type (string)
facts_financialpost['SBS_BudgetartID'] = facts_financialpost['SBS_BudgetartID'].astype(str)
dim_kontoplan['SBS_BudgetartID'] = dim_kontoplan['SBS_BudgetartID'].astype(str)

# Merge financial data with dim_kontoplan to explain the costs
financial_with_cost_type = pd.merge(facts_financialpost, dim_kontoplan, on='SBS_BudgetartID', how='left')

# Sum the Forbrug (spending) for each Budgetartnavn (no additional operations)
summed_forbrug = financial_with_cost_type.groupby('Budgetartnavn')['Forbrug'].sum().reset_index()

# Calculate total Forbrug across all Budgetartnavn
total_forbrug = summed_forbrug['Forbrug'].sum()
print(f"Total Forbrug across all Budgetartnavn: {total_forbrug}")

# Save the merged data for tracking
save_df(summed_forbrug, "summed_forbrug_by_Budgetartnavn")

# Visualization: Plot the summed Forbrug by Budgetartnavn
plt.figure(figsize=(12, 6))
bars = plt.bar(summed_forbrug['Budgetartnavn'], summed_forbrug['Forbrug'], color='orange')

# Add percentage annotations
for bar, value in zip(bars, summed_forbrug['Forbrug']):
    percentage = (value / total_forbrug) * 100
    plt.annotate(f'{percentage:.2f}%', xy=(bar.get_x() + bar.get_width() / 2, bar.get_height()), 
                 xytext=(0, 5), textcoords="offset points", ha='center', va='bottom', fontsize=10)

plt.title("Summed Financial Allocation by Budgetartnavn (Forbrug)")
plt.ylabel("Financial Amount (Forbrug)")
plt.xlabel("Budgetartnavn")
plt.xticks(rotation=45, ha="right")
plt.tight_layout()

# Save the plot
filename = os.path.join(output_dir, "summed_financial_allocation_by_Budgetartnavn_with_percentages.png")
plt.savefig(filename)
plt.close()

print(f"Saved Financial Allocation chart with percentages to {filename}")
