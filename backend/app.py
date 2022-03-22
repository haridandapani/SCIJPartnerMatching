import os
from flask import Flask, request, redirect, flash, url_for, render_template, current_app, send_from_directory, jsonify
from flask_cors import CORS, cross_origin
from werkzeug.utils import secure_filename
import pandas as pd
import json

from file_processing.uploads import is_allowed_file, file_to_dataframe
from file_processing.excel_opener import makePairings

from utils.constants import UPLOAD_FOLDER, MIN_HOURS

app = Flask(__name__, template_folder='templates')
cors = CORS(app)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['TESTING'] = True 
app.config['CORS_HEADERS'] = 'Content-Type'

@app.route('/upload_data', methods=['POST', 'GET'])
@cross_origin()
def upload_data():
    '''
    File upload endpoint. Adapted from https://flask.palletsprojects.com/en/2.0.x/patterns/fileuploads/
    '''
    if request.method == 'GET': 
        return '''
        <!doctype html>
        <title>Upload new File</title>
        <h1>Upload new File</h1>
        <form method=post enctype=multipart/form-data>
        <input type=file name=file>
        <input type=submit value=Upload>
        </form>
        '''
    data_file = request.files['data']
    headers_file = request.files['headers']
    # If the user does not select a file, the browser submits an
    # empty file without a filename.
    """ if data_file.filename == '' or headers_file.filename == '':
        flash('No selected file')
        return redirect(request.url) """
    if not data_file or not is_allowed_file(data_file.filename) or not is_allowed_file(headers_file.filename):
        """ # Prevent filenames that modify important files, e.g .bashrc
        filename = secure_filename(file.filename) 
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename)) 
        return redirect(url_for('download_file', name=filename)) """
        flash('Invalid File')
        flash(data_file)
        flash(headers_file)
        return redirect(request.url)
    data_df = file_to_dataframe(data_file)
    headers_df = file_to_dataframe(headers_file, True)
    if data_df is None or headers_df is None: 
        flash('Error parsing file')
        return redirect(request.url) 

    # headers don't need first row, need for data 

    matrix, legal = makePairings(headers_df, data_df, MIN_HOURS)
    # print(legal)
    # return render_template('simple.html',  tables=[df.to_html(classes='data')], titles=df.columns.values)
    test = {
        "Sabrina Mendez": {
            "Sabrina Mendez": 0, 
            "Madelyn Lu": -1, 
            "Billy-Joe Ramirez": 1
        }, 
        "Madelyn Lu": {
            "Sabrina Mendez": -1, 
            "Madelyn Lu": 0, 
            "Billy-Joe Ramirez": 1
        }, 
        "Billy-Joe Ramirez": {
            "Sabrina Mendez": 1, 
            "Madelyn Lu": 1, 
            "Billy-Joe Ramirez": 0
        }
    }


    return test

@app.route('/match', methods=['GET', 'POST'])
def match(): 
    '''
    Takes user defined criteria and creates top n pairs
    - criteria: [{header, rating}]
    - n: how many possible partners to provide
    '''
    criterion = request.json['criteria']
    n = request.json['top_n']

    pairs = get_top_n_pairs(criterion, n)


    # compareHours lets you get hours of overlap between 2 students. each student also has a school they need to be matched on 
    
    return pairs 

@app.route('/selection', methods=['POST'])
def selection(): 
    '''
    Takes user selections and stores selections
    '''
    # save file or save in gdrive? 
    # redirect to home 
    pass 

@app.route('/uploads/<path:filename>', methods=['GET', 'POST'])
def download(filename): 
    # set this up as a route
    # url_for("download_file", name=name) generates download url
    uploads = os.path.join(app.root_path, app.config['UPLOAD_FOLDER'])
    return send_from_directory(directory=uploads, path=filename)

# Any time in the backend when you need to save a file, save it to the uploads folder

########### HTML STUFF ###########

if __name__ == '__main__': 
    app.secret_key = 'super secret key'
    app.config['SESSION_TYPE'] = 'filesystem'
    app.run(debug=True)