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
