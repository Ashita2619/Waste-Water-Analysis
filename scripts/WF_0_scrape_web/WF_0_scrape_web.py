from WF_0_scrape_web.WF_0_helpers import WF_0_ClearLabs
import json
import os



def run_script_0(run_ids,res_path,download_p,cl_url,cl_username,cl_password):
    print("\n================================\nScrape Web Script\n================================\n\n")
    
    #creating WorkflowObj
    data_obj = WF_0_ClearLabs(cl_url,cl_username,cl_password)

    #save run info into var, while downloading fasta files for each run id supplied
    run_info=data_obj.scrape(run_ids,res_path,download_p)
    
    #save run info from var into json file, with name Runid_RunID.json
    abs_path = res_path + "/data/run_data.json"

    with open (abs_path,"w") as j_dump:
        run_info = json.dumps(run_info)
        j_dump.write(run_info)
    
    data_obj.close_conns()

    print("\n================================\nSUCCESS - END OF SCRIPT\n================================\n\n")


 

 