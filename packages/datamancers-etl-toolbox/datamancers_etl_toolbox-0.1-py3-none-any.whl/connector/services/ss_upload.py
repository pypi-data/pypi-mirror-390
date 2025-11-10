from ss_extract_data import instance

ss=instance(env_object="GCP_CREDS",spreadsheet_name="Sledování rozložení zásob")

ss.spreadsheet.worksheet_by_title("Sheet1").