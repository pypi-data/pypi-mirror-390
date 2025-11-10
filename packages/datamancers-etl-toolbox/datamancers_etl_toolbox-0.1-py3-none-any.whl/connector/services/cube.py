import requests as r
import logging
import argparse
import time

logging.basicConfig(level=logging.INFO)

import json
from urllib3.exceptions import ReadTimeoutError
from requests.exceptions import ReadTimeout

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog='cube handler',
        description='Cube handler for'
    )

    parser.add_argument("HOSTNAME")
    parser.add_argument("API_KEY")
    parser.add_argument("--command", '-c', default='refresh')
    parser.add_argument("--query", '-q', type=json.loads)
    arguments = parser.parse_args()
    method = "GET"
    data = {}

    if arguments.command == "refresh":
        endpoint = "run-scheduled-refresh"
    elif arguments.command == "preaggregations":
        endpoint = "pre-aggregations/jobs"
        method = "POST"
        data = {"json": {"action": "post", "selector": {"timezones": ["UTC"], "contexts": [{"securityContext": {}}]}}}
    elif arguments.command == "load":
        endpoint = arguments.command
        method = "POST"
        data = {"json": {"query": arguments.query}}
    else:
        endpoint = arguments.command

    api_url = f"https://{arguments.HOSTNAME}/cubejs-api/v1/"
    status_ok = False
    request_url = f"{api_url}{endpoint}"
    headers = {"Authorization": arguments.API_KEY, "Content-Type": "application/json"}
    args = {"method": method, "url": request_url, "headers": headers, "timeout":30} | data
    logging.warning(f"url:{request_url} | method:{method} | data: {data}")
    while not status_ok:
        try:
            res = r.request(**args)
            res_json = res.json()
            if arguments.command == "preaggregations":
                if args["json"]["action"] == "post":
                    logging.warning('set refresh jobs')
                    args["json"] = {"action": "get", "tokens": res_json}
                elif args["json"]["action"] == "get":
                    if res_json == {"error":"Continue wait"}:
                        time.sleep(10)
                        continue
                    statuses = [i["status"] for i in res_json]
                    statuses_count = dict((x, statuses.count(x)) for x in set(statuses))
                    logging.warning(f'Status of refresh jobs: {statuses_count}')
                    statuses = list(statuses_count.keys())
                    if statuses == ["done"]:
                        status_ok = True
                    elif "error" in statuses:
                        raise RuntimeError(
                            f'Error in following refresh jobs: {[i["table"] for i in res_json if i["status"] == "error"]}')
                    else:
                        time.sleep(10)
            elif arguments.command == "load" and res.status_code == 200 and res_json.get("data", False):
                status_ok = True
            else:
                status_ok = res.json().get("finished", False)
                time.sleep(10)
            logging.info(f"response status:{res.status_code} | text:{res.text}")
        except TypeError:
            raise Exception(f'Error: Status {res.status_code} : {res.text}')
        except (TimeoutError,ReadTimeoutError,ReadTimeout) as e:
            counter = + 1
            if counter == 100:
                raise Exception(f'Error too many retries aborting')
            else:
                logging.info(f"Timeout error, retrying {counter}")
                time.sleep(10)
        except KeyError:
            raise Exception(f'Error: Status {res.status_code} : {res.text}')
