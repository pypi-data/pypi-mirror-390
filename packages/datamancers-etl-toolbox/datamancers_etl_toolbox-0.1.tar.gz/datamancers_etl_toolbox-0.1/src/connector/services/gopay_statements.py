#!/usr/bin/env python3
import os.path
import base64
import json
import gopay
from typing import List
import logging
import datetime

# Configure the logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class GoPayClient:
    def __init__(self, client_id: str, client_secret: str, goid: int):
        """
        Initializes the GoPayClient with the given credentials.
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.goid = goid
        self.api = self.login()

    def login(self):
        """
        Obtains an access token for the GoPay API using the provided credentials.
        """
        
        api = gopay.payments({
            "goid": self.goid,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "gateway_url": "https://gate.gopay.cz/api/"
        })
        
        response=api.get_payment_instruments(self.goid, gopay.enums.Currency.CZECH_CROWNS)
        if not response.success:
            error_message = "Failed login: %s %s" % (response.json["errors"][0]["message"], response.json["errors"][0]["description"])
            logger.error(error_message)
            raise Exception(error_message)
    
        return api    
    
    def get_account_statement(self, date_from: str, date_to: str, currency: str = 'CZK', format: str = 'csv') -> List[dict]:
        
        # We assume that the goid variable contains your GoID
        from gopay.enums import Currency, StatementGeneratingFormat

        # Dictionary with the request body
        request_body = {
            "date_from": date_from,
            "date_to": date_to,
            "currency": Currency.CZECH_CROWNS,
            "format": StatementGeneratingFormat.CSV_A,
            "goid": self.goid,  # Use self.goid to access the instance variable
        }

        # API call for getting the account statement
        response = self.api.get_account_statement(request_body)

        # Check whether the API call was successful and decode the content
        if response.success:
            statement = response.raw_body.decode("windows-1250")
            import json
            import pandas as pd

            with open('statement.csv', 'w') as f:
                f.write(statement)
            # Convert CSV to JSON
            pd_data=pd.read_csv('statement.csv',sep=';').fillna("")
            pd_data.columns=[i.replace("/","_")for i in pd_data.columns]
            json_data=pd_data.to_dict(orient='records')
            
            # Convert the list of dictionaries to a JSON string
            logger.info("Account statement retrieved successfully.")
        else:
            logger.error("Failed to retrieve account statement: %s", response.error_message)

        return json_data 

# Example usage:
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='GoPay client to fetch account statement.')
    
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    parser.add_argument('client_id', type=str, help='Client ID')
    parser.add_argument('client_secret', type=str, help='Client secret')
    parser.add_argument('--goid', type=str, help='GoID')
    parser.add_argument('--date_from', type=str, help='Date from', default=today)
    parser.add_argument('--date_to', type=str, help='Date to', default=today)
    parser.add_argument('--path', type=str, help='Path to save the output JSON file', default='statement.json')
    args = parser.parse_args()

    client_id = args.client_id
    client_secret = args.client_secret
    goid = args.goid
    date_from = args.date_from
    date_to = args.date_to
    output_path = args.path

    
    client = GoPayClient(client_id, client_secret, goid)
    statement = client.get_account_statement(date_from, date_to)
    with open(output_path, 'w') as json_file:
        data="\n".join([json.dumps(i) for i in statement])
        json_file.write(data)
