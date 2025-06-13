from WF_0_scrape_web.WF_0_helpers import WF_0_ClearLabs
import json
import os



def run_script_0(run_ids, res_path, download_p, cl_url, cl_username, cl_password, runDate):
    print("\n================================\nScrape Web Script\n================================\n\n")

    # Create ClearLabs scraper object
    data_obj = WF_0_ClearLabs(cl_url, cl_username, cl_password)

    # Get run information
    run_info = data_obj.scrape(run_ids, res_path, download_p)

    # Remove unwanted "Sample ID" key if present
    run_info.pop("Sample ID", None)

    # Build output path
    abs_path = os.path.join(res_path, "data", f"{runDate}_run_data.json")

    # Save to JSON file in compact (one-line-per-entry) format
    with open(abs_path, "w") as j_dump:
        json.dump(run_info, j_dump, separators=(',', ':'))

    # Close browser/session/etc.
    data_obj.close_conns()

    return run_info

    print("\n================================\nSUCCESS - END OF SCRIPT\n================================\n\n")


 

 
