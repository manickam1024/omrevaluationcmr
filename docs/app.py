from flask import Flask, render_template, request, redirect, url_for
import os
import subprocess

UPLOAD_FOLDER = 'samples/inputs'
OUTPUT_FOLDER = 'outputs'

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'No file part'
    
    file = request.files['file']
    if file.filename == '':
        return 'No selected file'
    
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(file_path)

    # Run your evaluation command
    result = subprocess.run(['python', 'main.py', '--outputDir', OUTPUT_FOLDER], capture_output=True, text=True)
    
    return f"File uploaded and processed.<br><pre>{result.stdout}</pre>"

if __name__ == '__main__':
    app.run(debug=True)
