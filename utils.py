import json

def get_automation_json(
        analysis_name,
        analysis_description,
        hours_per_run,
        code_string,
        num_runs=[]
):
    return json.dumps({
        "automation_name": analysis_name,
        "automation_description": analysis_description,
        "hours_per_run": hours_per_run,
        "automation_code": code_string,
        "runs": num_runs
    })
