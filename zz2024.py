import re
import psycopg2
import os
import io
import pandas as pd
import numpy as np


def create_db_connection_and_cursor():
    # Database connection parameters
    DB_HOST = 'dbmdd.postgres.database.azure.com'
    DB_NAME = 'postgres'
    DB_USER = 'skline'
    DB_PASS = os.getenv('DB_PASS')

    try:
        # Connect to the database
        conn = psycopg2.connect(
            dbname=DB_NAME, 
            user=DB_USER, 
            password=DB_PASS, 
            host=DB_HOST
        )
        # Create a cursor
        cursor = conn.cursor()
        print("Database connection and cursor established")
        return conn, cursor
    except Exception as e:
        print(f"An error occurred: {e}")
        return None, None
conn, cursor = create_db_connection_and_cursor()
df = pd.read_excel('updated_data.xlsx')
for col in df.columns:
    if col != 'modifier':
        df[col].replace('nan', np.nan, inplace=True)
df['modifier'] = df['modifier'].where(pd.notnull(df['modifier']), 'None')


data = '\n'.join('\t'.join('' if pd.isnull(val) else str(val) for val in item) for item in df.values)
# Create a file-like object
data_io = io.StringIO(data)
# Use copy_expert to execute the COPY command
sql_command = """
    COPY cpt_code_to_rvus (
        cpt_code, modifier, description, status_code, not_used_for_medicare_payment, 
        work_rvu, non_fac_pe_rvu, non_fac_na_indicator, facility_pe_rvu, facility_na_indicator, 
        mp_rvu, non_facility_total, facility_total, pctc_ind, glob_days, pre_op, 
        intra_op, post_op, mult_proc, bilat_surg, asst_surg, co_surg, team_surg, 
        endo_base, conv_factor, physician_supervision_of_diagnostic_procedures, 
        calculation_flag, diagnostic_imaging_family_indicator, non_facility_pe_used_for_opps_payment_amount, 
        facility_pe_used_for_opps_payment_amount, mp_used_for_opps_payment_amount
    ) 
    FROM STDIN WITH (FORMAT csv, DELIMITER E'\t')
"""
cursor.copy_expert(sql_command, data_io)


# Commit the changes
conn.commit()
