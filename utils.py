import json
import os
import sys

def get_automation_json(
        analysis_name,
        analysis_description,
        hours_per_run,
        runnable_analysis,
        num_runs=[]
):
    return json.dumps({
        "automation_name": analysis_name,
        "automation_description": analysis_description,
        "hours_per_run": hours_per_run,
        "analysis_json": runnable_analysis.to_json(),
        "runs": num_runs
    })

def get_file_name_from_automation_name(automation_name):
    """
    To make sure we can save the automation to a file, we need to make sure the file name is valid.

    We filter to letters, numbers, underscores, spaces, dashes, periods, and commas
    """
    from string import ascii_letters, digits
    valid_characters = ascii_letters + digits + ' _-.,'
    return ''.join([c for c in automation_name if c in valid_characters])

def read_automation_from_file(automation_name):
    """
    Read an automation from a file, given the automation name
    """
    file_name = get_file_name_from_automation_name(automation_name)
    if not os.path.exists(f'automations/{file_name}.json'):
        return None

    with open(f'automations/{file_name}.json') as f:
        automation_data = json.loads(f.read())
        return automation_data

def write_automation_to_file(automation_name, automation_description, hours_per_run, runnable_analysis, num_runs=[], overwrite=False):
    """
    Write an automation to a file, given the automation name
    """
    file_name = get_file_name_from_automation_name(automation_name)

    if not overwrite and os.path.exists(f'automations/{file_name}.json'):
        return False

    with open(f'automations/{file_name}.json', 'w') as f:
        f.write(get_automation_json(automation_name, automation_description, hours_per_run, runnable_analysis, num_runs))
        return True

def get_all_automations(max_num_automations=sys.maxsize):
    """
    A generator that yields all of the automations in the automations folder, that are in the format {automation_name}.json
    and have a valid json format from above
    """
    num_automations = 0
    for automation in os.listdir('automations'):
        if automation.endswith('.json'):
            with open(f'automations/{automation}') as f:
                try:
                    automation_data = json.load(f)
                except:
                    continue

                # Check the automation data is valid - all the feilds should be there
                if 'automation_name' not in automation_data or not isinstance(automation_data['automation_name'], str):
                    continue
                if 'automation_description' not in automation_data or not isinstance(automation_data['automation_description'], str):
                    continue
                if 'hours_per_run' not in automation_data or not isinstance(automation_data['hours_per_run'], int):
                    continue
                if 'analysis_json' not in automation_data or not isinstance(automation_data['analysis_json'], str):
                    continue
                if 'runs' not in automation_data or not isinstance(automation_data['runs'], list):
                    continue
                
                num_automations += 1
                yield automation_data

                if num_automations >= max_num_automations:
                    break