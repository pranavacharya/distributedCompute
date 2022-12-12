from flask import Flask, jsonify, request
import os
import queue
import threading
import json
import requests
import psutil

UPLOAD_FOLDER = './uploads/'
OUTPUT_FOLDER = './outputs/'
HOSTIP_PORT = 'localhost:8080'

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER
app.config['HOST'] = HOSTIP_PORT

task_queue = queue.Queue()
output_queue = queue.Queue()

@app.route('/heartbeat', methods = ['GET'])
def heartbeat():
    status = getSystemStatus();
    response = {
        "ping": "pong",
        "memory": status
    }
    return jsonify(response)

@app.route('/postTask', methods=['POST'])
def upload_file():
    if request.method == 'POST':
        if 'program_file' not in request.files and 'job_file' not in request.files:
            return "404"
        program = request.files['program_file']
        req_object = json.loads(request.form['json'])
        programID = req_object['pid']
        program_name = programID + ".py"
        job = request.files['job_file']
        jobID = programID + ":" + req_object['jid']
        if program.filename == '' or job.filename == '':
            return "invalid file"
        if program and job:
            saveFile(program, program_name)
            saveFile(job, jobID)
            task = {
                "pid": programID,
                "jid": jobID
            }
            task_queue.put(task)
            print("task posted")
    return "OK"

## worker function to execute tasks
def taskRunner():
    while True:
        print("running task runner")
        item = task_queue.get()
        
        pid = item['pid']
        jid = item['jid']
        ## running task
        p_path = os.path.join(app.config['UPLOAD_FOLDER'], pid + ".py")
        j_path = os.path.join(app.config['UPLOAD_FOLDER'], jid)
        op_path = os.path.join(app.config['OUTPUT_FOLDER'], pid + ":" + jid + ".out")
        os.system("python3 "  + p_path + " " + j_path + " > " + op_path)
        
        ## insert into op queue
        op_obj = {
            "pid": pid,
            "jid": jid,
            "op_path": op_path
        }
        output_queue.put(op_obj)

        ##
        task_queue.task_done()

## worker function to post task output back to server
def outputPublisher():
    while True:
        item = output_queue.get()
        pid = item['pid']
        jid = item['jid']
        op_path = item['op_path']
        if sendFile(op_path, pid, jid):
            output_queue.task_done()

## util to save file
def saveFile(file, filename):
    print(filename)
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

## util to send file to host
def sendFile(file_path, pid, jid):
    output_file = open(file_path, "rb")
    data = {
        "pid" : pid,
        "jid" : jid
    }
    test_response = requests.post("http://" + app.config['HOST'] + "/recieveOutput", files = { "output_file": output_file, 'json': (None, json.dumps(data), 'application/json')})
    if test_response.ok:
        return True
    else:
        return False

## method to get system status
def getSystemStatus():
    mem = psutil.virtual_memory()
    available = mem[0] - mem[2]
    return available

threading.Thread(target=taskRunner, daemon=True).start()
threading.Thread(target=outputPublisher, daemon=True).start()

def main():
    app.run(host="0.0.0.0", port=8081)

if __name__ == "__main__":
    main()


# TODO: replace file before saving 
# https://stackoverflow.com/questions/65992804/flask-python-modify-uploaded-file-data-before-saving