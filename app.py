from flask import Flask, render_template, request
import yaml
from openai import OpenAI
from markupsafe import Markup
client = OpenAI()



app = Flask(__name__)

@app.route('/')
def form():
    return render_template('form.html')

@app.route('/submit', methods=['POST'])
def submit_form():
    # Convert form data to dictionary and save to YAML
    # ... Your existing code to generate YAML ...

    form_data = request.form.to_dict()
    # Convert dictionary to YAML format
    yaml_data = yaml.dump(form_data, default_flow_style=False)


    completion = client.chat.completions.create(
    model="gpt-4-1106-preview",
    messages=[
        {"role": "system", "content": "You are a medical debt advocate who is helping a patient create a letter to their medical provider. The letter should primarily consist of specific and polite questions seeking clarification and assistance regarding their medical debt. Ensure the letter is respectful and professional."},
        {"role": "user", "content": 'Compose the letter using this patient’s data in YAML format. The letter should ask the provider questions about the debt, the billing process, and any possible debt relief options.  Do not include the YAML in the output. Use pargraphs, do not make each new sentence a newline. Data:\n' + yaml_data}
    ]
    )

    # Print the response
    response = completion.choices[0].message.content
    print(response)

    response = response.replace('\n', '<br>')
    formatted_response = Markup(f"<div><p>{response}</p></div>")

    return formatted_response  # Or handle the response as needed


if __name__ == '__main__':
    app.run(debug=True)