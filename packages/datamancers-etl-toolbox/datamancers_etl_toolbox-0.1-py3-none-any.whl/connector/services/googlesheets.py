#!/usr/bin/env python3
import os
import json
import logging
import argparse
import pandas as pd
from googleapiclient.discovery import build
from google.oauth2 import service_account
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()


def fetch_google_sheets_data(spreadsheet_id: str, sheet_name: str, credentials_path: str, output_type: str = "json"):
    """
    Fetch data from Google Sheets and return it in the specified format.
    
    Args:
        spreadsheet_id: The ID of the Google Sheets document
        sheet_name: The name of the sheet to extract data from
        credentials_path: Path to the Google service account credentials file
        output_type: Format to return the data in ("json", "csv", or "pandas")
        
    Returns:
        Data in the specified format (list of dicts, CSV string, or pandas DataFrame)
    """
    # Load credentials
    credentials = service_account.Credentials.from_service_account_file(
        credentials_path, 
        scopes=['https://www.googleapis.com/auth/spreadsheets.readonly']
    )
    
    # Build the Google Sheets API service
    service = build('sheets', 'v4', credentials=credentials)
    
    # Call the Sheets API to get data
    logger.info(f"Fetching data from spreadsheet: {spreadsheet_id}, sheet: {sheet_name}")
    sheet = service.spreadsheets()
    result = sheet.values().get(
        spreadsheetId=spreadsheet_id,
        range=sheet_name
    ).execute()
    
    # Extract values from the result
    values = result.get('values', [])
    
    if not values:
        logger.warning("No data found in the specified sheet.")
        return [] if output_type in ["json", "pandas"] else ""
    
    logger.info(f"Fetched {len(values) - 1} rows of data")
    
    # Convert to list of dictionaries (assuming first row contains headers)
    headers = values[0]
    rows = []
    
    for row_values in values[1:]:
        # Ensure row has same length as headers by padding with empty strings if needed
        padded_values = row_values + [''] * (len(headers) - len(row_values))
        rows.append(dict(zip(headers, padded_values[:len(headers)])))
    
    # Return data in the requested format
    if output_type == "json":
        return rows
    elif output_type == "csv":
        # Convert to CSV string
        csv_rows = [",".join(headers)]
        for row in values[1:]:
            padded_row = row + [''] * (len(headers) - len(row))
            csv_rows.append(",".join(str(v) for v in padded_row[:len(headers)]))
        return "\n".join(csv_rows)
    elif output_type == "pandas":
        return pd.DataFrame(rows)
    else:
        raise ValueError(f"Invalid output type: {output_type}")


def main():
    parser = argparse.ArgumentParser(description='Google Sheets Extractor')
    parser.add_argument('--spreadsheet_id', type=str, required=True, help='Google Sheets spreadsheet ID')
    parser.add_argument('--sheet_name', type=str, required=True, help='Name of the sheet to extract')
    parser.add_argument('--output', type=str, default='sheets_data.json', help='Output file name')
    parser.add_argument('--format', type=str, choices=['json', 'csv'], default='json', 
                        help='Output format (json or csv)')
    args = parser.parse_args()

    # Get credentials from environment
    credentials_path = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
    
    if not credentials_path or not os.path.isfile(credentials_path):
        logger.error("GOOGLE_APPLICATION_CREDENTIALS not set or file does not exist.")
        exit(1)

    try:
        # Fetch data from Google Sheets
        results = fetch_google_sheets_data(
            args.spreadsheet_id, 
            args.sheet_name, 
            credentials_path,
            args.format
        )
        
        # Save data to output file
        if args.format == 'json':
            with open(args.output, 'w') as f:
                for row in results:
                    json.dump(row, f)
                    f.write('\n')
        else:  # csv
            with open(args.output, 'w') as f:
                f.write(results)
                
        logger.info(f"Data saved to {args.output}")
        
    except Exception as e:
        logger.error("Error occurred: %s", str(e))
        exit(1)


if __name__ == "__main__":
    main() 