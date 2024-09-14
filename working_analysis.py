import pandas as pd
import numpy as np
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

# Load the data, skipping the last two rows
print("Loading data...")
facts_budgetpost = pd.read_excel("data/facts_budgetpost.xlsx", skipfooter=2, engine='openpyxl')
facts_financialpost = pd.read_excel("data/facts_financialpost.xlsx", skipfooter=2, engine='openpyxl')

# Convert date columns to datetime
print("Converting date columns...")
facts_budgetpost['Dato'] = pd.to_datetime(facts_budgetpost['Dato'], errors='coerce')
facts_financialpost['Bogføringsdato'] = pd.to_datetime(facts_financialpost['Bogføringsdato'], errors='coerce')

# Drop rows with invalid dates
print("Dropping rows with invalid dates...")
facts_budgetpost.dropna(subset=['Dato'], inplace=True)
facts_financialpost.dropna(subset=['Bogføringsdato'], inplace=True)

# Adjust financial dates to month-end to match budget dates
facts_financialpost['Month_End'] = facts_financialpost['Bogføringsdato'] + pd.offsets.MonthEnd(0)

# Aggregate financial data by month-end
financial_monthly = facts_financialpost.groupby('Month_End')['Forbrug'].sum().reset_index()

# Function to calculate utilization percentage safely
def safe_utilization(actual, budget):
    return np.where(budget != 0, (actual / budget) * 100, np.nan)

# List of budget columns
budget_columns = ['Budget', 'Budgetbeloeb_Vedroerer', 'OprindeligtBudgetbeloeb']

# Calculate 'Averaged_budgets' as the average of the three budget columns for each record
facts_budgetpost['Averaged_budgets'] = facts_budgetpost[budget_columns].mean(axis=1)

# Aggregate budget data by 'Dato' and 'Budgetnavn'
budget_aggregated = facts_budgetpost.groupby(['Dato', 'Budgetnavn']).agg({
    'Budget': 'sum',
    'Budgetbeloeb_Vedroerer': 'sum',
    'OprindeligtBudgetbeloeb': 'sum',
    'Averaged_budgets': 'sum'
}).reset_index()

# Aggregate averaged budgets across all 'Budgetnavn' by 'Dato'
Averaged_budgets = facts_budgetpost.groupby('Dato')['Averaged_budgets'].mean().reset_index()

# Now, loop over each Budgetnavn to create the line charts and column charts
budgetnavn_list = facts_budgetpost['Budgetnavn'].unique()
print(f"Budgetnavn list: {budgetnavn_list}")

for budgetnavn in budgetnavn_list:
    print(f"Processing Budgetnavn: {budgetnavn}")
    try:
        # Filter budget data for the current Budgetnavn
        budget_data = budget_aggregated[budget_aggregated['Budgetnavn'] == budgetnavn]
        print(f"Budget data for {budgetnavn}:\n{budget_data.head()}")

        # Merge with financial data on date
        merged_data = pd.merge(budget_data, financial_monthly, left_on='Dato', right_on='Month_End', how='left')
        merged_data['Forbrug'] = merged_data['Forbrug'].fillna(0)
        merged_data.drop(columns=['Month_End'], inplace=True)
        print(f"Merged data for {budgetnavn}:\n{merged_data.head()}")

        # Merge with averaged budgets on date
        merged_data = pd.merge(merged_data, Averaged_budgets, on='Dato', how='left', suffixes=('', '_Avg'))
        print(f"Final merged data for {budgetnavn}:\n{merged_data.head()}")

        # Create line chart
        plt.figure(figsize=(12, 6))
        plt.plot(merged_data['Dato'], merged_data['Budget'], marker='o', label='Budget')
        plt.plot(merged_data['Dato'], merged_data['Budgetbeloeb_Vedroerer'], marker='o', label='Budgetbeloeb_Vedroerer')
        plt.plot(merged_data['Dato'], merged_data['OprindeligtBudgetbeloeb'], marker='o', label='OprindeligtBudgetbeloeb')
        plt.plot(merged_data['Dato'], merged_data['Averaged_budgets'], marker='o', label='Averaged_budgets')
        plt.plot(merged_data['Dato'], merged_data['Forbrug'], marker='o', label='Forbrug')
        plt.title(f"{budgetnavn} - Budgets and Actuals Over Time")
        plt.xlabel('Date')
        plt.ylabel('Amount')
        plt.legend()
        plt.xticks(rotation=45)
        plt.tight_layout()
        filename_line = f"{budgetnavn}_combined_line_chart.png"
        plt.savefig(os.path.join(output_dir, filename_line))
        plt.close()
        print(f"Saved line chart: {filename_line}")

        # --- Addition starts here ---
        # Calculate total annual amounts for averaged budgets and Forbrug
        total_budget = merged_data['Averaged_budgets'].sum()
        total_forbrug = merged_data['Forbrug'].sum()

        # Calculate percentage difference compared to Forbrug
        percentage_difference = safe_utilization(total_forbrug, total_budget) - 100  # Percentage over or under budget

        # Create a DataFrame for plotting
        df_totals = pd.DataFrame({
            'Type': ['Averaged Budget', 'Forbrug'],
            'Amount': [total_budget, total_forbrug]
        })

        # Create column chart
        plt.figure(figsize=(6, 6))
        bars = plt.bar(df_totals['Type'], df_totals['Amount'], color=['blue', 'orange'])
        plt.title(f"{budgetnavn} - Total Annual Amounts")
        plt.ylabel('Amount')
        # Annotate bars with amounts
        for bar in bars:
            height = bar.get_height()
            plt.annotate(f'{height:,.2f}', xy=(bar.get_x() + bar.get_width() / 2, height),
                         xytext=(0, 5), textcoords="offset points", ha='center', va='bottom')

        # Add percentage difference as a highlighted note
        note_text = f'Percentage Difference:\n{percentage_difference:.2f}%'
        # Adjust the position as needed
        plt.annotate(note_text,
                     xy=(0.5, max(df_totals['Amount']) * 0.6),
                     xycoords='data',
                     bbox=dict(boxstyle="round,pad=0.5", fc="yellow", ec="black", lw=1),
                     ha='center',
                     fontsize=12)
        plt.tight_layout()
        filename_column = f"{budgetnavn}_annual_totals_column_chart.png"
        plt.savefig(os.path.join(output_dir, filename_column))
        plt.close()
        print(f"Saved column chart: {filename_column}")
        # --- Addition ends here ---

    except Exception as e:
        print(f"Error processing {budgetnavn}: {e}")

