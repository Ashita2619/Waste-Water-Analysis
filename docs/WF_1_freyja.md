# Workflow 1 Script
_______________________________________

## Annoates genome and Multilocus sequence typing

<br />

# WF_1_freyja.py

- **run_script_nextflow()**
    - Calls remove_bad_samples to remove samples with 0 or no coverage
    - Runs wasteWater.nf main process to run freyja

- **remove_bad_samples()**
    - Loops through samples and removes samples with 0 or no coverage

<br />

# wasteWater.nf

- **workflow()**
    - Runs freyja to create variant files
    - Takes output and then runs freyja demix process

- **workflow final_step()**
    - Runs freyja to create a aggregate demix file
    - Uses the aggregated file to create graph



<br />
