import os
import subprocess
import glob
import shutil


def run_script_nextflow(runDate,path_to_nextflow,download_path,run_id,run_datas,nextflow_workdir,ref_genome,output_path,coverage):
    print("\n================================\nNextflow Processes\n================================\n\n")
    path_to_bam= download_path+"/"+runDate+"/"+run_id+"_all_bam_and_index_files"

    print("Removing bad coverage Samples")
    remove_bad_samples(download_path,path_to_bam,run_datas)
    print("")
    
    #print("conda run -n WasteWater nextflow run "+path_to_nextflow+" --in '"+path_to_bam+"/*.bam' --run_date '"+runDate+"' --ref "+ref_genome+" --output_path "+output_path+" --cov "+coverage+" -w "+nextflow_workdir)
    #subprocess.run("export NXF_DISABLE_PARAMS_TYPE_DETECTION=true && conda run -n WasteWater nextflow run "+path_to_nextflow+" --in '"+path_to_bam+"/*.bam' --run_date '"+runDate+"' --ref "+ref_genome+" --output_path "+output_path+" --cov "+coverage+" -w "+nextflow_workdir,shell=True)
    #first flow
    conda_path = "/epi/home/ssh_user/mambaforge/etc/profile.d/conda.sh"
    subprocess.run(f"export TERM=linux && export CURL_CA_BUNDLE=/epi/home/ssh_user/mambaforge/envs/nextflow/ssl/cacert.pem && . {conda_path} && conda activate WasteWater && export NXF_DISABLE_PARAMS_TYPE_DETECTION=true && nextflow run "+path_to_nextflow+" --in '"+path_to_bam+"/*.bam' --run_date '"+runDate+"' --ref "+ref_genome+" --output_path "+output_path+" --cov "+coverage+" -w "+nextflow_workdir+" && source deactivate",shell=True)

    #second flow
    subprocess.run(f"export TERM=linux && export CURL_CA_BUNDLE=/epi/home/ssh_user/mambaforge/envs/nextflow/ssl/cacert.pem && . {conda_path} && conda activate WasteWater && export NXF_DISABLE_PARAMS_TYPE_DETECTION=true && nextflow run "+path_to_nextflow+" -entry final_step --run_date "+runDate+" --ref "+ref_genome+" --output_path "+output_path+" --cov "+coverage+" -w "+nextflow_workdir+" && source deactivate",shell=True)


    print("\n================================\nSUCCESS - END OF SCRIPT\n================================\n\n")


def remove_bad_samples(d_path, path_to_bam_f, run_data):
    failed_dir = os.path.join(d_path, "failed_samples")
    os.makedirs(failed_dir, exist_ok=True)

    for sample in run_data:
        coverage_status = run_data[sample][-1]

        try:
            # Normalize and validate coverage string
            if coverage_status in ["0%", "—"]:
                low_coverage = True
            elif coverage_status.endswith("%"):
                coverage_value = float(coverage_status.rstrip("%"))
                low_coverage = coverage_value <= 15
            else:
                print(f"Skipping sample {sample}: invalid coverage format '{coverage_status}'")
                continue

            if low_coverage:
                src_files = glob.glob(os.path.join(path_to_bam_f, f"{sample}*"))
                if not src_files:
                    print(f"No files found for sample: {sample}")
                for src_file in src_files:
                    print(f"Moving {src_file} to {failed_dir}")
                    shutil.move(src_file, failed_dir)
                print(f"Successfully moved {sample} to failed directory.")

        except Exception as e:
            print(f"Error processing sample {sample}: {e}")

    print("Continuing with Nextflow")

#def remove_bad_samples(d_path,path_to_bam_f,run_data):
    #for sample in [*run_data]:
        #coverage_status = run_data[sample][-1]
        #print(f"Checking sample: {sample}, Coverage: {coverage_status}")
        #if coverage_status == "0%" or coverage_status == "\u2014" or float(coverage_status[:-1]) <= 15:
            #try:
                # Use glob to find all matching files
             #   src_files = glob.glob(os.path.join(path_to_bam_f, f"{sample}*"))
              #  if not src_files:
               #     print(f"No files found for sample: {sample}")
                #for src_file in src_files:
                 #   print(f"Moving {src_file} to {failed_dir}")
                  #  shutil.move(src_file, failed_dir)
                #print(f"Successfully moved {sample} to failed directory.")
            #except Exception as e:
             #   print(f"Error moving {sample}: {e}")
    #print("Continuing with Nextflow")



if __name__ == "__main__":
    r=  {}
    #remove_bad_samples("/epi/home//Downloads/","/home//Downloads/",r)
