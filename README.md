# General Package for State Lab WasteWater Clade Analysis
_______________________________________

Please note this package is being used in conjustion with ClearLabs waste water analysis
Workflow should be run after ClearLabs analysis is completed 
> Clear Labs handles the sequencing and alignment of samples producing BAM files

## Quick Start Installation

  1. Install necessary conda ENV from [WasteWater.yml](/resources/WasteWater.yml) file in resources 
  > Needed for sucessful analysis

```
  conda env create -f WasteWater.yaml
  #run to test installing sucessful
  conda activate WasteWater
```


<br />

## Before Running update Variables

  1. Update necessary locations in [Pipeline_Variable.json](/data/pipeline_variables.json) for your system
  2. Check your current version of Chrome and update [ChromeDriver](/resources/chromedriver-linux64/) to your respective version
  >This is only needed if downloading results from ClearLabs/other website

<br />

## Running Workflow

### Run Waste Water Analysis
  1. Run [wasteWater_analysis.py](/scripts/wasteWater_analysis.py) which takes the clear labs run ID as the input
 
```python 
  python wasteWater_analysis.py ClearLabsRunID
```
 > See 

<br />

## The package contains the following workflows in their respective subdirectories:

<br />

### **Workflow 0:** [Scrape_Web](/docs/WF_0_scrape_web.md)
 - Navigates to ClearLabs website
 - Log in using Private_cache.json file variables located in the data folder
 - After logged in the script scrapes run information and downloads BAM, and fastq files
 
<br />
<br />

### **Workflow 1:** [Freyja Analysis](/docs/WF_1_freyja.md)
 - Takes BAM files from ClearLabs and runs [Freyja](https://github.com/andersen-lab/Freyja)
 - This will produce a final pdf reports showing lineage break down of samples for given coverage
 

<br />
<br />