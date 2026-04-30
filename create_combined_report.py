import pandas as pd
import os

def process_sales_file(file_path):
    """
    Processes a sales data file and returns a flattened DataFrame.
    """
    # Read the header rows to get dates and metric names
    header_df = pd.read_excel(file_path, header=None, nrows=2)
    
    # Forward fill the dates in the first row
    dates = header_df.iloc[0].ffill()
    
    # Get the metrics from the second row
    metrics = header_df.iloc[1]
    
    # Create new column names
    new_columns = []
    current_date = None
    for i in range(len(dates)):
        if pd.notna(dates[i]) and isinstance(dates[i], pd.Timestamp):
            current_date = dates[i].strftime('%Y-%m-%d')
        
        metric_name = str(metrics[i])
        if current_date and 'Unnamed' not in metric_name:
            new_columns.append(f"{current_date}_{metric_name}")
        else:
            new_columns.append(metric_name)

    # Read the data, skipping the header rows
    df = pd.read_excel(file_path, header=None, skiprows=2)
    
    # Drop columns that are completely empty
    df = df.dropna(axis=1, how='all')
    
    df.columns = new_columns[:len(df.columns)]
    
    # Rename the first two columns
    df = df.rename(columns={df.columns[0]: 'Image', df.columns[1]: 'ASIN'})
    
    # Melt the dataframe to unpivot
    id_vars = ['Image', 'ASIN']
    value_vars = [col for col in df.columns if col not in id_vars and 'Total' not in col and 'nan' not in col]

    df_melted = pd.melt(df, id_vars=id_vars, value_vars=value_vars, var_name='Date_Metric', value_name='Value')
    
    # Split 'Date_Metric' into 'Date' and 'Metric'
    df_melted[['Date', 'Metric']] = df_melted['Date_Metric'].str.split('_', n=1, expand=True)
    df_melted = df_melted.drop(columns=['Date_Metric', 'Image'])
    
    df_melted['Metric'] = df_melted['Metric'].str.strip()
    
    metrics_to_keep = ['Total Sales', 'Units Sold', 'Orders']
    df_filtered = df_melted[df_melted['Metric'].isin(metrics_to_keep)]
    
    flat_table = df_filtered.pivot_table(index=['ASIN', 'Date'], columns='Metric', values='Value', aggfunc='first').reset_index()
    
    return flat_table

def process_ads_file(file_path):
    """
    Processes the advertising data file and returns a flattened DataFrame.
    """
    df = pd.read_excel(file_path)
    df = df.rename(columns={'Child ASIN': 'ASIN'})
    df = df[df['ASIN'] != 'Total']
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    df = df.dropna(subset=['Date'])
    df['Date'] = df['Date'].dt.date
    df = df[['ASIN', 'Date', 'Spend']]
    return df

def combine_and_convert():
    """
    Combines sales and advertising data, converts to USD, and creates a pivot table.
    """
    try:
        # File paths
        sales_file_10 = os.path.join('C:', os.sep, 'Users', 'User', 'Downloads', 'data (10).xlsx')
        sales_file_11 = os.path.join('C:', os.sep, 'Users', 'User', 'Downloads', 'data (11).xlsx')
        ads_file_12 = os.path.join('C:', os.sep, 'Users', 'User', 'Downloads', 'data (12).xlsx')
        
        # Process sales files
        df10 = process_sales_file(sales_file_10)
        df11 = process_sales_file(sales_file_11)
        
        # Process ads file
        df12 = process_ads_file(ads_file_12)
        
        # Combine sales data
        sales_df = pd.concat([df10, df11])
        
        # Convert Date columns to datetime objects for merging
        sales_df['Date'] = pd.to_datetime(sales_df['Date']).dt.date
        df12['Date'] = pd.to_datetime(df12['Date']).dt.date

        # Merge sales and ads data
        combined_df = pd.merge(sales_df, df12, on=['ASIN', 'Date'], how='outer')
        
        # Exchange rate
        exchange_rate = 0.72
        
        # Convert to numeric and then to USD
        combined_df['Total Sales'] = pd.to_numeric(combined_df['Total Sales'], errors='coerce')
        combined_df['Spend'] = pd.to_numeric(combined_df['Spend'], errors='coerce')
        combined_df['Total Sales (USD)'] = combined_df['Total Sales'] * exchange_rate
        combined_df['Spend (USD)'] = combined_df['Spend'] * exchange_rate
        
        # Drop original currency columns
        combined_df = combined_df.drop(columns=['Total Sales', 'Spend'])
        
        # Unpivot the combined dataframe
        id_vars = ['ASIN', 'Date']
        value_vars = ['Total Sales (USD)', 'Units Sold', 'Orders', 'Spend (USD)']
        final_df = pd.melt(combined_df, id_vars=id_vars, value_vars=value_vars, var_name='Metric', value_name='Value')
        
        # Create the final pivot table
        pivot_table = final_df.pivot_table(index=['ASIN', 'Metric'], columns='Date', values='Value', aggfunc='first')
        
        # Save the final report
        output_path = os.path.join(os.path.expanduser("~"), "Downloads", "combined_report.xlsx")
        pivot_table.to_excel(output_path)
        
        print(f"Объединенный и конвертированный отчет сохранен в {output_path}")

    except Exception as e:
        print(f"Произошла ошибка: {e}")

if __name__ == "__main__":
    combine_and_convert()