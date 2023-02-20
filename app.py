from flask import Flask, render_template, request, session, send_file
from flask_cors import CORS
import json
import os
import pandas as pd
from pprint import pprint
import io
from transformers import pipeline
from snorkel.labeling.model.label_model import LabelModel

app = Flask(__name__)
CORS(app)

# Set the upload folder and allowed file types
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'csv'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = 'some_secret'

# Check if a filename has an allowed file extension
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

"""### Routes"""

@app.route('/')
def index():
    return render_template('index.html')

# Handle file uploads
@app.route('/upload', methods=['POST'])
def upload_file():
   if request.method == 'POST':
       f = request.files['file']
       f.save(f.filename)
       session['filename'] = f.filename
       return render_template('index.html',msg="Success")

# Handle file downloads
@app.route('/download')
def download_file():
    filename = request.args.get('filename')
    try:
        return send_file(filename, as_attachment=True)
    except Exception as e:
        return str(e)

# Generate Labels
@app.route('/label')
def generate_label():
    run_labeling()
    return render_template('index.html',labeling_msg="Labeling.")

"""### Labeling Functions"""

def get_category(text):
  return str(text) == 'Technical'

def get_rating(text):
  try:
      return int(text) < 4
  except ValueError:
      return False

def get_subscription_type(text):
  return str(text) == 'Premium'

def get_sentiment(text):
    result = sentiment_model(str(text))[0]
    label = result['label']
    score = result['score']
    if (label == 'POSITIVE'): 
      return True 
    return False

def convert_value(x):
    return 'Acceptable' if x == 0 else 'Not Acceptable'

def run_labeling():
    filename = session.get('filename')
    df = pd.read_csv(filename)
    category_labels = [get_category(text) for text in df['Category']]
    sentiment_labels = [get_sentiment(text) for text in df['Comments']]
    rating_labels = [get_rating(text) for text in df['Rating']]
    type_labels = [get_subscription_type(text) for text in df['SubscriptionType']]
    df_lf = pd.DataFrame(
        {
            'Category': category_labels, 
            'Sentiment': sentiment_labels, 
            'Rating': rating_labels, 
            'Subscription': type_labels
        }
    )
    labeling_functions = [get_category, get_sentiment, get_rating, get_subscription_type]
    label_model = LabelModel(cardinality=2, verbose=True)
    label_matrix = df_lf.to_numpy()
    label_model.fit(label_matrix)
    df_final = df.copy()
    df_final['Prediction'] = label_model.predict(label_matrix) == 0
    base_name, extension = os.path.splitext(filename)
    df_final.to_csv(base_name+'_final.csv', index=False)

if __name__ == '__main__':
    sentiment_model = pipeline('sentiment-analysis') # Sentiment Analysis
    app.run(debug=True)





