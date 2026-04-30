import pandas as pd
import os

def combine_sales_reports(attribution_file_path, creator_file_path):
    # --- Process Attribution Report ---
    try:
        df_attr = pd.read_excel(attribution_file_path)
    except FileNotFoundError:
        print(f"Error: Attribution file not found at {attribution_file_path}")
        return
    except Exception as e:
        print(f"Error reading attribution file {attribution_file_path}: {e}")
        return

    # Data Cleaning for Attribution Report
    if '14 Day Product Sales' in df_attr.columns:
        df_attr['14 Day Product Sales'] = df_attr['14 Day Product Sales'].astype(str).str.replace('$', '', regex=False).str.replace(',', '', regex=False)
        df_attr['14 Day Product Sales'] = pd.to_numeric(df_attr['14 Day Product Sales'], errors='coerce').fillna(0)
    else:
        print(f"Warning: '14 Day Product Sales' column not found in {attribution_file_path}")
        return

    df_attr['Date'] = pd.to_datetime(df_attr['Date'])

    # Filter by Advertiser Country == 'US' if column exists
    if 'Advertiser Country' in df_attr.columns:
        df_attr = df_attr[df_attr['Advertiser Country'] == 'US']

    # Select and rename columns for consistency
    df_attr_sales = df_attr[['Advertised ASIN', 'Date', '14 Day Product Sales']].copy()
    df_attr_sales.rename(columns={'Advertised ASIN': 'ASIN', '14 Day Product Sales': 'Sales'}, inplace=True)

    # --- Process Creator Report ---
    try:
        df_creator = pd.read_csv(creator_file_path, encoding='utf-8-sig')
    except UnicodeDecodeError:
        df_creator = pd.read_csv(creator_file_path, encoding='cp1251')
    except FileNotFoundError:
        print(f"Error: Creator file not found at {creator_file_path}")
        return
    except Exception as e:
        print(f"Error reading creator file {creator_file_path}: {e}")
        return

    # Data Cleaning for Creator Report
    if 'Sales' in df_creator.columns:
        df_creator['Sales'] = df_creator['Sales'].astype(str).str.replace('$', '', regex=False).str.replace(',', '', regex=False)
        df_creator['Sales'] = pd.to_numeric(df_creator['Sales'], errors='coerce').fillna(0)
    else:
        print(f"Warning: 'Sales' column not found in {creator_file_path}")
        return

    df_creator['Date'] = pd.to_datetime(df_creator['Date'], format='%d-%b-%Y')

    # Select columns for consistency
    df_creator_sales = df_creator[['ASIN', 'Date', 'Sales']].copy()

    # --- Combine DataFrames ---
    combined_sales_df = pd.concat([df_attr_sales, df_creator_sales], ignore_index=True)

    # Group by ASIN and Date and sum sales
    combined_sales_df = combined_sales_df.groupby(['ASIN', 'Date'])['Sales'].sum().reset_index()

    # Create Pivot Table
    pivot_table = combined_sales_df.pivot_table(
        index='ASIN',
        columns='Date',
        values='Sales',
        aggfunc='sum',
        fill_value=0
    )

    # Format date columns
    pivot_table.columns = pivot_table.columns.map(lambda x: x.strftime('%Y-%m-%d'))

    # Save Output
    output_filename = os.path.join(os.path.dirname(attribution_file_path), "Combined_Sales_Report.csv")
    pivot_table.to_csv(output_filename)
    print(f"Combined Sales Report saved to: {output_filename}")

# Define file paths
attribution_file = r"C:\Users\User\Downloads\Amazon_Attribution_Promoted_product_report (24).xlsx"
creator_file = r"C:\Users\User\Downloads\result_0_450.csv"

# Execute the function
combine_sales_reports(attribution_file, creator_file)
