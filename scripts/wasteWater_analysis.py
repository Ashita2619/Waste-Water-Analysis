from WF_0_scrape_web.WF_0_scrape_web import run_script_0
from WF_1_freyja.WF_1_freyja import run_script_nextflow
from WF_2_DB.WF_2_DB_push import DB_push
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

        #If clear labs files already on machine will not re-download
        if os.path.exists(self.cache_path+"/data/"+run_date+"_run_data.json"):
            print("\nClear Lab Files already Downloaded continuing with Freyja\n")
            with open(self.cache_path+"/data/"+run_date+"_run_data.json") as json_file:
                run_specfic_data = json.load(json_file)
        else:
            run_specfic_data=run_script_0(run_ID,self.cache_path,self.download_path,self.cl_url,self.cl_username,self.cl_pwd,run_date)
        
        #only when data is already downloaded
        #with open(self.cache_path+"/data/run_data.json") as json_file:
        #    run_specfic_data = json.load(json_file)

        # Run Freyja script
        run_script_nextflow(run_date,self.cache_path+"/scripts/WF_1_freyja/wasteWater.nf",self.download_path,run_ID,run_specfic_data,self.nextflow_working_dir,self.referance_genome,self.waste_water_output,self.displayed_coverage)
        
        self.remove_nextflow_work()

        #PUSH TO DB
        #list of HSN's to know what demographics to pull
        DB_push(self.cache_path,[*run_specfic_data],run_date,self.waste_water_output,run_specfic_data)
        
        # #Uncomment this if its not a full run of 16 samples
        # # Filter out invalid samples (e.g., Blank1 and Blank2)
        # valid_samples = self.filter_valid_samples(run_specfic_data)

        # # Push only valid samples to the database
        # self.push_valid_samples_to_db(valid_samples,run_date, run_specfic_data)
        
    def remove_nextflow_work(self):
        
        if os.path.exists(self.nextflow_working_dir):
            subprocess.run("rm -r "+self.nextflow_working_dir,shell=True)
            print("Removing Nextflow WorkDir")

# Uncomment this if its not a full run of 16 samples
    # def filter_valid_samples(self, run_specfic_data):
    #     # Filter out Blank1 and Blank2 samples or any other invalid samples
    #     valid_samples = [sample for sample in run_specfic_data if sample not in ['Blank1', 'Blank2']]
    #     return valid_samples
    
    # def push_valid_samples_to_db(self, valid_samples, run_date, run_specfic_data):
    #     # Assuming you have a function to push data to the database
    #     for sample_id in valid_samples:
    #         # Push sample data to the database
    #         DB_push(self.cache_path, [sample_id], run_date, self.waste_water_output, run_specfic_data)



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

    
