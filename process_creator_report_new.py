import pandas as pd
import os

def process_creator_report(file_path):
    try:
        df = pd.read_csv(file_path, encoding='utf-8-sig')
    except UnicodeDecodeError:
        df = pd.read_csv(file_path, encoding='cp1251')

    # Data Cleaning: Remove '$' and ',' from numeric columns and convert to float
    numeric_cols = ['Spend', 'Sales', 'Commission Rate']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = df[col].astype(str).str.replace('$', '', regex=False).str.replace(',', '', regex=False)
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    # Convert 'Date' column to datetime objects
    df['Date'] = pd.to_datetime(df['Date'], format='%d-%b-%Y')

    # Calculate 'Commission Amount'
    df['Commission Amount'] = df['Sales'] * (df['Commission Rate'] / 100)

    # Define metrics to pivot
    metrics = ['Clicks', 'Orders', 'Sales', 'Spend', 'Commission Amount']

    base_name = os.path.splitext(os.path.basename(file_path))[0]
    output_dir = os.path.dirname(file_path)

    for metric in metrics:
        # Group by ASIN and Date, then sum the metric
        grouped_df = df.groupby(['ASIN', 'Date'])[metric].sum().reset_index()

        # Pivot the table
        pivot_df = grouped_df.pivot_table(
            index='ASIN',
            columns='Date',
            values=metric,
            aggfunc='sum',
            fill_value=0
        )

        # Flatten the columns for better readability (optional, but good for single-level index)
        pivot_df.columns = pivot_df.columns.map(lambda x: x.strftime('%Y-%m-%d'))

        output_filename = os.path.join(output_dir, f"Total_Creator_{metric.replace(' ', '_')}_by_ASIN_Date_{base_name}.csv")
        pivot_df.to_csv(output_filename)
        print(f"Successfully created {metric} report: {output_filename}")

# Example usage:
file_path = r"C:\Users\User\Downloads\result_0_450.csv"
process_creator_report(file_path)
