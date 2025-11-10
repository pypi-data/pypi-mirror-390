import requests
import json
import xmltodict
import argparse
from datetime import datetime
from pytz import timezone
import pandas as pd
import csv

extract_timestamp = datetime.now(timezone("Europe/Prague")).strftime(
    "%Y-%m-%dT%H:%M:%S"
)


def extract_feed(
    feed_url=None, nested=None, file_path=None, encoding="utf-8", output_type="JSON"
) -> list:
    if feed_url:
        response = requests.get(feed_url)
        response.encoding = response.apparent_encoding
        data_string = response.text
    elif file_path:
        with open(file_path, "r", encoding=encoding) as f:
            data_string = f.read()

    if output_type == "JSON":
        data = json.loads(json.dumps(xmltodict.parse(data_string)))
        if nested:
            nested = nested.split(".")
        for i in nested:
            data = data[i]
    elif output_type == "XML":
        data = data_string

    return data


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="xml_feed_extract", description="This helps extract heureka data"
    )
    parser.add_argument("--url", required=True)
    parser.add_argument("--nested", required=False, default=False)
    parser.add_argument("--output_type", required=True)
    arguments = parser.parse_args()
    data = extract_feed(
        arguments.url, arguments.nested, output_type=arguments.output_type
    )

    def replace_signs_in_keys(data, sign):
        """
        Recursively replace '@' with '_' in all dictionary keys.
        Works with nested dictionaries and lists of dictionaries.

        Args:
            data: The data structure to process (dict, list, or other value)

        Returns:
            The processed data structure with '@' replaced by '_' in all keys
        """
        if isinstance(data, dict):
            return {
                (
                    k.replace(sign, "_") if isinstance(k, str) else k
                ): replace_signs_in_keys(v, sign)
                for k, v in data.items()
            }
        elif isinstance(data, list):
            return [replace_signs_in_keys(item, sign) for item in data]
        else:
            return data

    if arguments.output_type == "JSON":
        data = replace_signs_in_keys(data, "@")
        data = [dict(item, **{"extract_timestamp": extract_timestamp}) for item in data]
        data = [json.dumps(item) for item in data]
        data = "\n".join(data)
        with open("feed", "w") as f:
            f.write(data)
    elif arguments.output_type == "CSV":
        pd.DataFrame(data).to_csv("feed", index=False, sep="\t")
    elif arguments.output_type == "XML":
        with open("feed", "w") as f:
            f.write(data)
