import json
import requests
from requests.adapters import HTTPAdapter
import datamonk.utils.functions as util_functions
from requests.packages.urllib3.util.retry import Retry

retry_strategy = Retry(
    total=20,
    status_forcelist=[429, 500, 502, 503, 504],
    method_whitelist=["HEAD", "GET", "OPTIONS","POST"]
)
adapter = HTTPAdapter(max_retries=retry_strategy)
https = requests.Session()
https.mount("https://", adapter)

class instance(object):

    def __init__(self,token):
        self.token = token
        self.url = "https://api2.ecomailapp.cz/"

    def create_list(self,
                    list_name,
                    from_name,
                    from_email,
                    reply_to,
                    sub_success_page=None,
                    unsub_page = None,
                    sub_confirmed_page=None,
                    double_optin=None,
                    conf_subject=None,
                    conf_message=None):

        data= {
                "name": list_name,
                "from_name": from_name,
                "from_email": from_email,
                "reply_to": reply_to,
                "sub_success_page": sub_success_page,
                "sub_confirmed_page": sub_confirmed_page,
                "unsub_page": unsub_page,
                "double_optin": double_optin,
                "conf_subject": conf_subject,
                "conf_message": conf_message
              }
        data_str=json.dumps(data)
        response=https.post(self.url + "lists",
                               headers={"key":self.token,
                                        'Content-Type': 'application/json'},
                               data=data_str)
        if response.status_code == 200:
            list_id=json.loads(response.content)["id"]
            print("subscriber list " + list_name + " created under id" + str(list_id))
        return response

    def get_lists(self):

        response=https.get(self.url + "lists",headers={"key":self.token})
        response_json=json.loads(response.content.decode("unicode-escape"))
        return response_json

    class list():
        def __init__(self, list_id, instance):
            self.instance = instance
            self.url = instance.url + "lists/" + str(list_id) + "/"

        def _get_call(self,endpoint,params):
            response = https.get(self.url+endpoint, headers={"key": self.instance.token},params=params,timeout=None)
            response_json = json.loads(response.content)
            if response.status_code != 200:
                raise ConnectionError("GET call ended up in error. Status code:"+ str(response.status_code) + "\n Error Message: " + response.reason)
            return response_json


        def _post_call(self,endpoint,data):
            response = https.post(self.url+endpoint,
                                 data=data,
                                 headers={"key": self.instance.token},
                                 timeout = None
                                  )
            if response.status_code != 200:
                raise ConnectionError("POST call ended up in error. Status code:"+ str(response.status_code) + "\n Error Message: " + response.reason)
            return response

        @util_functions.timeit
        def post_subscribers(self,data,chunk_size=3000):
            import math

            subscribers_count=len(data)
            bulk_chunks=math.ceil(subscribers_count/chunk_size)
            print("""data gathered, will be uploaded in bulk chunks by """+str(chunk_size) +""""  contacts per piece.
                 Total number of chunks:""" + str(bulk_chunks))

            current_chunk_nr = 1
            while current_chunk_nr <= bulk_chunks:
                current_chunk_lower = (current_chunk_nr-1) * chunk_size
                current_chunk_upper = min([current_chunk_nr * chunk_size ,subscribers_count])

                current_chunk_data = data[current_chunk_lower:current_chunk_upper]
                post_data=json.dumps({"subscriber_data":current_chunk_data,"update_existing":True})
                response=self._post_call(endpoint="subscribe-bulk",data=post_data)
                current_chunk_nr+=1
            return print("data upload successful")

        @util_functions.timeit
        def get_subscribers(self,**kwargs):
            params = {}
            if "per_page" in kwargs:
                params.update({"per_page":kwargs["per_page"]})
            response_json=self._get_call("subscribers",params=params)
            data=[contact["subscriber"] for contact in response_json["data"]]


            last_page_nr = response_json["last_page"]
            current_page_nr = response_json["current_page"]
            while current_page_nr != last_page_nr:
                params.update({"page":current_page_nr})
                current_page_nr = current_page_nr + 1
                response_json=self._get_call("subscribers",params=params)
                data.extend(response_json["data"])

            return data

