import os
import subprocess





def run_script_nextflow(runDate,path_to_nextflow,download_path,run_id,run_datas):
    print("\n================================\nScrape Web Script\n================================\n\n")
    path_to_bam= download_path+"/"+runDate+"/"+run_id+"-all_bam_and_index_files"

    remove_bad_samples(download_path,path_to_bam,run_datas)

    #first flow
    subprocess.run(". $CONDA_PREFIX/home/ssh_user/mambaforge/etc/profile.d/conda.sh && conda activate WasteWaster && nextflow run "+path_to_nextflow+" --in '"+path_to_bam+"/*.bam' --run_date "+runDate+" && source deactivate",capture_output=True, text=True,shell=True)

    #second flow
    subprocess.run(". $CONDA_PREFIX/home/ssh_user/mambaforge/etc/profile.d/conda.sh && conda activate WasteWaster && nextflow run "+path_to_nextflow+" -entry final_step --in '"+path_to_bam+"/*.bam' --run_date "+runDate+" && source deactivate",capture_output=True, text=True,shell=True)


    print("\n================================\nSUCCESS - END OF SCRIPT\n================================\n\n")



def remove_bad_samples(d_path,path_to_bam_f,run_data):
    for sample in [*run_data]:
        if run_data[sample][-1] == "0%" or run_data[sample][-1] == "\u2014" :
            #then remove/files to failed areas
            print("HSN\t"+sample+" failed or 0 coverage")
            subprocess.run("mv "+path_to_bam_f+"/"+sample+"* "+d_path+"/failed/",shell=True)



if __name__ == "__main__":
    r=  {"2600413": ["A01", "2600413", "Seq 2", "35.57", "63.78%"], "2599371": ["B01", "2599371", "Seq 2", "35.63", "48.6%"], "2600515": ["C01", "2600515", "Seq 2", "35.51", "36.15%"], "2600409": ["D01", "2600409", "Seq 2", "35.62", "40.58%"], "2601558": ["E01", "2601558", "Seq 2", "35.56", "23.24%"], "2600412": ["F01", "2600412", "Seq 2", "35.73", "33.76%"], "2599369": ["G01", "2599369", "Seq 2", "35.59", "23.55%"], "2599367": ["H01", "2599367", "Seq 2", "35.71", "17.26%"], "2599372": ["A02", "2599372", "Seq 2", "35.67", "23.88%"], "2599368": ["B02", "2599368", "Seq 2", "35.61", "27.75%"], "2600408": ["C02", "2600408", "Seq 2", "35.69", "13.3%"], "2600206": ["D02", "2600206", "Seq 2", "35.72", "5.02%"], "2599370": ["E02", "2599370", "Seq 2", "35.61", "14.48%"], "2593110": ["F02", "2593110", "Seq 2", "35.6", "7.64%"], "2589240": ["G02", "2589240", "Seq 2", "35.61", "0%"], "2589242": ["H02", "2589242", "Seq 2", "35.59", "\u2014"]}
    remove_bad_samples("/home/adrianlimagaray/Downloads/","/home/adrianlimagaray/Downloads/110723/BHRL11.2023-11-07.01_all_bam_and_index_files",r)