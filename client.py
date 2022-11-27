import time, random
from urllib import response
from flask import Flask, jsonify, request
import os, json

UPLOAD_FOLDER = './output/'

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/heartbeat', methods = ['GET'])
def heartbeat():
    response = {
        "ping": "pong"
    }
    return jsonify(response)

@app.route('/acceptTask', methods=['POST'])
def upload_file():
    if request.method == 'POST':
        if 'file_upload' not in request.files:
            return "404 lol"
        file = request.files['file_upload']
        if file.filename == '':
            return "file name daal"
        if file:
            filename = file.filename
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return "saved"
    return "done"

def main():
    app.run(host="0.0.0.0", port=8081)

if __name__ == "__main__":
    main()