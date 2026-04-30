import pandas as pd
import os

file_path = r'C:\Users\User\Downloads\data (5).xlsx'
output_path = r'C:\Users\User\pivoted_data_final.csv' # New output name

try:
    # --- Step 1: Read with multi-level header ---
    df = pd.read_excel(file_path, header=[0, 1])

    # --- Step 2: Identify and rename identifier columns ---
    # The ASIN is in the second column. Let's name it 'ASIN'.
    asin_col_tuple = df.columns[1] 
    df = df.rename(columns={asin_col_tuple: 'ASIN'})
    
    # Drop the first column (image URLs) as it's not needed.
    df = df.drop(columns=[df.columns[0]])

    # --- Step 3: Melt the DataFrame ---
    # id_vars is now 'ASIN'. The rest are value variables.
    melted_df = df.melt(id_vars=['ASIN'], var_name=['Date', 'Metric'], value_name='Value')

    # --- Step 4: Clean up the melted data ---
    melted_df['Date'] = pd.to_datetime(melted_df['Date'], errors='coerce').dt.date
    melted_df = melted_df.dropna(subset=['ASIN', 'Value', 'Date', 'Metric'])
    melted_df = melted_df[~melted_df['ASIN'].astype(str).str.contains('Total', na=False, case=False)]
    melted_df = melted_df[~melted_df['Metric'].astype(str).str.contains('Unnamed:', na=False)]
    # This extra metric '-' was also identified in the inspection
    melted_df = melted_df[melted_df['Metric'].astype(str).str.strip() != '-']

    # --- Step 5: Create the final pivot table ---
    final_pivot = melted_df.pivot_table(
        index=['ASIN', 'Metric'], 
        columns='Date', 
        values='Value', 
        aggfunc='sum'
    )

    # --- Step 6: Sort metrics as requested ---
    metric_level = final_pivot.index.get_level_values('Metric')
    unique_metrics = metric_level.unique().tolist()
    
    # Find 'PPC Spend' case-insensitively
    ppc_spend_col = next((m for m in unique_metrics if 'ppc spend' in str(m).lower()), None)

    if ppc_spend_col:
        # Remove it from the list and append it to the end
        unique_metrics.remove(ppc_spend_col)
        metrics_order = unique_metrics + [ppc_spend_col]
        final_pivot = final_pivot.reindex(metrics_order, level='Metric')

    # --- Step 7: Save the result ---
    final_pivot.to_csv(output_path)
    print(f"Processing complete. The final, correctly identified and ordered data has been saved to: {output_path}")

except Exception as e:
    print(f"An error occurred: {e}")
