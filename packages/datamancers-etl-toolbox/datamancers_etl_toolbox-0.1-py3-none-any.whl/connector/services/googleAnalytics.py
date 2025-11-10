import os
import sys
import pandas as pd
import numpy as np
import datetime as dt
import json
from datetime import datetime as dtd
import time


class instance():

    def __init__(self,viewId,credentials):
        from apiclient.discovery import build
        from oauth2client.service_account import ServiceAccountCredentials
        self.credentials = ServiceAccountCredentials.from_json_keyfile_dict(
            credentials, ['https://www.googleapis.com/auth/analytics.readonly'])
        self.instance = build('analyticsreporting', 'v4', credentials=self.credentials)
        self.viewId = viewId


    def fetch_data(self,date_start,date_end,dimensions,metrics,pageSize=5000,dailyWalk=False):
        """Function for fetching GA data.
        -----------------------------
        INPUT PARAMETERS:

        *date_start(str)* - start date in format 'YYYY-MM-DD',
        *date_end(str)* - end date  in format 'YYYY-MM-DD',

        *dimensions(list of str)* - list of dimensions without 'ga:' prefix,
        *metrics(list of str)* - list of metrics without 'ga:' prefix,
        NOTE: all dimension and metrics and its possible combinations can be found on this link:  https://ga-dev-tools.appspot.com/dimensions-metrics-explorer/

        *pageSize(int,default=5000)* - number of rows per report page. Should not impact output of function,
                                        can be used in case of function performance optimization

        *dailyWalk(bool,default=False)* - can be used to override data sampling. If True, function will split request
        by days, which will slow down speed but solve problem with sampling
        -----------------------------
        OUTPUT TYPE: Pandas dataframe
        """

        response_df = pd.DataFrame(columns=dimensions+metrics)
        dimensions_formatted = [{"name": "ga:{}".format(i)} for i in dimensions]
        metrics_formatted = [{"expression": "ga:{}".format(i)} for i in metrics]
        nextPageToken="0"

        date_last = date_end
        date_end = date_start if dailyWalk == True else date_end
        ### LOOP SEQUENCE - RUN UNTIL IT WON'T REACH LAST PAGE IN RESPONSE (PAGINATION)
        while nextPageToken != "end" and date_end <= date_last:
            print("date range:" + date_start + " <=> " + date_end + " rows: "+ nextPageToken + " - " + str(int(nextPageToken)+pageSize))

            ### API REQUEST BUILD
            response = self.instance.reports().batchGet(
              body={
                "reportRequests": [
                {
                  "viewId": self.viewId,
                  "dateRanges": [
                    {
                      "startDate": date_start,
                      "endDate":   date_end
                    }],
                  "metrics": metrics_formatted,
                  "dimensions": dimensions_formatted,
                "pageToken": nextPageToken,
                "pageSize": pageSize,
                      }]
              }
            ).execute()["reports"][0]

            response_data = response["data"]
            ### CHECK THE NUMBER OF ROWS IN RESPONSE, IF EMPTY, RETURN MESSAGE
            if "rowCount" in response_data:
                response_values = [i["dimensions"] + i["metrics"][0]["values"] for i in response_data["rows"]]
                response_df = response_df.append(pd.DataFrame(response_values, columns=response_df.columns))
                nextPageToken = response["nextPageToken"] if "nextPageToken" in response else "end"

                if dailyWalk == True:
                    nextPageToken = "0" if nextPageToken == "end" else nextPageToken
                    date_start = date_end = str(dtd.strptime(date_start,"%Y-%m-%d") + dt.timedelta(days=1))[:10]

                time.sleep(2)
            else:
                print("no record found for this date!")
                if dailyWalk == True:
                    nextPageToken = "0" if nextPageToken == "end" else nextPageToken
                    date_start = date_end = str(dtd.strptime(date_start,"%Y-%m-%d") + dt.timedelta(days=1))[:10]
        return response_df




