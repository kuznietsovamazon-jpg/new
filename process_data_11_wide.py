
import pandas as pd
import numpy as np

def process_wide_report(file_path):
    """
    Processes a complex wide-format Excel report into multiple pivoted CSV files.
    Handles non-date columns like 'Total' in the header.
    """
    try:
        # Step 1: Read the Excel file with a multi-level header.
        df = pd.read_excel(file_path, header=[0, 1])

        # Step 2: Process the multi-level column headers.
        new_cols = []
        valid_columns_map = {} # To store original columns that are valid

        for i, col in enumerate(df.columns):
            original_col_name = col
            try:
                # Attempt to convert the first level of the header to a date.
                date_part = pd.to_datetime(col[0]).strftime('%Y-%m-%d')
                metric_part = col[1]
                new_col_name = f"{date_part}_{metric_part}"
                new_cols.append(new_col_name)
                valid_columns_map[new_col_name] = original_col_name
            except (ValueError, TypeError):
                # If conversion fails, it's not a date (e.g., 'Day', 'Unnamed: 1', 'Total').
                # We'll keep the original column name for now if it's one of the first two.
                if i < 2:
                     new_cols.append(col[1] if pd.notna(col[1]) else col[0])
                     valid_columns_map[new_cols[-1]] = original_col_name
                # Otherwise, we ignore it (like the 'Total' columns)

        # Filter the DataFrame to only include the columns we processed
        df = df[[valid_columns_map[c] for c in new_cols]]
        df.columns = new_cols

        # Rename the first two columns based on inspection
        df.rename(columns={df.columns[0]: 'Item', df.columns[1]: 'ASIN'}, inplace=True)
        
        # Step 3: Melt the DataFrame to transform it from wide to long format.
        id_vars = ['ASIN', 'Item']
        value_vars = [c for c in df.columns if c not in id_vars]
        melted_df = df.melt(id_vars=id_vars, value_vars=value_vars, var_name='variable', value_name='value')

        # Step 4: Split the 'variable' column into 'Date' and 'Metric'.
        # Use n=1 to split only on the first underscore, in case metrics have underscores.
        melted_df[['Date', 'Metric']] = melted_df['variable'].str.split('_', n=1, expand=True)
        
        # Drop unnecessary columns and rows with missing critical data
        melted_df.drop(columns=['variable', 'Item'], inplace=True)
        melted_df.dropna(subset=['ASIN', 'value', 'Metric'], inplace=True)
        
        # Convert value to numeric, coercing errors
        melted_df['value'] = pd.to_numeric(melted_df['value'], errors='coerce')
        melted_df.dropna(subset=['value'], inplace=True)

        # Define the metrics we want to extract
        metrics_to_pivot = ['Sales', 'Units', 'Orders', 'Sessions']
        
        # Step 5: Create and save a pivot table for each metric.
        for metric in metrics_to_pivot:
            metric_df = melted_df[melted_df['Metric'].str.contains(metric, case=False, na=False)]
            
            if not metric_df.empty:
                pivot_df = metric_df.pivot_table(
                    index='ASIN', 
                    columns='Date', 
                    values='value',
                    aggfunc='sum'
                )
                output_filename = f'pivoted_{metric.lower()}_report.csv'
                pivot_df.to_csv(output_filename)
                print(f"Successfully created '{output_filename}'")
            else:
                print(f"No data found for metric: '{metric}'")

    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    file_to_process = r'C:\Users\User\Downloads\data (11).xlsx'
    process_wide_report(file_to_process)
