from flask import Flask, render_template, request, Response, jsonify
import yaml
from openai import OpenAI
from markupsafe import Markup
client = OpenAI()
from markupsafe import Markup
app = Flask(__name__)
import psycopg2
import os
import urllib.parse


# Database connection parameters
DB_HOST = 'dbmdd.postgres.database.azure.com'
DB_NAME = 'postgres'
DB_USER = 'skline'
DB_PASS = os.getenv('DB_PASS')

@app.route('/get_avg_fee', methods=['GET'])
def get_avg_fee():
    # Get the 'cpt_code' from the query parameters
    cpt_code = request.args.get('cpt_code')
    billable_units = request.args.get('billable_units', default=1, type=float)
    if not billable_units:
        billable_units = 1


    # Connect to the database
    conn = psycopg2.connect(
        dbname=DB_NAME, 
        user=DB_USER, 
        password=DB_PASS, 
        host=DB_HOST
    )

    # Create a cursor object
    cur = conn.cursor()

    # Query the database for the average fee information
    query = """
SELECT
    cec.cpt_code,
    cec.description,
    cec.expected_cost * %s AS adjusted_expected_cost
FROM
    cpt_code_expected_costs cec
WHERE
    cec.cpt_code = %s;

    """
    cur.execute(query, (billable_units,cpt_code,))

    # Fetch the result
    result = cur.fetchone()

    # Close the cursor and the connection
    cur.close()
    conn.close()

    # If no result is found, return an error
    if result is None:
        response = jsonify({'error': 'CPT code not found'}), 404
    else:
        # If a result is found, return the average fee information
        response_data = {
            'cpt_code': result[0],
            'description': result[1],
            'avg_fee': result[2]
        }
        response = jsonify(response_data), 200

    return response


@app.route('/add_lead', methods=['POST'])
def add_lead():
    # Parse data from request
    data = request.json
    email = data.get('email')
    name = data.get('name')

    # Validate data
    if not name or not email:
        return jsonify({'error': 'Missing name or email'}), 400

    # Connect to the database
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME, 
            user=DB_USER, 
            password=DB_PASS, 
            host=DB_HOST
        )
        cur = conn.cursor()

        # Insert data into the database
        cur.execute(''' 
    INSERT INTO public.leads (email, name) 
    VALUES (%s, %s) 
    ON CONFLICT (email) DO UPDATE 
    SET name = EXCLUDED.name
    ''', (email, name))
        conn.commit()

        # Close the connection
        cur.close()
        conn.close()

        return jsonify({'success': 'Client added successfully'}), 201

    except Exception as e:
        # Handle database connection errors
        return jsonify({'error': str(e)}), 500

@app.route('/get_real_name', methods=['GET'])
def get_real_name():
    # Get the 'name' from the query parameters
    name = request.args.get('name')
    name = (name).lower()
    # Connect to the database
    conn = psycopg2.connect(
        dbname=DB_NAME, 
        user=DB_USER, 
        password=DB_PASS, 
        host=DB_HOST
    )

    # Create a cursor object
    cur = conn.cursor()

    # Query the database for the real name
    cur.execute('SELECT real_name FROM client_names WHERE lower(name) = lower(%s)', (name,))
    result = cur.fetchone()

    # Close the cursor and the connection
    cur.close()
    conn.close()

    # If no result is found, return an error
    if result is None:
        response = jsonify({'error': 'Name not found'}), 404
    else:
        # If a result is found, return the real name
        real_name = result[0]
        response = jsonify({'real_name': real_name}), 200

    return response

@app.route('/')
def form():
    clear_text = 'clear' in request.args

    return render_template('form.html', clear_text=clear_text)

@app.route('/submit', methods=['POST'])
def submit_form():
    # Convert form data to dictionary and save to YAML
    form_data = request.form.to_dict()
    # Convert dictionary to YAML format
    yaml_data = yaml.dump(form_data, default_flow_style=False)


    completion = client.chat.completions.create(
    model="gpt-4-1106-preview",
    messages=[
        {"role": "system", "content": "You are a medical debt advocate who is helping a patient create a letter to their medical provider. The letter should primarily consist of specific and polite questions seeking clarification and assistance regarding their medical debt. Ensure the letter is respectful and professional."},
        {"role": "user", "content": 'Compose the letter using this patient’s data in YAML format. The letter should ask the provider questions about the debt, the billing process, and any possible debt relief options.  Do not include the YAML in the output. Use pargraphs, do not make each new sentence a newline. You have the patient\'s name in the yaml. Do not use placeholders, only use text in the yaml file Data:\n' + yaml_data}
    ]
    )

    print(completion.choices[0].message)
    response = completion.choices[0].message.content
    response = response.replace('\n', '<br>')
    formatted_response = Markup(f"<div><p>{response}</p></div>")
    return Response(formatted_response, mimetype='text/html')

@app.route('/create_letter', methods=['POST'])
def create_letter():
    # Convert form data to dictionary and save to YAML
    form_data = request.get_json()
    # Convert dictionary to YAML format
    yaml_data = yaml.dump(form_data, default_flow_style=False)

    completion = client.chat.completions.create(
    model="gpt-4-1106-preview",
    messages=[
        {"role": "system", "content": "You are a medical debt advocate who is helping a patient create a letter to their medical provider. The letter should primarily consist of specific and polite questions seeking clarification and assistance regarding their medical debt. Ensure the letter is respectful and professional."},
        {"role": "user", "content": 'Compose the letter using this patient’s data in YAML format. The letter should ask the provider questions about the debt, the billing process, and any possible debt relief options.  Do not include the YAML in the output. Use pargraphs, do not make each new sentence a newline. You have the patient\'s name in the yaml. Do not use placeholders, only use text in the yaml file Data:\n' + yaml_data}
    ]
    )

    print(completion.choices[0].message)
    response = completion.choices[0].message.content
    response = jsonify({'response': response}), 200
    return response





if __name__ == '__main__':
    app.run(debug=True)