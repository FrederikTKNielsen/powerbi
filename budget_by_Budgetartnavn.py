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
facts_budgetpost = pd.read_excel("data/facts_budgetpost.xlsx", skipfooter=2, engine='openpyxl')
dim_kontoplan = pd.read_excel("data/dim_kontoplan.xlsx", skipfooter=2, engine='openpyxl')

# Convert date columns to datetime
print("Converting date columns...")
facts_budgetpost['Dato'] = pd.to_datetime(facts_budgetpost['Dato'], errors='coerce')

# Drop rows with invalid dates
print("Dropping rows with invalid dates...")
facts_budgetpost.dropna(subset=['Dato'], inplace=True)

# Ensure both 'SBS_BudgetartID' columns are of the same data type (string)
facts_budgetpost['SBS_BudgetartID'] = facts_budgetpost['SBS_BudgetartID'].astype(str)
dim_kontoplan['SBS_BudgetartID'] = dim_kontoplan['SBS_BudgetartID'].astype(str)

# Calculate 'Averaged_budgets' before merging
# List of budget columns
budget_columns = ['Budget', 'Budgetbeloeb_Vedroerer', 'OprindeligtBudgetbeloeb']

# Calculate 'Averaged_budgets' as the average of the three budget columns for each record
facts_budgetpost['Averaged_budgets'] = facts_budgetpost[budget_columns].mean(axis=1)

# Save the budget data with Averaged_budgets for tracking
save_df(facts_budgetpost, "facts_budgetpost_with_averaged_budgets")

# Merge budget data with dim_kontoplan to explain the costs
budget_with_cost_type = pd.merge(facts_budgetpost, dim_kontoplan, on='SBS_BudgetartID', how='left')

# Aggregate the data by 'Budgetartnavn' and sum 'Averaged_budgets'
summed_budget = budget_with_cost_type.groupby('Budgetartnavn')['Averaged_budgets'].sum().reset_index()

# Summing the total of averaged budgets
total_averaged_budget = summed_budget['Averaged_budgets'].sum()
print(f"Total of Averaged Budgets: {total_averaged_budget}")

# Save the aggregated data for tracking
save_df(summed_budget, "summed_budget_by_Budgetartnavn")

# Visualization: Plot the budget allocation by Budgetartnavn using 'Averaged_budgets'
plt.figure(figsize=(12, 6))
bars = plt.bar(summed_budget['Budgetartnavn'], summed_budget['Averaged_budgets'], color='blue')

# Add percentage annotations
for bar, value in zip(bars, summed_budget['Averaged_budgets']):
    percentage = (value / total_averaged_budget) * 100
    plt.annotate(f'{percentage:.2f}%', xy=(bar.get_x() + bar.get_width() / 2, bar.get_height()), 
                 xytext=(0, 5), textcoords="offset points", ha='center', va='bottom', fontsize=10)

plt.title("Budget Allocation by Budgetartnavn (Averaged Budgets)")
plt.ylabel("Averaged Budget Amount")
plt.xlabel("Budgetartnavn")
plt.xticks(rotation=45, ha="right")
plt.tight_layout()

# Save the plot
filename = os.path.join(output_dir, "budget_allocation_by_Budgetartnavn_averaged_budget_with_percentages.png")
plt.savefig(filename)
plt.close()

print(f"Saved Budget Allocation chart with percentages to {filename}")
