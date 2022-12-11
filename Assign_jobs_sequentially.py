
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
        
client_status={'C1':1,
               'C2':1,
               'C3':1,
               'C4':1,
               'C5':1,
               'C6':0,
               'C7':0}
#list_of_clients=['C1','C2','C3','C4','C5']
job_parts=['J1','J2','J3','J4','J5','J6','J7','J8','J9','J10']
job_parts=['test1.txt','test2.txt','test3.txt','test4.txt','test5.txt','test6.txt','test7.txt','test8.txt','test9.txt','test10.txt']

assign_job=assign_jobs_sequentially(client_status, job_parts)
# 

def send_file(client_ip,job_id,program_id):
    program_file = open("./input/"+program_id, "rb")
    job_file = open("./input/"+job_id, "rb")
    data = {
        "pid" : program_id.split('.')[0],
        "jid" : job_id.split('.')[0]
    }
    test_response = requests.post(client_ip+"/postTask", files = { "program_file": program_file, "job_file" : job_file, 'json': (None, json.dumps(data), 'application/json')})
    if test_response.ok:
        # done
        print("Upload completed successfully!")
        print(test_response.text)
    else:
        # error
        print("Something went wrong!")
    return "done"

def send_to_all_clients(assign_job):
    active_clients=list(assign_job.keys())
    #active_clients=[k for k,v in client_status.items() if v ==1]
    for each_client in active_clients:
        for job in assign_job[each_client]:
            send_file(each_client,job,"program1.py")
        
    
C1="http://localhost:8081"

C1+"/postTask"

job_id="1.txt"
job_id.split('.')[0]

program_id="program1.py"
program_id.split('.')[0]




