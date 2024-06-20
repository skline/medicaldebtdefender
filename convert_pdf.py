from tabula import read_pdf
import pandas as pd

def convert_pdf_to_csv(pdf_path, csv_path):
    # Read tables from PDF
    tables = read_pdf(pdf_path, pages='all', multiple_tables=True)

    # Combine all tables into one DataFrame
    combined_table = pd.concat(tables, ignore_index=True)

    # Save the DataFrame to a CSV file
    combined_table.to_csv(csv_path, index=False)

    print("CSV file has been created successfully.")

# Path to your PDF file
pdf_path = '/Users/spencerkline/Downloads/EffectiveJune302021-CPT_HCPCS_ADAandOWCPCodeswithRVUandConversionFactors.pdf'

# Path to save the CSV file
csv_path = '/Users/spencerkline/Downloads/converted_data.csv'

# Convert PDF to CSV
convert_pdf_to_csv(pdf_path, csv_path)
