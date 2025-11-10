import time
import os
import json
from dotenv import load_dotenv
from requests_oauthlib import OAuth2Session
import logging
import webbrowser
from datamonk.scriptorium.storage.gcp import bigQuery
from typing import Union
load_dotenv()
import requests

logger=logging.getLogger("")
# bq.table("L0_google_fit_api","fit_data",bq)


class Token:
    def __init__(self, path: str):
        """
        get token from file, and check if it is still valid or create new one
        :param path: path to token file
        """
        if not os.path.exists(path):
            raise FileNotFoundError("token file not found")
        self.path = path
        self.credentials = self.load(os.environ["CREDENTIALS"])
        if os.path.exists(path) and json.load(open(path))["expires_at"] > time.time():
            self.object = self.load(path)
        else:
            self.service = OAuth2Session(self.credentials["client_id"],
                                         scope=self.credentials["scopes"],
                                         redirect_uri=self.credentials["redirect_uri"])
            if not os.path.exists(path):
                self.create(self.credentials)
                self.object = self.load(path)
            else:
                self.object = self.load(path)
                self.refresh_token()
                self.object = self.load(path)

    def save(self, token: json) -> None:
        """
        save token to file
        :param token: Token object to save
        :return: None
        """
        with open(self.path, "w") as f:
            json.dump(token, f)

        logger.info(f"token saved to destination file {self.path}")

    @staticmethod
    def load(path) -> json:
        """
        load token from file
        :param path: path to token file
        :return:
        """
        with open(path, "w") as f:
            return json.load(f)

    def refresh_token(self) -> None:
        """
        refresh oauth token if expired
        :return: None
        """
        if self.object["expires_at"] < time.time():
            logger.info("token is expired")
            new_token = self.service.refresh_token(self.credentials["token_uri"],
                                                   client_id=self.credentials["client_id"],
                                                   client_secret=self.credentials["client_secret"],
                                                   refresh_token=self.object["refresh_token"])
            self.save(new_token)
        else:
            logger.log("token is still valid")

    def create(self, credentials: json):
        """
        create new token
        :return:
        """
        authorization_url, state = self.service.authorization_url(credentials["auth_uri"],
                                                                  # offline for refresh token
                                                                  # force to always make user click authorize
                                                                  access_type="offline",
                                                                  prompt="select_account")

        webbrowser.open(authorization_url)

        redirect_response = input('Paste the full redirect URL here: ')
        self.service.fetch_token(credentials["token_uri"],
                                 client_secret=credentials["client_secret"],
                                 authorization_response=redirect_response)

        return self.save(self.service.token)

class Service:
    def __init__(self, base_url: str, token_path: str = "token.json"):
        self.base_url = base_url
        self.token = Token(token_path)
        self.service = OAuth2Session(client_id=self.token.credentials["client_id"],
                                     token=self.token.object,
                                     auto_refresh_url=self.token.credentials["token_uri"],
                                     auto_refresh_kwargs=self.token.credentials,
                                     token_updater=self.token.save)

    def get(self, url: str = "", output: str = "json") -> Union[json,str,requests.Response]:

        self.url = self.base_url + url
        if output == "json":
            return self.service.get(self.url).json()
        elif output == "text":
            return self.service.get(self.url).text
        else:
            return self.service.get(self.url)


fitData = Service(base_url='https://fitness.googleapis.com/fitness/v1/users/me/dataSources/')
data = fitData.get("")["dataSource"]
data_types = {str.replace(i["dataType"]["name"], '.', '_') for i in data}
bq = bigQuery(os.environ["GCP_PROJECT_ID"])

now = int(time.time())
data_sources = [i["dataStreamId"] for i in data]
for idx, i in enumerate(data_sources):
    print(data[idx]["dataType"]["name"])
    responses = fitData.get(f'{i}/datasets/{now-10000000}000000000-{now}000000000')['point']
    if len(responses) > 0:
        table_name =  responses[0]["dataTypeName"].replace('.', '_')
        bq_tb=bq.table("L0_google_fit",table_name , bq)
        if bq_tb.exists:
            last_val=bq.query(f"SELECT MAX(startTimeNanos) as startTimeNanos FROM L0_google_fit.{bq_tb.table_id} WHERE originDataSourceId = '{i}'").values[0][0]
            import numpy as np
            if not np.isnan(last_val):
                responses = [i for i in responses if int(i["startTimeNanos"]) > last_val]

        bq_tb.upload(responses,config_object={},create_nonexisting_table=True)

