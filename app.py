from flask import Flask, render_template, request, send_file
from flask_cors import CORS
import json
import os

app = Flask(__name__)
CORS(app)

# Set the upload folder and allowed file types
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'csv'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Check if a filename has an allowed file extension
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

# Handle file uploads
@app.route('/upload', methods=['POST'])
def upload_file():
   if request.method == 'POST':
       f = request.files['file']
       f.save(f.filename)
       return 'file uploaded successfully'

# Handle file downloads
@app.route('/download')
def download_file():
    filename = request.args.get('filename')
    try:
        return send_file(filename, as_attachment=True)
    except Exception as e:
        return str(e)

if __name__ == '__main__':
    app.run(debug=True)





