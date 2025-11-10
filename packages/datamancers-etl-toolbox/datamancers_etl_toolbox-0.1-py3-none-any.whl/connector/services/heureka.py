import requests
import os
import argparse
import logging
import xmltodict
import json
import pandas as pd
from datetime import datetime
from pytz import timezone
import unicodedata
import re
import retrying
# import kestra
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_input_keys(input_keys_list, arguments):
    if [k for k, v in arguments.__dict__.items() if v] == input_keys_list:
        logging.info(f"starting extraction of {arguments.url}")
    else:
        raise ValueError(f"Invalid parameter input, should be json with following keys:{input_keys_list}")

def to_snake_case(input_str):
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    only_ascii = nfkd_form.encode('ASCII', 'ignore')
    output= re.sub('_+','_',only_ascii

             .decode("utf-8")
             .lower()
             .replace(" ", "_")
             .replace("-", "_")
             .replace(":","_")
             )
    return output
def get_costReport(costReport_URL):
    from io import StringIO
    import pandas as pd

    costReport_request = requests.get(costReport_URL)
    costReport_string = StringIO(str(costReport_request.content, "utf-8"))
    costReport_df = pd.read_csv(costReport_string)
    return costReport_df


def get_ProductURLs(conversionReport_URL):
    import gzip
    import xml.etree.ElementTree as et
    report = requests.get(conversionReport_URL)

    xml_string = gzip.decompress(report.content)

    xtree = et.fromstring(xml_string)
    product_tpls = []
    for product in xtree.iter("PRODUCT"):
        url_split = product.find("HEUREKA_URL").text.split("/")
        url_product = url_split[3]
        url_category = url_split[2].split(".")[0]
        product_tpls.append(tuple([url_category, url_product]))

    return product_tpls


class bidding_api(object):
    def __init__(self, token):
        self.token = token

    from retrying import retry

    @retry(stop_max_attempt_number=10)
    def get_product(self, product_id, format=True, **kwargs):

        import json
        ## generate basic form of request
        url = "https://api.heureka.cz/bidding_api/v1"
        payload = {
            "jsonrpc": "2.0",
            "method": "product.get",
            "id": 1,
            "params": {
                "access_key": self.token,
                "id": product_id
            }
        }

        ## if category parameter is defined, add it to request
        if "category" in kwargs:
            payload["params"]["category_id"] = kwargs["category"]

        ## data are present in nested product dictionary
        response = requests.post(url=url, json=payload)
        product = response.json()["result"]["product"]
        ## preprocess data, add new features and unify data format
        if format:

            ## format and shop keys to unified verssion
            logging.info(str(product))
            if product["top_shop"]:
                product["top_shop"]["offers"] = [product["top_shop"].pop("offer")]
            product["top"] = [product.pop("top_shop")]
            product["organic"] = product.pop("shops")
            product["highlighted"] = product.pop("highlighted_shops")

            ## merge all shop dictionaries into one and delete redundant keys
            merged_keys = ["top", "highlighted", "organic"]
            product["shops"] = []
            for key in merged_keys:
                if product[key]:
                    ## add feature of shop position type
                    product[key] = [dict(item, position=key) for item in product[key]]
                product["shops"].extend(product.pop(key))
            ## add offer position rank (ranked from top-sponsored-organic)
            product["shops"] = [dict(item, rank=ind + 1) for ind, item in enumerate(product["shops"])]
            ## add variant position rank (ranked by order in list)
            for index, shop in enumerate(product["shops"]):
                shop_offers_list = product["shops"][index]["offers"]
                product["shops"][index]["offers"] = [dict(offers, rank=ind + 1) for ind, offers in
                                                     enumerate(shop_offers_list)]

        return product


