import requests
import urllib3
import gzip
from io import BytesIO
import xmltodict
import time
from datetime import datetime
from requests.adapters import HTTPAdapter, Retry
import logging
logger=logging.getLogger(__name__)
logger.setLevel(logging.INFO)


s = requests.Session()
retries = Retry(total=5,
                backoff_factor=1,
                status_forcelist=[400, 502, 503, 504])
s.mount('https://', HTTPAdapter(max_retries=retries))


class Sreality:
    def __init__(self, filter_config=dict()):

        sitemap_index_response = s.get('https://www.sreality.cz/sitemap.xml')
        sitemap_index_list = xmltodict.parse(sitemap_index_response.text)["sitemapindex"]["sitemap"]
        sitemap_urls = [i["loc"] for i in sitemap_index_list]
        self.offer_urls = []
        for sitemap_url in sitemap_urls:
            sitemap_requests = s.get(sitemap_url, stream=True)
            sitemap = gzip.GzipFile(fileobj=BytesIO(sitemap_requests.content)).read()
            self.offer_urls.extend([url["loc"] for url in xmltodict.parse(sitemap)["urlset"]["url"]])
        self.offer_filter_conditions = filter_config
        if filter_config:
            self.extract_offer_urls = self.filter_urls_by_parameters(
                offer_type=self.offer_filter_conditions["offer_types"],
                disposition=self.offer_filter_conditions["dispositions"],
                estate=self.offer_filter_conditions["estate"],
                city=self.offer_filter_conditions["locations"])
        else:
            self.extract_offer_urls = self.offer_urls
        self.extract_offer_ids = [self.parse_detail_url(url)["id"] for url in self.extract_offer_urls]
        self.extract_offer_count = len(self.extract_offer_ids)
        logger.info(msg="sreality instance initialized, offers to extract: {}".format(str(self.extract_offer_count)))

    @staticmethod
    def parse_detail_url(url):
        path = urllib3.util.parse_url(url).path
        try:
            path_split = str.split(path, '/')
            path_parsed = {"offer_type": path_split[2],
                           "estate": path_split[3],
                           "disposition": path_split[4],
                           "city": str.split(path_split[5], '-')[0],
                           "id": path_split[-1]}
            return path_parsed
        except:
            return {}


    def filter_urls_by_parameters(self,
                                  offer_type=None,
                                  disposition=None,
                                  estate=None,
                                  city=None,
                                  **kwargs):
        if "url_list" not in kwargs:
            kwargs["url_list"] = self.offer_urls

        output = list(
            filter(
                lambda x: self.parse_detail_url(x).get("estate", '') in estate and
                          self.parse_detail_url(x).get("disposition", '') in disposition and
                          self.parse_detail_url(x).get("city", '') in city and
                          self.parse_detail_url(x).get("offer_type", '') in offer_type, kwargs["url_list"]
                                                       )
            )
        return output

    def extract_offer_data(self, offer_url):
        try:
            page_url_params = self.parse_detail_url(offer_url)
            timestamp_extraction = round(time.time())
            url_extraction = "https://www.sreality.cz/api/cs/v2/estates/{}?tms={}".format(page_url_params["id"],
                                                                                          timestamp_extraction)

            response = s.get(url_extraction,headers= {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36"})
            response = response.json() | page_url_params
            response["timestamp"] = datetime.utcfromtimestamp(timestamp_extraction).strftime('%Y-%m-%dT%H:%M:%S')

            return response
        except Exception as e:
            return print(offer_url + str(e))

    @staticmethod
    def transform_offer_data(offer_dict):

        items_parsed = []
        pois_parsed = []

        for item in offer_dict.get("items", []):
            try:

                if item["type"] in ['price_czk', 'price_czk_old']:
                    item_parsed = {
                        "value": {"int":
                                      int(str.replace(item.get("value",''), '\u00A0', '')) if type(item["value"]) == str
                                      else item["value"],
                                  "string": item["currency"] + ' ' + item.get("unit", '')
                                  }}
                elif item["type"] in ['integer', 'count']:
                    item_parsed = {
                        "value": {"int": int(item["value"])
                                  }}
                elif item["type"] == 'area':
                    item_parsed = {
                        "value": {"int": int(item["value"]), "string": item["unit"]
                                  }}
                elif item["type"] == 'boolean':
                    item_parsed = {
                        "value": {"bool": item["value"]
                                  }}
                elif item["type"] == 'set':
                    item_parsed = {
                        "value": {"array": [i["value"] for i in item["value"]]
                                  }}
                else:
                    item_parsed = {
                        "value": {"string": item["value"]
                                  }}

                item_parsed["key"] = item["name"]
                item_parsed["type"] = item["type"]

                items_parsed.append(item_parsed)
            except Exception as e:
                logger.error("ITEM: error for id: {id}, content {item}, error {error}"
                                     .format(id=offer_dict.get("id"),
                                             item=item,
                                             error = str(e))
                                     )

        for poi in offer_dict.get("poi", []):
            try:
                poi_parsed = \
                    {"description": poi.get("description").replace("'", "`").replace('"', "`")
                    if type(poi["description"]) == str else None,
                     "name": poi.get("name").replace("'", "`").replace('"', "`") if type(poi.get("name")) == str else None,
                     "distance": poi.get("distance"),
                     "review_count": poi.get("review_count"),
                     "rating": poi.get("rating"),
                     }
                pois_parsed.append(poi_parsed)
            except Exception as e:
                logger.error("POI: error for id: {id}, content {poi}, error {error}"
                                     .format(id=offer_dict.get("poi"),
                                             poi=poi,
                                             error = str(e))
                                     )

        output = \
            {"map": {"lat": offer_dict.get("map", {}).get("lat"),
                     "lon": offer_dict.get("map", {}).get("lon")
                     },
             "estate": offer_dict.get("estate"),
             "offer_type": offer_dict.get("offer_type"),
             "id": offer_dict.get("id"),
             "disposition": offer_dict.get("disposition"),
             "seo": offer_dict.get("seo", {}).get("locality"),
             "price_czk": offer_dict.get("price_czk", {}).get("value_raw"),
             "seller_id": offer_dict.get("_embedded", {}).get("seller", {}).get("user_id"),
             "text": offer_dict.get("text", {}).get("value").replace('"', '`').replace("'", '`')
             if type(offer_dict.get("text", {}).get("value")) == str else None,
             "meta_description": offer_dict.get("meta_description"),
             "locality": {"city": offer_dict.get("city",{})} | offer_dict.get("locality",{}),
             "is_topped_today": offer_dict.get("is_topped_today"),
             "name": offer_dict.get("name", {}).get("value"),
             "items": items_parsed,
             "poi": pois_parsed,
             "extraction_timestamp": offer_dict.get("timestamp")
             }

        return output
