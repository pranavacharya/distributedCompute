import time, random
from urllib import response
from flask import Flask, jsonify, request
import os, json
from apscheduler.schedulers.background import BackgroundScheduler
import requests

OUTPUT_FOLDER = './server_op/'

app = Flask(__name__)

clients = ['localhost:8081']

app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER

def pingClients():
    for i in range(0, len(clients)):
        response = requests.get("http://" + clients[i] + "/heartbeat")
        print(response)

@app.route('/pingClients', methods = ['GET'])
def get_info_to_display():
    response = {
        "ping": "pong"
    }
    return jsonify(response)

@app.route('/send', methods = ['GET'])
def send_file():
    program_file = open("./input/program1.py", "rb")
    job_file = open("./input/test.txt", "rb")
    data = {
        "pid" : "1",
        "jid" : "1"
    }
    test_response = requests.post("http://localhost:8081/postTask", files = { "program_file": program_file, "job_file" : job_file, 'json': (None, json.dumps(data), 'application/json')})
    if test_response.ok:
        # done
        print("Upload completed successfully!")
        print(test_response.text)
    else:
        # error
        print("Something went wrong!")
    return "done"


@app.route('/recieveOutput', methods = ['POST'])
def upload_file():
    if request.method == 'POST':
        if 'output_file' not in request.files:
            return "404"
        req_object = json.loads(request.form['json'])
        programID = req_object['pid']
        jobID = req_object['jid']
        output_file = request.files['output_file']
        if output_file.filename == '':
            return "invalid file"
        if output_file:
            ##TODO
            saveFile(output_file, 'output.txt')
            print("file recieved")
    return "OK"

## util to save file
def saveFile(file, filename):
    print(filename)
    file.save(os.path.join(app.config['OUTPUT_FOLDER'], filename))

scheduler = BackgroundScheduler()
job = scheduler.add_job(pingClients, 'interval', seconds=5)
scheduler.start()

def main():
    app.run(host="0.0.0.0", port=8080)

if __name__ == "__main__":
    main()