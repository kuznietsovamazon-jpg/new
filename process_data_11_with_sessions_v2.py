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

        new_columns = ['Image', 'ASIN']
        date_metric_columns_to_melt = []

        current_date = None
        for i in range(2, len(raw_df.columns)): # Start from the third column
            # Get date from the first header row
            if pd.notna(header_row1[i]):
                current_date = header_row1[i]
            
            # Get metric from the second header row
            metric_name = str(header_row2[i]).strip()

            if isinstance(current_date, pd.Timestamp) and 'Unnamed' not in metric_name and metric_name != 'nan':
                col_name = f"{current_date.strftime('%Y-%m-%d')}_{metric_name}"
                new_columns.append(col_name)
                date_metric_columns_to_melt.append(col_name)
            elif 'Unnamed' not in metric_name and metric_name != 'nan': # For the first two columns, if they are not dates
                new_columns.append(metric_name)
            else:
                new_columns.append(f"col_{i}") # Placeholder for unhandled columns

        # Read the data, skipping the header rows
        df = pd.read_excel(file_path, header=None, skiprows=2)
        
        # Drop columns that are completely empty
        df = df.dropna(axis=1, how='all')
        
        # Ensure df has enough columns for new_columns
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
