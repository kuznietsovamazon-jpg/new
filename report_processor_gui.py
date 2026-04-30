import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
import os
import numpy as np
from io import BytesIO

# --- Processing Functions (adapted for file paths) ---

def process_returns_report_logic(file_path):
    try:
        # Read the file
        try:
            df = pd.read_csv(file_path, encoding='utf-8-sig')
        except UnicodeDecodeError:
            df = pd.read_csv(file_path, encoding='cp1251')

        # Convert 'return-date' to datetime and extract date only
        df['return-date'] = pd.to_datetime(df['return-date']).dt.date

        # Categorize returns
        df['return_category'] = df['detailed-disposition'].apply(
            lambda x: 'SELLABLE' if x == 'SELLABLE' else 'UNSELLABLE'
        )

        # Group by ASIN, return_category, and return-date, then sum quantity
        grouped_df = df.groupby(['asin', 'return_category', 'return-date'])['quantity'].sum().reset_index()

        # Pivot the table
        pivot_df = grouped_df.pivot_table(
            index=['asin', 'return_category'],
            columns='return-date',
            values='quantity',
            fill_value=0
        )

        # Format column names to string for CSV output
        pivot_df.columns = pivot_df.columns.map(lambda x: x.strftime('%Y-%m-%d'))

        return pivot_df, "Returns Report processed successfully!"

    except Exception as e:
        return None, f"Error processing Returns Report: {e}"

def process_attribution_report_logic(file_path):
    try:
        df = pd.read_excel(file_path)

        # Data Cleaning: Remove '$' and ',' from numeric columns and convert to float
        numeric_cols = ['14 Day Product Sales']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = df[col].astype(str).str.replace('$', '', regex=False).str.replace(',', '', regex=False)
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            else:
                return None, f"Error: Required column '{col}' not found in Attribution Report."


        # Convert 'Date' column to datetime objects
        df['Date'] = pd.to_datetime(df['Date'])

        # Filtering: Advertiser Country == 'US' if column exists
        if 'Advertiser Country' in df.columns:
            df = df[df['Advertiser Country'] == 'US']

        # --- Campaign Grouping Logic ---
        df['Grouped_Campaign_Name'] = np.where(
            df['Campaign Name'].str.lower().str.startswith('adv'),
            'Adv Campaigns',
            df['Campaign Name']
        )

        sales_metric = '14 Day Product Sales'

        # --- Create Main Pivot Table ---
        pivot_table_main = pd.pivot_table(
            df,
            values=sales_metric,
            index=['Advertised ASIN', 'Grouped_Campaign_Name'],
            columns=['Date'],
            aggfunc='sum',
            fill_value=0
        )
        pivot_table_main.columns = pivot_table_main.columns.map(lambda x: x.strftime('%Y-%m-%d'))

        # --- Filter for 'Adv Campaigns' and Create Second Report ---
        pivot_table_adv = None
        if 'Adv Campaigns' in pivot_table_main.index.get_level_values('Grouped_Campaign_Name'):
            pivot_table_adv = pivot_table_main[pivot_table_main.index.get_level_values('Grouped_Campaign_Name') == 'Adv Campaigns']

        return (pivot_table_main, pivot_table_adv), "Attribution Report processed successfully!"

    except Exception as e:
        return None, f"Error processing Attribution Report: {e}"

def process_creator_report_logic(file_path):
    try:
        # Read the file
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
            else:
                return None, f"Error: Required column '{col}' not found in Creator Report."


        # Convert 'Date' column to datetime objects
        df['Date'] = pd.to_datetime(df['Date'], format='%d-%b-%Y')

        # Calculate 'Commission Amount'
        df['Commission Amount'] = df['Sales'] * (df['Commission Rate'] / 100)

        metrics = ['Clicks', 'Orders', 'Sales', 'Spend', 'Commission Amount']
        output_dfs = {}

        for metric in metrics:
            if metric in df.columns:
                grouped_df = df.groupby(['ASIN', 'Date'])[metric].sum().reset_index()
                pivot_df = grouped_df.pivot_table(
                    index='ASIN',
                    columns='Date',
                    values=metric,
                    aggfunc='sum',
                    fill_value=0
                )
                pivot_df.columns = pivot_df.columns.map(lambda x: x.strftime('%Y-%m-%d'))
                output_dfs[metric] = pivot_df
            else:
                messagebox.showwarning("Missing Column", f"Metric '{metric}' not found in Creator Report. Skipping.")

        return output_dfs, "Creator Report processed successfully!"

    except Exception as e:
        return None, f"Error processing Creator Report: {e}"

