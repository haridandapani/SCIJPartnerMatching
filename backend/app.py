import os
from flask import Flask, request, redirect, flash, send_from_directory
from flask_cors import CORS, cross_origin

from file_processing.uploads import is_allowed_file, file_to_dataframe
from file_processing.excel_opener import makePairings

from utils.constants import UPLOAD_FOLDER, MIN_HOURS, UPLOAD_FILE

app = Flask(__name__, template_folder='templates')
cors = CORS(app)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['TESTING'] = True 
app.config['CORS_HEADERS'] = 'Content-Type'

'''
Endpoint for displaying legal pairings directly in frontend. 
'''
@app.route('/upload_data', methods=['POST'])
@cross_origin()
def upload_data():
    '''
    File upload endpoint. Adapted from https://flask.palletsprojects.com/en/2.0.x/patterns/fileuploads/
    '''
    data_file = request.files['data']
    headers_file = request.files['headers']

    # If the user does not select a file, the browser submits an
    # empty file without a filename.
    if not data_file or not is_allowed_file(data_file.filename) or not is_allowed_file(headers_file.filename):
        flash('Invalid File')
        flash(data_file)
        flash(headers_file)
        return redirect(request.url)

    data_df = file_to_dataframe(data_file)
    headers_df = file_to_dataframe(headers_file, True)

    if data_df is None or headers_df is None: 
        flash('Error parsing file')
        return redirect(request.url) 

    final_dict = makePairings(headers_df, data_df, MIN_HOURS)
    test = final_dict['matrix'] # also has 'unpaired' and 'optimal': [{'person1': steven, 'person2': hari}, ...]

    return test

''' 
Endpoint for excel format download. Assumes legal pairings are saved at 
UPLOAD_FOLDER/UPLOAD_FILE (currently data/xlsx_example.xlsx). 
'''
@app.route('/download', methods=['POST'])
@cross_origin()
def download(): 
    data_file = request.files['data']
    headers_file = request.files['headers']

    # If the user does not select a file, the browser submits an
    # empty file without a filename.
    if not data_file or not is_allowed_file(data_file.filename) or not is_allowed_file(headers_file.filename):
        flash('Invalid File')
        flash(data_file)
        flash(headers_file)
        return redirect(request.url)

    data_df = file_to_dataframe(data_file)
    headers_df = file_to_dataframe(headers_file, True)

    if data_df is None or headers_df is None: 
        flash('Error parsing file')
        return redirect(request.url) 

    final_dict = makePairings(headers_df, data_df, MIN_HOURS)
    test = final_dict['matrix'] # also has 'unpaired' and 'optimal': [{'person1': steven, 'person2': hari}, ...]

    # TODO: code to write test into excel 

    # set this up as a route
    # url_for("download_file", name=name) generates download url
    uploads = os.path.join(app.root_path, app.config['UPLOAD_FOLDER'])
    return send_from_directory(directory=uploads, filename=UPLOAD_FILE, as_attachment=True)

'''
Unused endpoint for excel download. Use if we want frontend to specify file loc
'''
@app.route('/uploads/<path:filename>', methods=['GET', 'POST'])
@cross_origin()
def download_specific_file_path(filename): 
    # set this up as a route
    # url_for("download_file", name=name) generates download url
    uploads = os.path.join(app.root_path, app.config['UPLOAD_FOLDER'])
    return send_from_directory(directory=uploads, path=filename)

if __name__ == '__main__': 
    app.secret_key = 'super secret key'
    app.config['SESSION_TYPE'] = 'filesystem'
    app.run(debug=True)