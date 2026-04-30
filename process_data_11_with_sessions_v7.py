import pandas as pd
import os

def process_file_with_sessions(file_path, output_filename, exchange_rate):
    """
    Processes a sales data file, includes sessions, converts sales to USD, and returns a flattened DataFrame.
    """
    try:
        # Read the entire sheet as raw data
        raw_df = pd.read_excel(file_path, header=None)

        # Identify header rows (assuming first two rows are headers)
        header_row1 = raw_df.iloc[0]
        header_row2 = raw_df.iloc[1]

        # Create a list to store the new column names
        new_columns = []
        date_metric_columns_to_melt = []

        # Handle the first two columns which are not part of the date/metric pattern
        new_columns.append('Image')
        new_columns.append('ASIN')

        # Iterate through the columns starting from the third column (index 2)
        # to construct the multi-level header
        current_date = None
        for i in range(2, len(raw_df.columns)):
            date_val = header_row1[i]
            metric_val = str(header_row2[i]).strip()

            # Update current_date if a new date is encountered in the first header row
            if pd.notna(date_val) and isinstance(date_val, pd.Timestamp):
                current_date = date_val
            
            # Only process if we have a valid date and a meaningful metric
            if current_date is not None and 'Unnamed' not in metric_val and metric_val != 'nan':
                date_str = current_date.strftime('%Y-%m-%d')
                col_name = f"{date_str}_{metric_val}"
                new_columns.append(col_name)
                date_metric_columns_to_melt.append(col_name)
            else:
                # For columns that don't fit the date_metric pattern (e.g., trailing totals)
                # We'll just use the metric name if it's not 'Unnamed' or 'nan'
                if 'Unnamed' not in metric_val and metric_val != 'nan':
                    new_columns.append(metric_val)
                else:
                    new_columns.append(f"col_{i}") # Fallback for truly unhandled columns


        # Read the data, skipping the header rows
        df = pd.read_excel(file_path, header=None, skiprows=2)
        
        # Drop columns that are completely empty
        df = df.dropna(axis=1, how='all')
        
        # Adjust new_columns to match the actual number of columns in df
        if len(new_columns) > len(df.columns):
            new_columns = new_columns[:len(df.columns)]
        elif len(new_columns) < len(df.columns):
            for j in range(len(df.columns) - len(new_columns)):
                new_columns.append(f"extra_col_{j}")

        df.columns = new_columns
        
        # Rename the first two columns
        df = df.rename(columns={df.columns[0]: 'Image', df.columns[1]: 'ASIN'})
        
        # Melt the dataframe to unpivot
        id_vars = ['Image', 'ASIN']
        
        df_melted = pd.melt(df, id_vars=id_vars, value_vars=date_metric_columns_to_melt, var_name='Date_Metric', value_name='Value')

        # Split 'Date_Metric' into 'Date' and 'Metric'
        df_melted[['Date', 'Metric']] = df_melted['Date_Metric'].str.split('_', n=1, expand=True)
        df_melted = df_melted.drop(columns=['Date_Metric', 'Image'])

        # Strip whitespace from the 'Metric' column
        df_melted['Metric'] = df_melted['Metric'].str.strip()

        # Filter for the desired metrics, including 'Total Sessions'
        metrics_to_keep = ['Total Sales', 'Units Sold', 'Orders', 'Total Sessions']
        df_filtered = df_melted[df_melted['Metric'].isin(metrics_to_keep)]

        # Convert 'Value' to numeric, coercing errors
        df_filtered['Value'] = pd.to_numeric(df_filtered['Value'], errors='coerce')

        # Convert 'Total Sales' to USD
        df_filtered.loc[df_filtered['Metric'] == 'Total Sales', 'Value'] *= exchange_rate
        df_filtered.loc[df_filtered['Metric'] == 'Total Sales', 'Metric'] = 'Total Sales (USD)'

        # Pivot the table
        pivot_table = df_filtered.pivot_table(index=['ASIN', 'Metric'], columns='Date', values='Value', aggfunc='first')

        # Save the pivot table
        output_path = os.path.join(os.path.expanduser("~"), "Downloads", output_filename)
        pivot_table.to_excel(output_path)
        
        print(f"Обработанный файл с сессиями сохранен в {output_path}")

    except Exception as e:
        print(f"Произошла ошибка: {e}")

# Process data (11).xlsx
file_path_11 = os.path.join('C:', os.sep, 'Users', 'User', 'Downloads', 'data (11).xlsx')
exchange_rate = 0.72
process_file_with_sessions(file_path_11, 'data_11_with_sessions.xlsx', exchange_rate)