def combine_sales_reports_logic(attribution_file_path, creator_file_path):
    # --- Process Attribution Report ---
    try:
        df_attr = pd.read_excel(attribution_file_path)
    except Exception as e:
        return None, f"Error reading attribution file: {e}"

    if '14 Day Product Sales' in df_attr.columns:
        df_attr['14 Day Product Sales'] = df_attr['14 Day Product Sales'].astype(str).str.replace('$', '', regex=False).str.replace(',', '', regex=False)
        df_attr['14 Day Product Sales'] = pd.to_numeric(df_attr['14 Day Product Sales'], errors='coerce').fillna(0)
    else:
        return None, f"Error: '14 Day Product Sales' column not found in attribution file."

    df_attr['Date'] = pd.to_datetime(df_attr['Date'])

    if 'Advertiser Country' in df_attr.columns:
        df_attr = df_attr[df_attr['Advertiser Country'] == 'US']

    df_attr_sales = df_attr[['Advertised ASIN', 'Date', '14 Day Product Sales']].copy()
    df_attr_sales.rename(columns={'Advertised ASIN': 'ASIN', '14 Day Product Sales': 'Sales'}, inplace=True)

    # --- Process Creator Report ---
    try:
        try:
            df_creator = pd.read_csv(creator_file_path, encoding='utf-8-sig')
        except UnicodeDecodeError:
            df_creator = pd.read_csv(creator_file_path, encoding='cp1251')
    except Exception as e:
        return None, f"Error reading creator file: {e}"

    if 'Sales' in df_creator.columns:
        df_creator['Sales'] = df_creator['Sales'].astype(str).str.replace('$', '', regex=False).str.replace(',', '', regex=False)
        df_creator['Sales'] = pd.to_numeric(df_creator['Sales'], errors='coerce').fillna(0)
    else:
        return None, f"Error: 'Sales' column not found in creator file."

    df_creator['Date'] = pd.to_datetime(df_creator['Date'], format='%d-%b-%Y')
    df_creator_sales = df_creator[['ASIN', 'Date', 'Sales']].copy()

    # --- Combine DataFrames ---
    combined_sales_df = pd.concat([df_attr_sales, df_creator_sales], ignore_index=True)
    combined_sales_df = combined_sales_df.groupby(['ASIN', 'Date'])['Sales'].sum().reset_index()

    # Create Pivot Table
    pivot_table = combined_sales_df.pivot_table(
        index='ASIN',
        columns='Date',
        values='Sales',
        aggfunc='sum',
        fill_value=0
    )
    pivot_table.columns = pivot_table.columns.map(lambda x: x.strftime('%Y-%m-%d'))

    return pivot_table, "Combined Sales Report processed successfully!"

# --- GUI Application ---