class Extraction:
    @staticmethod
    def heureka_cost_report(costReport_URL):
        cost_report = get_costReport(costReport_URL=costReport_URL)
        return cost_report

    @staticmethod
    def heureka_product_urls(conversionReport_URL):
        productsURL_list = get_ProductURLs(conversionReport_URL=conversionReport_URL)
        ## remove duplicats
        list(set(productsURL_list))
        return productsURL_list

    @staticmethod
    def feed(feed_url, nested_path):
        response = requests.get(feed_url)
        response.encoding = response.apparent_encoding
        nested_path = nested_path.split(".")

        data = json.loads(json.dumps(xmltodict.parse(response.text)))
        if nested_path:
            for i in nested_path:
                data = data[i]
        data = [{to_snake_case(k): v for k, v in i.items()} for i in data]
        return data

    @staticmethod
    def heureka_products(productsURL_list, token, CLIENT__heureka_project_name):
        mapping_pd = pd.DataFrame(columns=["product_id_heureka", "product_id_shop"])

        instance = bidding_api(token=token)

        product_list = []
        for iter, i in enumerate(productsURL_list):
            if iter % 100 == 0:
                logger.info("number of products processed:" + str(iter))
            try:
                product_json = instance.get_product(product_id=i[1], category=i[0])
            except (TypeError, KeyError) as e:
                logger.error("error for product: " + i[1] + " " + str(e))
                continue
            try:
                product_id_shop = \
                    [i["offers"][0]["item_id"] for i in product_json["shops"] if
                     i["slug"] in CLIENT__heureka_project_name][0]
            except:
                logger.error("error extracting shop product id : " + str(i) + " " + str(e))
            mapping_dict = {"product_id_heureka": product_json["id"], "product_id_shop": product_id_shop}
            mapping_pd = pd.concat([mapping_pd, pd.DataFrame([mapping_dict])], ignore_index=True)

            product_list.append(product_json)
        return mapping_pd, product_list


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog='heureka_extract',
        description='This helps extract heureka data'
    )
    parser.add_argument("data_type", )
    parser.add_argument("--url", required=True)
    parser.add_argument("--token")
    parser.add_argument("--projectname")
    parser.add_argument("--nested_path")
    arguments = parser.parse_args()

    extract_timestamp = datetime.now(timezone("Europe/Prague")).strftime("%Y-%m-%dT%H:%M:%S")
    outputs = {}

    if arguments.data_type == "cost_report":
        check_input_keys(input_keys_list=['data_type', 'url'], arguments=arguments)
        outputs['HEUREKA__click_costs'] = Extraction.heureka_cost_report(costReport_URL=arguments.url)
        logging.info(f"ending extraction of {arguments.url}")


    elif arguments.data_type == "products":
        check_input_keys(input_keys_list=['data_type', 'url', 'token', 'projectname'], arguments=arguments)
        heureka_product_urls = Extraction.heureka_product_urls(conversionReport_URL=arguments.url)
        logging.info(f"starting extraction of heureka products")
        outputs["HEUREKA__products_mapping"], outputs["HEUREKA__biddingApi"] = Extraction.heureka_products(
            productsURL_list=heureka_product_urls,
            token=arguments.token,
            CLIENT__heureka_project_name=arguments.projectname
        )
        logging.info(f"ending extraction of heureka products")

    elif arguments.data_type == "feed":
        check_input_keys(input_keys_list=['data_type', 'url', 'nested_path'], arguments=arguments)
        outputs["MERGADO__heureka_feed"] = Extraction.feed(feed_url=arguments.url,
                                                           nested_path=arguments.nested_path)
        logging.info(f"ending extraction of {arguments.url}")

    else:
        raise ValueError("Invalid argument, expected one of the following: cost_report, products, feed")

    for i in list(outputs.keys()):
        if not os.path.exists("data"):
            os.makedirs("data")
        object_to_save = outputs[i]
        if type(object_to_save) == pd.DataFrame:
            object_to_save["extract_timestamp"] = extract_timestamp
            if object_to_save.index.name:
                object_to_save = object_to_save.reset_index()
            object_to_save.to_csv("data/" + i + ".csv", index=False)
        elif type(object_to_save) in (dict, list):
            object_to_save = [json.dumps(dict(item, **{"extract_timestamp": extract_timestamp})) for item in
                              object_to_save]
            data = '\n'.join(object_to_save)
            with open("data/" + i + ".json", "w") as f:
                f.write(data)
        else:
            raise TypeError("unexpected object type of " + str(type(object_to_save)) + "must be one of: csv , json")