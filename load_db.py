import re
import psycopg2
import os
import io

file_path = '/Users/spencerkline/Downloads/EffectiveJune302021-CPT_HCPCS_ADAandOWCPCodeswithRVUandConversionFactors.txt'

i =0
j=0
k=0
m=0
cpt_pattern = re.compile(r'\b([A-Za-z]\d{4}|\d{5})\b')
data_to_insert = []

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

# Open the file and iterate through each line
prior_row=['none', 'none']
with open(file_path, 'r') as file:
    for line in file:
        i+=1
        print(i)
        # Process each line
# Re-define the regular expression split to account for the blank item
        split_items = re.split(r'\s{2,}', line.strip())

        # Insert an empty string to represent the blank item between '0001A' and 'C'
        if len(split_items) <9:
            if cpt_pattern.search(split_items[0]):
                first = split_items
                second = prior_row
            elif cpt_pattern.search(prior_row[0]):
                second = split_items
                first = prior_row
            elif 'Energy' in split_items[0] or 'FECA' in split_items[0]:
                second = split_items
                first = prior_row
            elif 'Energy' in prior_row[0] or 'FECA' in prior_row[0]:
                first =  prior_row
                second = split_items 
            elif len(split_items) >= 5:
                first = split_items
                second = prior_row
            else:
                first =  prior_row
                second = split_items 
            m+=1
            merged = first+second
            if len(merged) == 9 or len(merged) == 10:
                print(split_items)
                print(prior_row)
                split_items = merged
                k+=1
                print(merged)
                print(first, second)
                print()
        if len(split_items)  == 9:
            split_items.insert(1, '')
        if len(split_items) !=10 and 'Table' not in line and 'NON-FACILITY' not in line and 'CONVERSION' and 'FECA' not in line:
            j+=1
            #print(len(split_items))
            #print(line)
        if len(split_items) == 10 and split_items[0] !='HCPCS' and split_items[0] !='ADA':
            data_to_insert.append(split_items)


        prior_row = split_items

data = '\n'.join('\t'.join(map(str, item)) for item in data_to_insert)

data_io = io.StringIO(data)


cursor.execute('select * from public.all_cpt_codes')
sql_command = """
    COPY public.all_cpt_codes (
        cpt_code, modifier, pay_status, work_rvu, non_facility_pe_rvu, 
        facility_pe_rvu, mpe_rvu, global_rvu, conversion_factor, short_description
    ) 
    FROM STDIN WITH (FORMAT csv, DELIMITER E'\t')
"""
cursor.copy_expert(sql_command, data_io)



conn.commit()