class ReportProcessorApp:
    def __init__(self, master):
        self.master = master
        master.title("Amazon Report Processor")

        self.current_file_path = {} # To store paths for multi-file operations

        # --- Returns Report Section ---
        self.returns_frame = tk.LabelFrame(master, text="Returns Report Processing", padx=10, pady=10)
        self.returns_frame.pack(pady=10, fill="x")

        tk.Label(self.returns_frame, text="Returns CSV File:").grid(row=0, column=0, sticky="w")
        self.returns_file_entry = tk.Entry(self.returns_frame, width=50)
        self.returns_file_entry.grid(row=0, column=1, padx=5, pady=5)
        tk.Button(self.returns_frame, text="Browse", command=self.browse_returns_file).grid(row=0, column=2, padx=5, pady=5)
        tk.Button(self.returns_frame, text="Process Returns", command=self.process_returns).grid(row=1, column=1, pady=5)

        # --- Attribution Report Section ---
        self.attribution_frame = tk.LabelFrame(master, text="Attribution Report Processing", padx=10, pady=10)
        self.attribution_frame.pack(pady=10, fill="x")

        tk.Label(self.attribution_frame, text="Attribution Excel File:").grid(row=0, column=0, sticky="w")
        self.attribution_file_entry = tk.Entry(self.attribution_frame, width=50)
        self.attribution_file_entry.grid(row=0, column=1, padx=5, pady=5)
        tk.Button(self.attribution_frame, text="Browse", command=self.browse_attribution_file).grid(row=0, column=2, padx=5, pady=5)
        tk.Button(self.attribution_frame, text="Process Attribution", command=self.process_attribution).grid(row=1, column=1, pady=5)

        # --- Creator Report Section ---
        self.creator_frame = tk.LabelFrame(master, text="Creator Report Processing", padx=10, pady=10)
        self.creator_frame.pack(pady=10, fill="x")

        tk.Label(self.creator_frame, text="Creator CSV File:").grid(row=0, column=0, sticky="w")
        self.creator_file_entry = tk.Entry(self.creator_frame, width=50)
        self.creator_file_entry.grid(row=0, column=1, padx=5, pady=5)
        tk.Button(self.creator_frame, text="Browse", command=self.browse_creator_file).grid(row=0, column=2, padx=5, pady=5)
        tk.Button(self.creator_frame, text="Process Creator", command=self.process_creator).grid(row=1, column=1, pady=5)

        # --- Combine Sales Reports Section ---
        self.combine_frame = tk.LabelFrame(master, text="Combine Sales Reports", padx=10, pady=10)
        self.combine_frame.pack(pady=10, fill="x")

        tk.Label(self.combine_frame, text="Attribution Excel File:").grid(row=0, column=0, sticky="w")
        self.combine_attr_file_entry = tk.Entry(self.combine_frame, width=50)
        self.combine_attr_file_entry.grid(row=0, column=1, padx=5, pady=5)
        tk.Button(self.combine_frame, text="Browse", command=self.browse_combine_attr_file).grid(row=0, column=2, padx=5, pady=5)

        tk.Label(self.combine_frame, text="Creator CSV File:").grid(row=1, column=0, sticky="w")
        self.combine_creator_file_entry = tk.Entry(self.combine_frame, width=50)
        self.combine_creator_file_entry.grid(row=1, column=1, padx=5, pady=5)
        tk.Button(self.combine_frame, text="Browse", command=self.browse_combine_creator_file).grid(row=1, column=2, padx=5, pady=5)

        tk.Button(self.combine_frame, text="Combine Sales", command=self.combine_sales).grid(row=2, column=1, pady=5)


    def browse_returns_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if file_path:
            self.returns_file_entry.delete(0, tk.END)
            self.returns_file_entry.insert(0, file_path)

    def process_returns(self):
        file_path = self.returns_file_entry.get()
        if not file_path:
            messagebox.showwarning("Input Error", "Please select a Returns CSV file.")
            return

        processed_df, message = process_returns_report_logic(file_path)
        if processed_df is not None:
            messagebox.showinfo("Success", message)
            self.save_dataframe_to_csv(processed_df, "processed_returns_report.csv")
        else:
            messagebox.showerror("Processing Error", message)

    def browse_attribution_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx *.xls")])
        if file_path:
            self.attribution_file_entry.delete(0, tk.END)
            self.attribution_file_entry.insert(0, file_path)

    def process_attribution(self):
        file_path = self.attribution_file_entry.get()
        if not file_path:
            messagebox.showwarning("Input Error", "Please select an Attribution Excel file.")
            return

        (main_df, adv_df), message = process_attribution_report_logic(file_path)
        if main_df is not None:
            messagebox.showinfo("Success", message)
            self.save_dataframe_to_csv(main_df, "attribution_by_asin_and_campaign.csv")
            if adv_df is not None:
                self.save_dataframe_to_csv(adv_df, "attribution_adv_campaigns.csv")
        else:
            messagebox.showerror("Processing Error", message)

    def browse_creator_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if file_path:
            self.creator_file_entry.delete(0, tk.END)
            self.creator_file_entry.insert(0, file_path)

    def process_creator(self):
        file_path = self.creator_file_entry.get()
        if not file_path:
            messagebox.showwarning("Input Error", "Please select a Creator CSV file.")
            return

        processed_dfs, message = process_creator_report_logic(file_path)
        if processed_dfs is not None:
            messagebox.showinfo("Success", message)
            for metric, df in processed_dfs.items():
                self.save_dataframe_to_csv(df, f"creator_{metric.lower().replace(' ', '_')}_report.csv")
        else:
            messagebox.showerror("Processing Error", message)

    def browse_combine_attr_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx *.xls")])
        if file_path:
            self.combine_attr_file_entry.delete(0, tk.END)
            self.combine_attr_file_entry.insert(0, file_path)
            self.current_file_path['combine_attr'] = file_path

    def browse_combine_creator_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if file_path:
            self.combine_creator_file_entry.delete(0, tk.END)
            self.combine_creator_file_entry.insert(0, file_path)
            self.current_file_path['combine_creator'] = file_path

    def combine_sales(self):
        attr_file_path = self.combine_attr_file_entry.get()
        creator_file_path = self.combine_creator_file_entry.get()

        if not attr_file_path or not creator_file_path:
            messagebox.showwarning("Input Error", "Please select both Attribution and Creator files for combining.")
            return

        combined_df, message = combine_sales_reports_logic(attr_file_path, creator_file_path)
        if combined_df is not None:
            messagebox.showinfo("Success", message)
            self.save_dataframe_to_csv(combined_df, "combined_sales_report.csv")
        else:
            messagebox.showerror("Processing Error", message)

    def save_dataframe_to_csv(self, df, default_filename):
        save_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            initialfile=default_filename,
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if save_path:
            df.to_csv(save_path)
            messagebox.showinfo("Save Success", f"Report saved to {save_path}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ReportProcessorApp(root)
    root.mainloop()
