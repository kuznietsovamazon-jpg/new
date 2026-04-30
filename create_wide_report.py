import pandas as pd
import os
import sys

def process_data_sortable(file_path, output_filename):
    """
    Processes the Excel file to create a pivot table that is easier to sort.
    """
    try:
        # Read the header rows to get dates and metric names
        header_df = pd.read_excel(file_path, header=None, nrows=2)
        
        # Forward fill the dates in the first row
        dates = header_df.iloc[0].ffill()
        
        # Get the metrics from the second row
        metrics = header_df.iloc[1]
        
        # Create new column names
        new_columns = []
        for i in range(len(dates)):
            if isinstance(dates[i], pd.Timestamp):
                date_str = dates[i].strftime('%Y-%m-%d')
            else:
                date_str = str(dates[i])
            new_columns.append(f"{date_str}_{metrics[i]}")
            
        # Read the data, skipping the header rows
        df = pd.read_excel(file_path, header=None, skiprows=2)
        df.columns = new_columns
        
        # Rename the first two columns
        df = df.rename(columns={df.columns[0]: 'Image', df.columns[1]: 'ASIN'})
        
        # Melt the dataframe to unpivot
        id_vars = ['Image', 'ASIN']
        value_vars = [col for col in df.columns if col not in id_vars]
        df_melted = pd.melt(df, id_vars=id_vars, value_vars=value_vars, var_name='Date_Metric', value_name='Value')
        
        # Split 'Date_Metric' into 'Date' and 'Metric'
        df_melted[['Date', 'Metric']] = df_melted['Date_Metric'].str.split('_', n=1, expand=True)
        df_melted = df_melted.drop(columns=['Date_Metric', 'Image'])
        
        # Strip whitespace from the 'Metric' column
        df_melted['Metric'] = df_melted['Metric'].str.strip()
        
        # Filter for the desired metrics
        metrics_to_keep = ['Total Sales', 'Units Sold', 'Orders']
        df_filtered = df_melted[df_melted['Metric'].isin(metrics_to_keep)]

        # Pivot the table to have metrics as columns
        pivot_table = df_filtered.pivot_table(index='ASIN', columns=['Date', 'Metric'], values='Value', aggfunc='first')
        
        # Save the pivot table
        output_path = os.path.join(os.path.expanduser("~"), "Downloads", output_filename)
        pivot_table.to_excel(output_path)
        
        print(f"Таблица, с датами вверху, сохранена в {output_path}")

    except Exception as e:
        print(f"Произошла ошибка: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python create_wide_report.py <input_file> <output_file>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    process_data_sortable(input_file, output_file)
