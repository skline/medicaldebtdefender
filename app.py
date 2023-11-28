from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/')
def form():
    return render_template('form.html')

@app.route('/submit', methods=['POST'])
def submit_form():
    # Process your form data here
    # For now, we'll just print it to the console
    print(request.form)
    return "Form Submitted"

if __name__ == '__main__':
    app.run(debug=True)