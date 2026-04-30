import pandas as pd
import os

file_path = r'C:\Users\User\Downloads\data (5).xlsx'
output_path = r'C:\Users\User\pivoted_data_final.csv'

try:
    # --- Step 1: Read with multi-level header ---
    df = pd.read_excel(file_path, header=[0, 1])

    # --- Step 2: Identify ASIN and URL column names ---
    url_col = df.columns[0]
    asin_col = df.columns[1]

    # --- Step 3: Set ASIN as index and drop URL column ---
    df = df.set_index(asin_col)
    df = df.drop(columns=[url_col])
    df.index.name = 'ASIN' # Clean up index name

    # --- Step 4: Stack the Date level (level 0) of columns ---
    # This moves the dates from columns to a new level in the index
    stacked_df = df.stack(level=0)
    stacked_df.index.set_names(['ASIN', 'Date'], inplace=True) # Name the new index level

    # --- Step 5: Reset index and melt metrics ---
    # Now we have a DataFrame with ASIN, Date as index and metrics as columns
    long_df = stacked_df.reset_index()
    
    # Melt the metric columns
    final_melted = long_df.melt(
        id_vars=['ASIN', 'Date'],
        var_name='Metric',
        value_name='Value'
    )

    # --- Step 6: Clean and Pivot ---
    final_melted['Date'] = pd.to_datetime(final_melted['Date'], errors='coerce').dt.date
    final_melted = final_melted.dropna(subset=['ASIN', 'Value', 'Date', 'Metric'])
    final_melted = final_melted[~final_melted['ASIN'].astype(str).str.contains('Total', na=False, case=False)]
    final_melted = final_melted[~final_melted['Metric'].astype(str).str.contains('Unnamed:', na=False)]
    final_melted = final_melted[final_melted['Metric'].astype(str).str.strip() != '-']

    final_pivot = final_melted.pivot_table(
        index=['ASIN', 'Metric'],
        columns='Date',
        values='Value',
        aggfunc='sum'
    )

    # --- Step 7: Sort metrics and Save ---
    metric_level = final_pivot.index.get_level_values('Metric')
    unique_metrics = metric_level.unique().tolist()
    
    ppc_spend_col = next((m for m in unique_metrics if 'ppc spend' in str(m).lower()), None)

    if ppc_spend_col:
        unique_metrics.remove(ppc_spend_col)
        metrics_order = unique_metrics + [ppc_spend_col]
        final_pivot = final_pivot.reindex(metrics_order, level='Metric')

    final_pivot.to_csv(output_path)
    print(f"Processing complete. The final data has been saved to: {output_path}")

except Exception as e:
    print(f"An error occurred: {e}")
