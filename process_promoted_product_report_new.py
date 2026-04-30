import pandas as pd
import os
import re

def process_promoted_product_report(file_path):
    try:
        df = pd.read_excel(file_path)

        # Filter for 'Advertiser Country' == 'US'
        if 'Advertiser Country' in df.columns:
            df = df[df['Advertiser Country'] == 'US'].copy()
        else:
            print("Warning: 'Advertiser Country' column not found. Skipping country filtering.")

        # Convert 'Date' to datetime objects
        df['Date'] = pd.to_datetime(df['Date']).dt.date

        # Create 'Grouped_Campaign_Name'
        df['Grouped_Campaign_Name'] = df['Campaign Name'].apply(
            lambda x: "Adv Campaigns" if isinstance(x, str) and x.lower().startswith("adv") else x
        )

        # Identify the correct sales column
        sales_column = None
        for col in ['14 Day Product Sales', '14 Day Sales', 'Sales']:
            if col in df.columns:
                sales_column = col
                break
        
        if not sales_column:
            print(f"Error: No sales column found in {file_path}. Expected '14 Day Product Sales', '14 Day Sales', or 'Sales'.")
            return None

        # Clean and convert sales column to numeric
        df[sales_column] = df[sales_column].astype(str).str.replace('$', '').str.replace(',', '').astype(float)

        # Pivot the table for all campaigns
        pivot_df_all = df.pivot_table(
            index=['Advertised ASIN', 'Grouped_Campaign_Name'],
            columns='Date',
            values=sales_column,
            aggfunc='sum',
            fill_value=0
        )
        pivot_df_all.columns = [col.strftime('%Y-%m-%d') for col in pivot_df_all.columns]

        # Pivot the table for "Adv Campaigns" only
        df_adv_campaigns = df[df['Grouped_Campaign_Name'] == "Adv Campaigns"].copy()
        if not df_adv_campaigns.empty:
            pivot_df_adv = df_adv_campaigns.pivot_table(
                index=['Advertised ASIN', 'Grouped_Campaign_Name'],
                columns='Date',
                values=sales_column,
                aggfunc='sum',
                fill_value=0
            )
            pivot_df_adv.columns = [col.strftime('%Y-%m-%d') for col in pivot_df_adv.columns]
        else:
            pivot_df_adv = pd.DataFrame() # Empty DataFrame if no "Adv Campaigns"

        # Generate output file names
        base_name = os.path.basename(file_path)
        name_without_ext = os.path.splitext(base_name)[0]

        output_path_all = os.path.join(os.path.dirname(file_path), f"promoted_product_report_by_asin_and_campaign_{name_without_ext}.csv")
        output_path_adv = os.path.join(os.path.dirname(file_path), f"promoted_product_report_adv_campaigns_{name_without_ext}.csv")

        pivot_df_all.to_csv(output_path_all, encoding='utf-8-sig')
        print(f"Processed promoted product report (all campaigns) saved to: {output_path_all}")

        if not pivot_df_adv.empty:
            pivot_df_adv.to_csv(output_path_adv, encoding='utf-8-sig')
            print(f"Processed promoted product report (Adv Campaigns only) saved to: {output_path_adv}")
        else:
            print("No 'Adv Campaigns' found to generate a separate report.")

        return output_path_all, output_path_adv

    except Exception as e:
        print(f"Error processing file {file_path}: {e}")
        return None

# Example usage:
file_path = r'C:\Users\User\Downloads\Amazon_Attribution_Promoted_product_report (21).xlsx'
process_promoted_product_report(file_path)
