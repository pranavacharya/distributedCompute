from flask import Flask, request
import os, json
import queue
from apscheduler.schedulers.background import BackgroundScheduler
import requests
import threading
from collections import defaultdict
from copy import deepcopy
from file_splitter import file_split
from aggregation import aggregator
from job_assigner import assign_jobs_sequentially

INPUT_FOLDER = './input/'
OUTPUT_FOLDER = './server_op/'
PROGRAM_FILE_NAME = 'job.py'
JOB_FILE_NAME = 'job.txt'

app = Flask(__name__)

clients = ['localhost:8081', 'localhost:8082']

status_dict=dict.fromkeys(clients, 0)
memory_dict=dict.fromkeys(clients, 0)
job_tracker = defaultdict(lambda: [])

app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER
app.config['INPUT_FOLDER'] = INPUT_FOLDER
app.config['PROGRAM_FILE_NAME'] = PROGRAM_FILE_NAME
app.config['JOB_FILE_NAME'] = JOB_FILE_NAME

# program id and job id counter
ID = 0

scheduler_queue = queue.Queue()
distributer_queue = queue.Queue()
asssembler_queue = queue.Queue()
aggregator_queue = queue.Queue()

def pingClients():
    for i in range(0, len(clients)):
        try:
            response = requests.get("http://" + clients[i] + "/heartbeat")
        except:
            status_dict[clients[i]]=0
            memory_dict[clients[i]]=0
            continue
        if response.status_code==200:
            status_dict[clients[i]]=1
            memory_dict[clients[i]]=response.json()['memory']
        else:
            status_dict[clients[i]]=0
            memory_dict[clients[i]]=0

@app.route('/send', methods = ['GET'])
def send_to_all_clients():
    global ID
    chunks = chunk_task(ID, app.config['INPUT_FOLDER'] + app.config['JOB_FILE_NAME'])
    job_tracker[ID] = { "chunks": chunks, "parts": deepcopy(chunks)}
    obj = {
        "file_chunk": chunks,
        "ID": ID
    }
    # add to scheduler queue
    scheduler_queue.put(obj)
    ID += 1
    return "OK"
    
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
            saveFile(output_file, programID + "-" + jobID)
            print("output file recieved form client" + programID + "---" + jobID)
            asssembler_queue.put({
                "pid": programID,
                "job_part": jobID
            })
    return "OK"

# function to schedule job to clients
def job_scheduler():
    while True:
        obj = scheduler_queue.get()
        file_chunk = obj['file_chunk']
        id = obj['ID']

        # assign file_chunks to clients in round robin
        assignments = assign_jobs_sequentially(status_dict, file_chunk)
        for client in assignments:
            file_parts = assignments[client]
            for part in file_parts:
                distributer_queue.put({
                    "client": client,
                    "id": id,
                    "job_part": part
                })
        scheduler_queue.task_done()

# function to distribute jobs to respective clients
def job_distributer():
    while True:
        obj = distributer_queue.get()
        client = obj['client']
        id = obj['id']
        job_part = obj['job_part']
        if send_file(client, id, job_part):
            distributer_queue.task_done()

# function to aggregate jobs recieved
def job_assembler():
    while True:
        obj = asssembler_queue.get()
        id = int(obj['pid'])
        job_part = obj['job_part']
        parts = job_tracker[id]["chunks"]
        parts.remove(job_part)
        if (len(parts) == 0):
            print("task", id, " done....")
            aggregator_queue.put({
                "id": id
            })
        asssembler_queue.task_done()

# function to aggregated completed job
def job_aggregator():
    while True:
        obj = aggregator_queue.get()
        parts = job_tracker[obj["id"]]["parts"]
        print("aggregate results for ", parts)
        final_output = aggregator(obj["id"], parts)
        #save final output
        print(obj["id"], final_output)
        aggregator_queue.task_done()

## util to save file
def saveFile(file, filename):
    file.save(os.path.join(app.config['OUTPUT_FOLDER'], filename))

## util to send program + job file to client
def send_file(client_ip, id, job_id):
    program_file = open(app.config['INPUT_FOLDER'] + app.config['PROGRAM_FILE_NAME'], "rb")
    job_file = open(app.config['INPUT_FOLDER'] + job_id, "rb")
    data = {
        "pid" : str(id),
        "jid" : job_id.split('_')[1]
    }
    test_response = requests.post("http://" + client_ip + "/postTask", files = { "program_file": program_file, "job_file" : job_file, 'json': (None, json.dumps(data), 'application/json')})
    if test_response.status_code == 200:
        return True
    else:
        print("Error in sending file to client")
        return False

## util function to chunk file
def chunk_task(ID, file):
    # change when file is passed
    file_part = file_split(file, ID)
    return file_part

scheduler = BackgroundScheduler()
job = scheduler.add_job(pingClients, 'interval', seconds=5)
scheduler.start()

threading.Thread(target=job_scheduler, daemon=True).start()
threading.Thread(target=job_distributer, daemon=True).start()
threading.Thread(target=job_assembler, daemon=True).start()
threading.Thread(target=job_aggregator, daemon=True).start()

def main():
    app.run(host="0.0.0.0", port=8080)

if __name__ == "__main__":
    main()