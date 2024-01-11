import os
import subprocess



def run_script_nextflow(runDate,path_to_nextflow,download_path,run_id,run_datas,nextflow_workdir,ref_genome,output_path,coverage):
    print("\n================================\nNextflow Processes\n================================\n\n")
    path_to_bam= download_path+"/"+runDate+"/"+run_id+"_all_bam_and_index_files"

    print("Removing bad coverage Samples")
    remove_bad_samples(download_path,path_to_bam,run_datas)
    print(". $CONDA_PREFIX/home/ssh_user/mambaforge/etc/profile.d/conda.sh && conda activate WasteWater && nextflow run "+path_to_nextflow+" --in '"+path_to_bam+"/*.bam' --run_date '"+runDate+"' --ref "+ref_genome+" --output_path "+output_path+" --cov "+coverage+" -w "+nextflow_workdir+" && source deactivate")
    #first flow
    subprocess.run(". $CONDA_PREFIX/home/ssh_user/mambaforge/etc/profile.d/conda.sh && conda activate WasteWater && export NXF_DISABLE_PARAMS_TYPE_DETECTION=true && nextflow run "+path_to_nextflow+" --in '"+path_to_bam+"/*.bam' --run_date '"+runDate+"' --ref "+ref_genome+" --output_path "+output_path+" --cov "+coverage+" -w "+nextflow_workdir+" && source deactivate",shell=True)

    #second flow
    subprocess.run(". $CONDA_PREFIX/home/ssh_user/mambaforge/etc/profile.d/conda.sh && conda activate WasteWater && export NXF_DISABLE_PARAMS_TYPE_DETECTION=true && nextflow run "+path_to_nextflow+" -entry final_step --run_date "+runDate+" --ref "+ref_genome+" --output_path "+output_path+" --cov "+coverage+" -w "+nextflow_workdir+" && source deactivate",shell=True)


    print("\n================================\nSUCCESS - END OF SCRIPT\n================================\n\n")



def remove_bad_samples(d_path,path_to_bam_f,run_data):
    for sample in [*run_data]:
        if run_data[sample][-1] == "0%" or run_data[sample][-1] == "\u2014" or float(run_data[sample][-1][:-1]) <= 5  :
            #then remove/files to failed areas
            print("HSN\t"+sample+" failed or 0 coverage")
            subprocess.run("mv "+path_to_bam_f+"/"+sample+"* "+d_path+"/failed/",shell=True)
    print("Continuing with Nextflow")



if __name__ == "__main__":
    r=  {}
    #remove_bad_samples("/home//Downloads/","/home//Downloads/",r)