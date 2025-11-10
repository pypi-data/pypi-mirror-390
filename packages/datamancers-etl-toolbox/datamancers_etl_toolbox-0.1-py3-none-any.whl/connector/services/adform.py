###############################################################################
############## Extractor Configuration ########################################
###############################################################################

start_date = "2022-03-01"
end_date = "2030-01-01"
reported_dimensions = ["client", "date", "campaign", "lineItem", "media"]
reported_metrics = [
  	"rtbBids",
    "rtbBrandSafetyCost",
    "rtbAdformIncludedFee",
    "rtbMediaCost",
    "rtbContextualTargetingCost",
    "rtbCrossDeviceCost",
    "impressions",
    "viewImpressions",
    "clicks", "cost"
]


ADFORM_CLIENT_ID = "eapi.analytics.cyberfootprint.cz@clients.adform.com" # "ENTER CLIENTID HERE"
ADFORM_CLIENT_SECRET = "YlPnc3SJ_fi1D3O1IjtHLSunU8WIun8iRrzbOtna" # 'ENTER CLIENT SECRET HERE'
SCOPE = 'https://api.adform.com/scope/buyer.stats'
STORAGE_PATH = "out/tables"
###############################################################################
############## Code Start #####################################################
###############################################################################

# main.py
import subprocess
import sys
import os


def install_packages():
    # Prevent docker conflict during requests/urllib3 downgrade
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "uninstall", "-y", "docker"])
        subprocess.check_call([sys.executable, "-m", "pip", "uninstall", "-y", "mlflow"])
        print("Uninstalled docker to avoid pip resolver conflicts.")
    except subprocess.CalledProcessError:
        print("Docker wasn't installed or couldn't be removed cleanly. Continuing.")

    MARKER_FILE = "/tmp/.packages_installed"

    if not os.path.exists(MARKER_FILE):
        print("🔧 Installing compatible package versions (this will run once)...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--no-cache-dir", "--force-reinstall",
            "numpy==1.23.5",
            "pandas==1.5.3",
            "numexpr==2.8.4",
            "charset-normalizer==2.1.1",
            "pytz==2022.7",
            "requests==2.23.0",
            "urllib3==1.25.11",
            "idna==2.9"
        ])
        # Prevent infinite loops
        with open(MARKER_FILE, "w") as f:
            f.write("ok")
        print("🔁 Restarting script to apply fixed versions...")
        subprocess.call([sys.executable, *sys.argv])
        sys.exit()

#### Import packages ##########################

import requests
import time
import datetime as dt
import json
import pandas as pd
from datetime import datetime

#### Authenticate and obtain access token ######

def get_access_token(client_id, client_secret):
    url = 'https://id.adform.com/sts/connect/token'
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    data = {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret,
        'scope': SCOPE
    }
    response = requests.post(url, headers=headers, data=data)
    response.raise_for_status()
    print("Access token retrieved.")
    return response.json()['access_token']

#### Submit report request ######################

def submit_report_request(token, payload):
    try:
        url = 'https://api.adform.com/v1/buyer/stats/data'
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        print("Report request submitted.")
        return response.headers['Location'].split('/')[-1]
    except Exception as e:
        print(f"Error submitting report request: {e}, response: {response.text}")
        raise e


#### Poll for report completion ################

def poll_report_status(token, operation_id, max_attempts=15, delay=10):
    url = f'https://api.adform.com/v1/buyer/stats/data/{operation_id}'
    headers = {'Authorization': f'Bearer {token}'}
    print("Reaching for the data.")
    for attempt in range(max_attempts):
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            response_json=response.json()
            return response_json
        except Exception as e:
            print(f"Error polling report status: {e}, response: {response.text}")
            
        time.sleep(delay*attempt)
    raise TimeoutError('Report generation timed out.')

#### Main execution ############################

def main():
    # Define report parameters
    payload = {
        "dimensions": reported_dimensions,
        "metrics": reported_metrics,
        "filter": {
            "date": {
                "from": f"{start_date}T00:00:00.0000000Z",
                "to": f"{end_date}T00:00:00.0000000Z"
            }
        },
        "paging": {
            "limit": 0
        },
        "includeRowCount": False,
        "includeTotals": False,
        "sort": [
            {
                "dimension": "date",
                "direction": "desc"
            },
            {
                "metric": "impressions",
                "direction": "asc"
            }
        ]
    }

    try:
        token = get_access_token(ADFORM_CLIENT_ID, ADFORM_CLIENT_SECRET)
        operation_id = submit_report_request(token, payload)
        report_data = poll_report_status(token, operation_id)
        print("Data returned")
        rows = report_data['reportData']['rows']
        headers = report_data['reportData']['columnHeaders']
        df = pd.DataFrame(rows, columns=headers)
        df=df.loc[df["client"]=="Neocity",:]
        df['extractionDatetime'] = datetime.now()
        df.to_csv(f'{STORAGE_PATH}/ex_adform.csv', index=False)
        print("Report successfully retrieved and saved.")
    except Exception as e:
        print(f"An error occurred: {e}")


#install_packages()
main()