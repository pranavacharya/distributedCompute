import time, random
from urllib import response
from flask import Flask, jsonify, request
import os, json
from apscheduler.schedulers.background import BackgroundScheduler
import requests
# from io import StringIO
# from Assign_jobs_sequentially import assign_jobs_sequentially
from file_splitter import file_split
OUTPUT_FOLDER = './server_op/'

app = Flask(__name__)

clients = ['localhost:8081']
statusDict=dict.fromkeys(clients,0)
memoryDict=dict.fromkeys(clients,0)
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER

def pingClients():
    for i in range(0, len(clients)):
        try:
            response = requests.get("http://" + clients[i] + "/heartbeat")
        except:
            statusDict[clients[i]]=0
            memoryDict[clients[i]]=0
            print(statusDict)
            print(memoryDict)
            continue
        if response.status_code==200:
            statusDict[clients[i]]=1
            memoryDict[clients[i]]=response.json()['memory']
        else:
            statusDict[clients[i]]=0
            memoryDict[clients[i]]=0
        print(statusDict)
        print(memoryDict)

@app.route('/pingClients', methods = ['GET'])
def get_info_to_display():
    response = {
        "ping": "pong"
    }
    return jsonify(response)

def send_file(client_ip,job_id,program_id):
    program_file = open("./input/"+program_id, "rb")
    job_file = open("./input/"+job_id, "rb")
    job_file = open(job_id, "rb")
    print(job_file)
    data = {
        "pid" : program_id.split('.')[0],
        "jid" : job_id.split('.')[0]
    }
    test_response = requests.post("http://" + client_ip+"/postTask", files = { "program_file": program_file, "job_file" : job_file, 'json': (None, json.dumps(data), 'application/json')})
    if test_response.ok:
        # done
        print("Upload completed successfully!")
        print(test_response.text)
    else:
        # error
        print("Something went wrong!")
    return "done"

 
def assign_jobs_sequentially(client_status, job_parts):
    list_of_clients=[k for k,v in client_status.items() if v ==1]
    len_client=len(list_of_clients)
    len_job=len(job_parts)
    max_len=max(len_client,len_job)
    assign_list = [[] for x in range(len_client)]    
    n_j=0
    for i in range(max_len):
        for j in range(len_client):
            if n_j==len_job:
                break
            assign_list[j].append(job_parts[n_j])
            n_j=n_j+1
        if n_j==len_job:
            break
    assign_jobs={}
    for i in range(len(list_of_clients)):    
        assign_jobs[list_of_clients[i]]=assign_list[i]
    return assign_jobs

@app.route('/send', methods = ['GET'])
def send_to_all_clients():
    split_file_op=file_split("./input/job.txt")
    print(split_file_op)
    assign_job=assign_jobs_sequentially(statusDict,split_file_op )
    active_clients=list(assign_job.keys())
    #active_clients=[k for k,v in client_status.items() if v ==1]
    ctr=0
    for each_client in active_clients:
        for job in assign_job[each_client]:
            # try:
            print(each_client)
            print(job)
            send_file(each_client,job,"program1.py")
            ctr=ctr+1
            # except:
            #     print("send_file failed")
    return {"status":"done","ctr":ctr}

# def send_file():
#     program_file = open("./input/program1.py", "rb")
#     job_file = open("./input/test.txt", "rb")
#     split_job_files=file_split("./input/job.txt")
#     assign_jobs_sequentially(statusDict, split_job_files)
#     data = {
#         "pid" : "1",
#         "jid" : "1"
#     }
#     test_response = requests.post("http://localhost:8081/postTask", files = { "program_file": program_file, "job_file" : job_file, 'json': (None, json.dumps(data), 'application/json')})
#     if test_response.ok:
#         # done
#         print("Upload completed successfully!")
#         print(test_response.text)
#     else:
#         # error
#         print("Something went wrong!")
#     return "done"


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