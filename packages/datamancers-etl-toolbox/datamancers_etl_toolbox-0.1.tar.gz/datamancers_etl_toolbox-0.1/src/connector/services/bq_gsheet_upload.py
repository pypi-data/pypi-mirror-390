import requests as r
import json
import logging
import time
import argparse
from google.cloud import bigquery
import os
import pygsheets
import re
import google.auth
import unicodedata
logging.basicConfig(level=logging.INFO)

## convert string with accented letters to regular letters and snake case
def to_snake_case(input_str):
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    only_ascii = nfkd_form.encode('ASCII', 'ignore')
    output= re.sub('_+','_',only_ascii

             .decode("utf-8")
             .lower()
             .replace(" ", "_")
             .replace("-", "_")
             .replace(":","_")
             )
    return output
class instance():
    def __init__(self, **kwargs):
        if "env_object" in kwargs:
            self.client = pygsheets.authorize(service_file=os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"))
        self.spreadsheets = self.client.spreadsheet_titles()
        if "spreadsheet_name" in kwargs:
            self.spreadsheet = self.client.open(kwargs["spreadsheet_name"])


class SpreadsheetExtract(object):
    def __init__(self, spreadsheet_name, gs, worksheet_title_regex):
        self.ss = gs.client.open(spreadsheet_name)
        self.worksheets = [i for i in self.ss.worksheets() if re.fullmatch(f"{worksheet_title_regex}", i.title)]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog='spreadsheet_extract',
        description='This helps extract heureka data'
    )
    parser.add_argument("GCP_PROJECT_ID")
    parser.add_argument("sheet_name")
    parser.add_argument("dataset")
    credentials, project = google.auth.default(
        scopes=[
            "https://www.googleapis.com/auth/cloud-platform",
            "https://www.googleapis.com/auth/drive",
            "https://www.googleapis.com/auth/bigquery",
        ]
    )
    parser.add_argument("--worksheet_title_regex", "-wtr", default=".*")
    arguments = parser.parse_args()

    logging.info(f"Look for worksheets in spreadsheet {arguments.sheet_name}  with regexp pattern: .*")

    worksheet_names = SpreadsheetExtract(spreadsheet_name=arguments.sheet_name,
                                         gs=instance(env_object="GOOGLE_APPLICATION_CREDENTIALS"),
                                         worksheet_title_regex=arguments.worksheet_title_regex).worksheets

    logging.info(f"Found {len(worksheet_names)} worksheets: {worksheet_names}")

    bq_client = bigquery.Client(arguments.GCP_PROJECT_ID,credentials)
    external_config = bigquery.ExternalConfig("GOOGLE_SHEETS")

    external_config.options.skip_leading_rows = 1



    for spreadsheet in worksheet_names:
        ## set schema for all columns
        col_names = [i for i in spreadsheet.get_values("A1", "AZ1")[0] if i != '']
        schema=[bigquery.SchemaField(to_snake_case(i), "STRING") for i in col_names]
        table = bigquery.Table(
            table_ref=f"{arguments.GCP_PROJECT_ID}."
                      f"{arguments.dataset}."
                      f"L0_GOOGLE_DRIVE__{to_snake_case(arguments.sheet_name)}__{to_snake_case(spreadsheet.title)}",
        schema=schema)



        external_config.source_uris = [spreadsheet.url]
        external_config.options.range = (spreadsheet.title)
        table.external_data_configuration = external_config

        table = bq_client.create_table(table)
        logging.info(f"Created table {table.table_id}")
