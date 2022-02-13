import os
from flask import Flask, request, redirect, flash, url_for
from werkzeug.utils import secure_filename

from utils.constants import UPLOAD_FOLDER
from utils.uploads import allowed_file, preprocess
from utils.match import get_top_n_pairs

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/upload_data', methods=['POST'])
def upload_data():
    '''
    File upload endpoint. Adapted from https://flask.palletsprojects.com/en/2.0.x/patterns/fileuploads/
    '''
    # check if the post request has the file part
    if 'link' in request.form: 
        link = request.form['link']
        # TODO: do something with the sheets link
        print(link)
        data = preprocess(link, is_link=True)
        #return redirect(request.url)

    elif 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['file']
    # If the user does not select a file, the browser submits an
    # empty file without a filename.
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)
    if file and allowed_file(file.filename):
        """ filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return redirect(url_for('download_file', name=filename)) """

        data = preprocess(file)

    return data # frontend takes universal format and asks user for matching criteria

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
    app.run(debug=True)