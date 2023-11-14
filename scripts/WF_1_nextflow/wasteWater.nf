#!/usr/bin/env nextflow

params.in = "/home/ssh_user/WGS_Drive/wasteWater/clearLabFiles/100723/*.bam"
params.run_date = "100723"
params.output_path="/home/ssh_user/WGS_Drive/wasteWater/output"
params.ref = "/home/ssh_user/WGS_Drive/wasteWater/refseq/MN908947_RefSeq.fasta"




process create_var{
	//debug true

	tag "$sample_id"

	publishDir "${params.output_path}/${params.run_date}", mode:'copy'

	input:
		tuple val(sample_id), file(bam) 
		path o_path
		path referance
		val r_date
	output:
		tuple val(sample_id), file("${sample_id}_variant.tsv"), file ("${sample_id}_depth") 
 
	script:

	"""
	freyja variants $bam --variants "${sample_id}_variant" --depths "${sample_id}_depth" --ref $referance  
	"""

}

process demix{
	
	tag "$sample_id"

	publishDir "${params.output_path}/${params.run_date}/final/", mode:'copy'
	

	input:
		tuple val(sample_id), file(var) ,file(depth)
	output:
		file "${sample_id}.final"
	script:
	"""
	freyja demix $var $depth --output "${sample_id}.final"
	"""

}

process create_aggre{
	
	publishDir "${params.output_path}/${params.run_date}/final/", mode:'copy'

	input:
		path demix_out
		val run_date

	output:
		file "${run_date}_all.tsv"

	script:
	"""
	freyja aggregate "${demix_out}/${run_date}/final/" --output "${run_date}_all.tsv"
	"""
}

process create_graphs{
	publishDir "${params.output_path}/${params.run_date}/final", mode:'copy'
	
	input:
		path demix_out
		val run_date

	output:
		file "${run_date}.pdf"

	script:
	"""
	freyja plot "${run_date}_all.tsv" --mincov 5 --output "${run_date}.pdf"
	"""
}

workflow final_step{
	//agreeate all variant files into one
	agree_file = create_aggre(params.output_path,params.run_date)
	//Creating final report, setting coverage to 5 to see all results
	create_graphs(agree_file,params.run_date)
	
}

workflow{
	//Read BAM files download from ClearLabs (This is post assembly)
	bams = Channel.fromPath(params.in)
	//Formating files 
	formatted_bams = bams.map{
	file -> 
	prefix = file.name.split("-")[0]
	return[prefix,file]
	}
	//formatted_bams.view()
	//Creating a variant file for each BAM file
	create_var_ch = create_var(formatted_bams,params.output_path,params.ref,params.run_date)
	//create_var_ch.view()
	//Create a final report 
	demix(create_var_ch)

}
