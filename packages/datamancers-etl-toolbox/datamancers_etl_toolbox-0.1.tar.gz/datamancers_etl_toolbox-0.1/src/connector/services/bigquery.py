#!/usr/bin/env python3
import os
import json
import logging
import argparse
import pandas as pd
from google.cloud import bigquery
from google.oauth2 import service_account
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def fetch_bigquery_data(query: str, credentials_path: str, output_type: str = "json", project_id: str = None):
    """
    Fetch data from BigQuery using a SQL query and return it in the specified format.
    
    Args:
        query: SQL query to execute
        credentials_path: Path to the Google service account credentials file
        output_type: Format to return the data in ("json", "csv", or "pandas")
        project_id: Optional GCP project ID
    Returns:
        Data in the specified format (list of dicts, CSV string, or pandas DataFrame)
    """
    credentials = service_account.Credentials.from_service_account_file(credentials_path)
    client = bigquery.Client(credentials=credentials, project=project_id)
    logger.info(f"Running query: {query}")
    query_job = client.query(query)
    df = query_job.result().to_dataframe()
    if output_type == "json":
        return df.to_dict(orient="records")
    elif output_type == "csv":
        return df.to_csv(index=False)
    elif output_type == "pandas":
        return df
    else:
        raise ValueError(f"Invalid output type: {output_type}")

def main():
    parser = argparse.ArgumentParser(description='BigQuery Extractor')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--query', type=str, help='SQL query to execute')
    group.add_argument('--table', type=str, help='Table to extract, e.g. dataset.table')
    parser.add_argument('--output', type=str, default='bigquery_data.json', help='Output file name')
    parser.add_argument('--format', type=str, choices=['json', 'csv'], default='json', 
                        help='Output format (json or csv)')
    parser.add_argument('--project_id', type=str, default=None, help='GCP project ID (optional)')
    args = parser.parse_args()

    credentials_path = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
    if not credentials_path or not os.path.isfile(credentials_path):
        logger.error("GOOGLE_APPLICATION_CREDENTIALS not set or file does not exist.")
        exit(1)

    # Determine query
    if args.table:
        query = f"SELECT * FROM `{args.table}`"
    else:
        query = args.query

    try:
        results = fetch_bigquery_data(
            query,
            credentials_path,
            args.format,
            args.project_id
        )
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