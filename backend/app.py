import os
from flask import Flask, request, redirect, flash, url_for, render_template
from werkzeug.utils import secure_filename
import pandas as pd

from utils.constants import UPLOAD_FOLDER
from utils.uploads import is_allowed_file, file_to_dataframe, preprocess
from utils.match import get_top_n_pairs

app = Flask(__name__, template_folder='templates')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route('/upload_data', methods=['POST', 'GET'])
def upload_data():
    '''
    File upload endpoint. Adapted from https://flask.palletsprojects.com/en/2.0.x/patterns/fileuploads/
    '''
    """ # check if the post request has the file part
    if 'link' in request.form: 
        link = request.form['link']
        # TODO: do something with the sheets link
        print(link)
        data = preprocess(link, is_link=True)
        #return redirect(request.url)

    elif 'file' not in request.files:
        flash('No file part')
        return redirect(request.url) """

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

    file = request.files['file']
    # If the user does not select a file, the browser submits an
    # empty file without a filename.
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)
    if not file or not is_allowed_file(file.filename):
        """ # Prevent filenames that modify important files, e.g .bashrc
        filename = secure_filename(file.filename) 
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename)) 
        return redirect(url_for('download_file', name=filename)) """
        flash('Invalid File')
        flash(file)
        flash(is_allowed_file(file.filename))
        return redirect(request.url)
    df = file_to_dataframe(file)
    if df is None: 
        flash('Error parsing file')
        return redirect(request.url) 
    print(df)
    #data = preprocess(file)
    # return data # frontend takes universal format and asks user for matching criteria
    return render_template('simple.html',  tables=[df.to_html(classes='data')], titles=df.columns.values)
    
@app.route('/match', methods=['POST'])
def match(): 
    '''
    Takes user defined criteria and creates top n pairs
    - criteria: [{header, rating}]
    - n: how many possible partners to provide
    '''
    criterion = request.json['criteria']
    n = request.json['top_n']

    pairs = get_top_n_pairs(criterion, n)
    return pairs 

@app.route('/selection', methods=['POST'])
def selection(): 
    '''
    Takes user selections and stores selections
    '''
    # save file or save in gdrive? 
    # redirect to home 
    pass 


if __name__ == '__main__': 
    app.secret_key = 'super secret key'
    app.config['SESSION_TYPE'] = 'filesystem'
    app.run(debug=True)