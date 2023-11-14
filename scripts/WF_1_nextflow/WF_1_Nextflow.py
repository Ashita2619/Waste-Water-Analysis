import os
import subprocess





def run_script_nextflow(runDate,path_to_nextflow,download_path,run_id):
    print("\n================================\nScrape Web Script\n================================\n\n")
    path_to_bam= download_path+"/"+runDate+"/"+run_id+"-all_bam_and_index_files"

    #first flow
    subprocess.run(". $CONDA_PREFIX/home/ssh_user/mambaforge/etc/profile.d/conda.sh && conda activate WasteWaster && nextflow run "+path_to_nextflow+" --in '"+path_to_bam+"/*.bam' --run_date "+runDate+" && source deactivate",capture_output=True, text=True,shell=True)

    #second flow
    subprocess.run(". $CONDA_PREFIX/home/ssh_user/mambaforge/etc/profile.d/conda.sh && conda activate WasteWaster && nextflow run "+path_to_nextflow+" -entry final_step --in '"+path_to_bam+"/*.bam' --run_date "+runDate+" && source deactivate",capture_output=True, text=True,shell=True)


    print("\n================================\nSUCCESS - END OF SCRIPT\n================================\n\n")



def run_nextflow(path_to_nextflow_file,runDate,path_to_bam):

    #first flow
    subprocess.run(". $CONDA_PREFIX/home/ssh_user/mambaforge/etc/profile.d/conda.sh && conda activate WasteWaster && nextflow run "+path_to_nextflow_file+" --in '"+path_to_bam+"/*.bam' --run_date "+runDate+" && source deactivate",capture_output=True, text=True,shell=True)

    #second flow
    subprocess.run(". $CONDA_PREFIX/home/ssh_user/mambaforge/etc/profile.d/conda.sh && conda activate WasteWaster && nextflow run "+path_to_nextflow_file+" -entry final_step --in '"+path_to_bam+"/*.bam' --run_date "+runDate+" && source deactivate",capture_output=True, text=True,shell=True)
