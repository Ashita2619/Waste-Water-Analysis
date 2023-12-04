from WF_0_scrape_web.WF_0_scrape_web import run_script_0
from WF_1_nextflow.WF_1_Nextflow import run_script_nextflow
import os
import sys
import json
import datetime
import subprocess



class WasteWater_pipeline_worker():

    def __init__(self, cache_path) :
        self.cache_path = cache_path

        with open(cache_path+"/data/pipeline_variables.json", 'r') as json_cache1:
            demo_cahce = json.load(json_cache1)
        
        with open(cache_path+"/data/private_cache.json", 'r') as json_cache2:
            private_cahce = json.load(json_cache2)

        for item in [*demo_cahce] :
            setattr(self,item, demo_cahce[item])
        for item in [*private_cahce] :
            setattr(self,item, private_cahce[item])
    

    def wastewater_pipeline(self,run_ID):
        run_date= datetime.datetime.strptime(run_ID[7:17], '%Y-%m-%d').strftime("%m%d%y")
        
        run_specfic_data=run_script_0(run_ID,self.cache_path,self.download_path,self.cl_url,self.cl_username,self.cl_pwd)
        
        run_script_nextflow(run_date,self.cache_path+"/scripts/WF_1_nextflow/wasteWater.nf",self.download_path,run_ID,run_specfic_data,self.nextflow_working_dir)
        
        self.remove_nextflow_work()
        
    def remove_nextflow_work(self):
        
        if os.path.exists(self.nextflow_working_dir):
            subprocess.run("rm -r "+self.nextflow_working_dir,shell=True)
            print("Removing Nextflow WorkDir")
            


if __name__ == "__main__":
    
    dir_path = "/".join(os.path.dirname(os.path.realpath(__file__)).split("/")[:-1]) #path minus scripts 
    #print(dir_path)
    
    #inputs need to be ClearLabs Run NAme
    print(sys.argv)
    run_name = sys.argv[1]
   
    print(run_name)
    print("-----------")

    WasteWater_p = WasteWater_pipeline_worker(dir_path)
    WasteWater_p.wastewater_pipeline(run_name)

    