# --- Addition starts here ---

print("Creating average budget across all Budgetnavn...")

# Aggregate budget data across all Budgetnavn by 'Dato' (calculating the mean)
average_budget_data = budget_aggregated.groupby('Dato').agg({
    'Budget': 'mean',
    'Budgetbeloeb_Vedroerer': 'mean',
    'OprindeligtBudgetbeloeb': 'mean',
    'Averaged_budgets': 'mean'
}).reset_index()

print(f"check 1:\n{average_budget_data.head()}")

# Merge with financial data on date
merged_avg_data = pd.merge(average_budget_data, financial_monthly, left_on='Dato', right_on='Month_End', how='left')
merged_avg_data['Forbrug'] = merged_avg_data['Forbrug'].fillna(0)
merged_avg_data.drop(columns=['Month_End'], inplace=True)

print(f"check 2:\n{merged_avg_data.head()}")

# Create line chart for the average budgets and actual spending
plt.figure(figsize=(12, 6))
plt.plot(merged_avg_data['Dato'], merged_avg_data['Budget'], marker='o', label='Average Budget')
plt.plot(merged_avg_data['Dato'], merged_avg_data['Budgetbeloeb_Vedroerer'], marker='o', label='Average Budgetbeloeb_Vedroerer')
plt.plot(merged_avg_data['Dato'], merged_avg_data['OprindeligtBudgetbeloeb'], marker='o', label='Average OprindeligtBudgetbeloeb')
plt.plot(merged_avg_data['Dato'], merged_avg_data['Averaged_budgets'], marker='o', label='Averaged Budget')
plt.plot(merged_avg_data['Dato'], merged_avg_data['Forbrug'], marker='o', label='Forbrug')
plt.title("Average Budgets and Actuals Over Time")
plt.xlabel('Date')
plt.ylabel('Amount')
plt.legend()
plt.xticks(rotation=45)
plt.tight_layout()
filename_line_avg = "Average_Budgets_and_Actuals_Line_Chart.png"
plt.savefig(os.path.join(output_dir, filename_line_avg))
plt.close()
print(f"Saved line chart: {filename_line_avg}")

# Calculate total annual amounts for average budgets and Forbrug
total_budget_avg = merged_avg_data['Averaged_budgets'].sum()
total_forbrug_avg = merged_avg_data['Forbrug'].sum()

# Calculate percentage difference compared to Forbrug
percentage_difference_avg = safe_utilization(total_forbrug_avg, total_budget_avg) - 100  # Percentage over or under budget

# Create a DataFrame for plotting
df_totals_avg = pd.DataFrame({
    'Type': ['Average Budget', 'Forbrug'],
    'Amount': [total_budget_avg, total_forbrug_avg]
})

# Create column chart for average budgets
plt.figure(figsize=(6, 6))
bars = plt.bar(df_totals_avg['Type'], df_totals_avg['Amount'], color=['green', 'orange'])
plt.title("Average Budget vs Total Actual Spending")
plt.ylabel('Amount')
# Annotate bars with amounts
for bar in bars:
    height = bar.get_height()
    plt.annotate(f'{height:,.2f}', xy=(bar.get_x() + bar.get_width() / 2, height),
                 xytext=(0, 5), textcoords="offset points", ha='center', va='bottom')

# Add percentage difference as a highlighted note
note_text = f'Percentage Difference:\n{percentage_difference_avg:.2f}%'
# Adjust the position as needed
plt.annotate(note_text,
             xy=(0.5, max(df_totals_avg['Amount']) * 0.6),
             xycoords='data',
             bbox=dict(boxstyle="round,pad=0.5", fc="yellow", ec="black", lw=1),
             ha='center',
             fontsize=12)
plt.tight_layout()
filename_column_avg = "Average_Budgets_and_Actuals_Column_Chart.png"
plt.savefig(os.path.join(output_dir, filename_column_avg))
plt.close()
print(f"Saved column chart: {filename_column_avg}")

# --- Addition ends here ---
