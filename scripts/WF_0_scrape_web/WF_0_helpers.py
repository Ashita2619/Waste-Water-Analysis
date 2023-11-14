from WF_0_scrape_web.ClearLabsScrapper import ClearLabsApi
#from scripts.WF_0_scrape_web.ClearLabsScrapper import ClearLabsApi
import datetime
import os
import time
import zipfile



class WF_0_ClearLabs():

    def __init__(self,clearlabs_url,cl_user,cl_pwd):
        self.clearlabs_url = clearlabs_url
        self.cl_user = cl_user
        self.cl_pwd = cl_pwd
        

    def scrape(self, runId,resource_path,download_path):
        #create folder for fasta files
        machine_num = runId[4:6]
        run_date = datetime.datetime.strptime(runId[7:17], '%Y-%m-%d').strftime("%m%d%y")
        day_run_num = str(int(runId[-2:]))
        runIds = run_date + "." + machine_num + "." + day_run_num

        if not os.path.exists(download_path+"/"+run_date):
            os.mkdir(download_path+"/"+run_date)

        #create webdriver object
        self.scrapper_obj = ClearLabsApi(download_path+"/"+run_date,resource_path)

        
        #Log into ClearLabs
        self.scrapper_obj.login(self.clearlabs_url,self.cl_user,self.cl_pwd)
        
        
        #extract run info and download corresponding fastas files
        run_dump= self.scrapper_obj.find_runs(runId)

        #check if rundata is empty
        for key in [*run_dump]:
            if len(run_dump[key]) <= 1:
                    raise ValueError("Was not able to gather run info, CHECK CLEAR LABS SCRAPPER PY")

        #checking that compress file has downloaded before closing browswer
        compressed_file_name= self.download_wait(runId, run_date,download_path)

        #closing web browser
        self.scrapper_obj.driver.close()

        self.uncompress_file(download_path+"/"+run_date,compressed_file_name)

        #returning run information in a dic 
            #structure {'RunID':{'SampleID':[position,sampleID, type of analysis, seq_coverage, assembly_coverage]}}
        return run_dump


    def download_wait(self,runId, run_d,download_p):

        download_complete = True

        while download_complete:

            if os.path.exists(download_p+"/"+run_d+"/"+runId+"-all_bam_and_index_files.zip"):
                download_complete=False
                break
            else:
                print("Waiting on Download")
            time.sleep(10)
        
        return runId+"-all_bam_and_index_files.zip"
            
    def uncompress_file(self,downloaded_f_path,f_name):
        #will unzip file
        with zipfile.ZipFile(downloaded_f_path+"/"+f_name, 'r') as zip_ref:
            zip_ref.extractall(downloaded_f_path)
        
        print("File Decompressed")


    
    def close_conns(self):
        self.scrapper_obj.close_conns()







	
