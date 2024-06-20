import json
import os
import requests
from openai import OpenAI
from prompts import assistant_instructions
import urllib.parse
import requests
import psycopg2

OPENAI_API_KEY = os.environ['OPENAI_API_KEY']
# Database connection parameters
DB_HOST = 'dbmdd.postgres.database.azure.com'
DB_NAME = 'postgres'
DB_USER = 'skline'
DB_PASS = os.getenv('DB_PASS')

# Create or load assistant
def create_assistant(client):
  assistant_file_path = 'assistant.json'

  # If there is an assistant.json file already, then load that assistant
  if os.path.exists(assistant_file_path):
    with open(assistant_file_path, 'r') as file:
      assistant_data = json.load(file)
      assistant_id = assistant_data['assistant_id']
      print("Loaded existing assistant ID.")
  else:
    # If no assistant.json is present, create a new assistant using the below specifications

    # To change the knowledge document, modifiy the file name below to match your document
    # If you want to add multiple files, paste this function into ChatGPT and ask for it to add support for multiple files
    file = client.files.create(file=open("knowledge.txt", "rb"),
                               purpose='assistants')
    assistant = client.beta.assistants.create(
        # Getting assistant prompt from "prompts.py" file, edit on left panel if you want to change the prompt
        instructions=assistant_instructions,
        model="gpt-4-1106-preview",
        tools=[
            {
                "type": "retrieval"  # This adds the knowledge base as a tool
            },
            {
                "type": "function",  # This adds the lead capture as a tool
                "function": {
                    "name": "create_lead_local",
                    "description":
                    "Capture lead details and save to Airtable.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "email": {
                                "type": "string",
                                "description": "Email of Lead"
                            },
                            "name": {
                                "type": "string",
                                "description": "Name of Lead"
                            },
                        },
                        "required": ["email", "name"]
                    }
                }
            }
        ],
        file_ids=[file.id])

    # Create a new assistant.json file to load on future runs
    with open(assistant_file_path, 'w') as file:
      json.dump({'assistant_id': assistant.id}, file)
      print("Created a new assistant and saved the ID.")

    assistant_id = assistant.id

  return assistant_id

def create_lead_local(email, name):
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

def create_lead(email, name):
  url = "https://medicaldebtdefender.com/add_lead"
  headers = {"Content-Type": "application/json"}
  data = {"email": email, "name": name}
  response = requests.post(url, headers=headers, json=data)

  if response.status_code == 201:
    print("Client added successfully.")
    return response.json()
  else:
    print(f"Failed to add client: {response.status_code} - {response.text}")


def get_avg_fee(cpt_code, billable_units=1):
  base_url = "https://medicaldebtdefender.com/get_avg_fee"
  # URL encode the cpt_code to ensure it's correctly formatted for a query parameter
  encoded_cpt_code = urllib.parse.quote(cpt_code)
  # Construct the full URL with query parameters
  url = f"{base_url}?cpt_code={encoded_cpt_code}&billable_units={billable_units}"

  try:
    response = requests.get(url)

    if response.status_code == 200:
      data = response.json()
      return data
    else:
      return f"Failed to get average fee: {response.status_code} - {response.text}"
  except Exception as e:
    return f"An error occurred: {e}"
