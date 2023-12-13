# Workflow 0 Script
_______________________________________

## Downloads and Scrapes samples from ClearLabs

<br />

# ClearLabsScrapper.py

- **ClearLabsApi()**
    - Class which contains a wrapper script using selenium to transverse the clear labs website
    - Logs in to clear labs for entered user
    - Downloads all assocaited BAM and fastq files for entered run id

<br />

# WF_0_scrape_web.py

- **run_script_0()**
    - Calls WF_O_ClearLabs class from helper.py
    - Jumps run data scrapped from clear labs to json file
    - Returns run data

<br />

# WF_0_helper.py

- **WF_0_ClearLabs()**
    - Class to use ClearLabsApi 
    - Scrapes run information from clear labs
    - Uncompresses zip files





<br />
