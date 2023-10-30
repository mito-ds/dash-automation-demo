# Mito Automation With Dash

This demo application shows how Mito can be used to automate spreadsheet processes. Namely, users of this Spreadsheet Automation Hub can:
1. Create a new Python automations by simply editing the Mito spreadsheet
2. Run these automations on new datasets

## How to Run

First, install dependencies:
```
pip install -r requirements.txt
```

Run the application with:
```
python main.py
```

## How to Use

### Creating a new automation

1. Click the `Create New Automation` button at the bottom of the main page. 
2. Configure the new automation wizard with the name, description, and timing of this automation. 
3. Use the Mito spreadsheet to create an automation. Import data, make edits, create your final dataset. **The final sheet tab in the Mito spreadsheet is taken as the result of the analysis**.
4. Click `Save Automation` to be able to run these edits on new data.

### Using an automation on new data

Now, you're ready to use the automation you created above on a new dataset:
1. Click on the `Click Here` button that appears on the New Automation page post save to navigate to your new automation.
2. See the automation name, description, and other metadata, and then use the Mito spradsheet to upload the new versions of your input datasets.
3. Click `Run Automation` to run your edits on these new datasets. Mito will automatically download a CSV of your final file.
