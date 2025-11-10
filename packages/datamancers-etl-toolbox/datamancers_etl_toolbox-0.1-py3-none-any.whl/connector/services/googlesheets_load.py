#!/usr/bin/env python3
import os
import json
import csv
import logging
import argparse
import pandas as pd
from googleapiclient.discovery import build
from google.oauth2 import service_account
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()


def upload_to_google_sheets(
    data,
    spreadsheet_id: str,
    sheet_name: str,
    credentials_path: str,
    clear_sheet: bool = False,
    append: bool = False,
):
    """
    Upload data to a Google Sheet.

    Args:
        data: List of dictionaries or pandas DataFrame containing the data to upload
        spreadsheet_id: The ID of the Google Sheets document
        sheet_name: The name of the sheet to upload data to
        credentials_path: Path to the Google service account credentials file
        clear_sheet: Whether to clear the sheet before uploading (default: False)
        append: Whether to append data to existing data (default: False)

    Returns:
        Dictionary with upload status and details
    """
    # Load credentials
    credentials = service_account.Credentials.from_service_account_file(
        credentials_path, scopes=["https://www.googleapis.com/auth/spreadsheets"]
    )

    # Build the Google Sheets API service
    service = build("sheets", "v4", credentials=credentials)
    sheet = service.spreadsheets()

    # Convert data to list of lists for API
    if isinstance(data, pd.DataFrame):
        # Convert DataFrame to list of lists
        values = [data.columns.tolist()]  # Headers
        values.extend(data.values.tolist())
    else:
        # Convert list of dicts to list of lists
        if not data:
            logger.warning("No data to upload")
            return {"status": "warning", "message": "No data to upload"}

        headers = list(data[0].keys())
        values = [headers]
        for row in data:
            values.append([row.get(header, "") for header in headers])

    # Prepare for upload
    if clear_sheet:
        logger.info(f"Clearing sheet: {sheet_name}")
        try:
            # Get sheet ID
            sheet_metadata = sheet.get(spreadsheetId=spreadsheet_id).execute()
            sheets = sheet_metadata.get("sheets", [])
            sheet_id = None

            for s in sheets:
                if s["properties"]["title"] == sheet_name:
                    sheet_id = s["properties"]["sheetId"]
                    break

            if sheet_id is not None:
                # Clear sheet content
                sheet.batchUpdate(
                    spreadsheetId=spreadsheet_id,
                    body={
                        "requests": [
                            {
                                "updateCells": {
                                    "range": {
                                        "sheetId": sheet_id,
                                        "startRowIndex": 0,
                                        "startColumnIndex": 0,
                                    },
                                    "fields": "userEnteredValue",
                                }
                            }
                        ]
                    },
                ).execute()
            else:
                logger.warning(f"Sheet '{sheet_name}' not found. Will create it.")
        except Exception as e:
            logger.error(f"Error clearing sheet: {str(e)}")
            return {"status": "error", "message": f"Error clearing sheet: {str(e)}"}

    # Upload data
    try:
        if append:
            logger.info(f"Appending data to sheet: {sheet_name}")
            result = (
                sheet.values()
                .append(
                    spreadsheetId=spreadsheet_id,
                    range=sheet_name,
                    valueInputOption="RAW",
                    insertDataOption="INSERT_ROWS",
                    body={"values": values},
                )
                .execute()
            )
        else:
            logger.info(f"Uploading data to sheet: {sheet_name}")
            result = (
                sheet.values()
                .update(
                    spreadsheetId=spreadsheet_id,
                    range=sheet_name,
                    valueInputOption="RAW",
                    body={"values": values},
                )
                .execute()
            )

        logger.info(f"Upload successful. Updated {result.get('updatedCells')} cells.")
        return {
            "status": "success",
            "updatedRows": result.get("updatedRows"),
            "updatedColumns": result.get("updatedColumns"),
            "updatedCells": result.get("updatedCells"),
        }
    except Exception as e:
        logger.error(f"Error uploading data: {str(e)}")
        return {"status": "error", "message": str(e)}


def load_data_from_file(file_path: str):
    """
    Load data from a JSON or CSV file.

    Args:
        file_path: Path to the input file

    Returns:
        List of dictionaries containing the data
    """
    logger.info(f"Loading data from {file_path}")

    if not os.path.isfile(file_path):
        logger.error(f"File not found: {file_path}")
        return None

    file_ext = os.path.splitext(file_path)[1].lower()

    try:
        if file_ext == ".json":
            # Handle both JSON array and newline-delimited JSON
            with open(file_path, "r") as f:
                content = f.read().strip()
                if content.startswith("["):
                    # JSON array
                    return json.loads(content)
                else:
                    # Newline-delimited JSON
                    return [
                        json.loads(line) for line in content.split("\n") if line.strip()
                    ]

        elif file_ext == ".csv":
            with open(file_path, "r", newline="") as f:
                reader = csv.DictReader(f)
                return list(reader)

        else:
            logger.error(f"Unsupported file format: {file_ext}")
            return None

    except Exception as e:
        logger.error(f"Error loading data: {str(e)}")
        return None


def main():
    parser = argparse.ArgumentParser(description="Google Sheets Uploader")
    parser.add_argument(
        "--input", type=str, required=True, help="Input file (JSON or CSV)"
    )
    parser.add_argument(
        "--spreadsheet_id", type=str, required=True, help="Google Sheets spreadsheet ID"
    )
    parser.add_argument(
        "--sheet_name", type=str, required=True, help="Name of the sheet to upload to"
    )
    parser.add_argument(
        "--clear", action="store_true", help="Clear sheet before uploading"
    )
    parser.add_argument(
        "--append", action="store_true", help="Append data to existing data"
    )
    args = parser.parse_args()

    # Check for conflicting options
    if args.clear and args.append:
        logger.error("Cannot use both --clear and --append options together")
        exit(1)

    # Get credentials from environment
    credentials_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")

    if not credentials_path or not os.path.isfile(credentials_path):
        logger.error("GOOGLE_APPLICATION_CREDENTIALS not set or file does not exist.")
        exit(1)

    # Load data from file
    data = load_data_from_file(args.input)
    if data is None:
        logger.error("Failed to load data from input file")
        exit(1)

    logger.info(f"Loaded {len(data)} rows from {args.input}")

    # Upload to Google Sheets
    result = upload_to_google_sheets(
        data,
        args.spreadsheet_id,
        args.sheet_name,
        credentials_path,
        args.clear,
        args.append,
    )

    if result["status"] == "success":
        logger.info(f"Upload successful. Updated {result.get('updatedCells')} cells.")
    else:
        logger.error(f"Upload failed: {result.get('message')}")
        exit(1)


if __name__ == "__main__":
    main()
