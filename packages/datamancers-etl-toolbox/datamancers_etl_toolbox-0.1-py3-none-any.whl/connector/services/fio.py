import logging
import pandas as pd
import fiobank
from flask import escape
import time
import datetime as dt
from datetime import datetime as dtd
import flask



def fio_extractor(config,keys):
    # first security layer - verify request against hardcoded security token to prevent outside triggering of cloud function
 #   request_json = request.get_json(force=True)  # https://stackoverflow.com/questions/53216177/http-triggering-cloud-function-with-cloud-scheduler/60615210#60615210
 #   if escape(request_json['token']) != 'qomaAI5SBnHTgfxAmssduv6MlV0YH7Xk':
 #       logging.info('Ignoring request without valid token')
 #       return

    # main code to extract data
    first_run = True  # important to disable header after the first download when downloading multiple accounts
    extracted_columns = config["extracted_columns"]
    incremental = config["incremental_LBW"]
    transactions = list()
    max_attempts = config["max_attempts"]
    # df = pd.DataFrame(columns = ["a"]) # inicialization of df necessary to proceed
    if incremental:
        lookback_window = dt.timedelta(config["lookback_window"])
        start_date = (dtd.now() - lookback_window).strftime("%Y-%m-%d")
        end_date = dtd.now().strftime("%Y-%m-%d")
    else:
        start_date = config["start_date"]
        end_date = config["end_date"]
    logging.info("Processing period from " + str(start_date) + " to " + end_date + ".")

    for access_token in keys["keys"]:
        client = fiobank.FioBank(token=access_token)
        account_number = client.info()['account_number']
        attempts = 1
        done = False

        while done is False and attempts <= max_attempts:
            try:
                logging.info("Processing data for account number " + account_number + ".")
                transactions = client.period(start_date, end_date)
                done = True
            except fiobank.ThrottlingError:
                logging.info("Token unavailable. Retrying in 5s.")
                time.sleep(5)  # constant backoff 5 seconds
                attempts = attempts + 1
                # or increase counter somehow to create backoff
            except:
                logging.info("Error occured: ", sys.exc_info()[0])
                done = True

        data = pd.DataFrame(list(transactions))
        try:
            data_select = data.loc[:, extracted_columns]
            data_select['account_number'] = account_number
            if first_run:
                df = data_select
            else:
                df = df.append(data_select)
            # data_select.to_csv("data_select.csv", index=False, header=first_run ,encoding='ANSI', mode='a')
            first_run = False
        except KeyError:
            logging.info("No data available for the date range from " +
                         start_date +
                         " to " +
                         end_date +
                         " under token " +
                         str((keys["keys"].index(access_token) + 1)) + ".")

    logging.info("Extraction done.")

    # add extraction date to received data
    extraction_date = dtd.now()
    df['extractionDate'] = extraction_date.strftime("%Y-%m-%d %H:%M:%S")
    logging.info("Extraction date added.")
    return df