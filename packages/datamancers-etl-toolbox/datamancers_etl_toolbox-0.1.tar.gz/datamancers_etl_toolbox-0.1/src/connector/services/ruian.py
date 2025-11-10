## https://connection.north-europe.azure.keboola.com/admin/projects/19859/transformations-v2/keboola.python-transformation-v2/76462291
## This script is used to extract the data from the SUKL website and save it in the OUTPUT_FOLDER
import requests as r
import re
import pandas as pd
from zipfile import ZipFile
import io
import csv
import sys
import logging
import os
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
# VARIABLES
## destination url where the zip file link is present
#URL = 'https://nahlizenidokn.cuzk.cz/stahniadresnimistaruian.aspx'
## regex pattern to extract the zip file link
#ZIP_FILE_REGEXP_PATTERN='https://vdp\\.cuzk\\.cz/vymenny_format/csv/\\d{10}_OB_ADR_csv\\.zip'
## extract timestamp
EXTRACT_TIMESTAMP = pd.Timestamp.now()
## folder where the extracted data will be saved
OUTPUT_FOLDER=""

## fetch the html text from the url
#response=r.get(URL)
## extract all links from the html text
#links=re.findall(r'href="([^"]+)"',response.text)
## extract the link which contains the zip file with zip_file_regexp_pattern

    #[i for i in links if re.findall(ZIP_FILE_REGEXP_PATTERN,i)][0]

def extract_data(file_name_date):
    zip_link = f'https://vdp.cuzk.cz/vymenny_format/csv/{file_name_date}_OB_ADR_csv.zip'
    ### fetch the zip file from the sukl_link
    logging.warning(f"Extracting data from {zip_link}")
    response=r.get(zip_link)
    logging.warning(f"Response status code: {response.status_code}")
    ## open the zip file
    z = ZipFile(io.BytesIO(response.content))
    ## extract the zip file to the folder
    z.extractall(OUTPUT_FOLDER)

    ## for all files under the zip file
    for idx,i in enumerate(z.namelist()):
        ## open the file
        with z.open(i) as f:
            ## read the file and decode it
            data=io.TextIOWrapper(f,encoding="windows-1250")
            ## convert the csv data to pandas dataframe
            csv_data=pd.read_csv(data,sep=";",header=0)
            ## add the extract timestamp to the csv data
            csv_data["extract_timestamp"]=EXTRACT_TIMESTAMP
            ## add the source url to the csv data
            csv_data["source_url"]=zip_link
            mode_type="a" if idx>0 else "w"
            csv_data.to_csv(OUTPUT_FOLDER+"ruian_addresses",mode=mode_type, quoting=csv.QUOTE_NONNUMERIC, quotechar='"',sep=',',index=False,header=1 if idx==0 else False)
            logging.info(f"File {i} extracted successfully")
            os.remove(OUTPUT_FOLDER+i)

if __name__ == "__main__":
    file_name_date = sys.argv[1]
    extract_data(file_name_date)
    logging.warning("Data extraction finished successfully")