import json
from google.cloud import bigquery

with open('mergado_data.json') as file:
    data = [json.loads(line) for line in file]


client = bigquery.Client(project="datamancers")
schema_json = '''

    [
    {"name": "item_id", "type": "STRING", "mode": "REQUIRED"},
    {"name": "productname", "type": "STRING", "mode": "REQUIRED"},
    {"name": "description", "type": "STRING", "mode": "NULLABLE"},
    {"name": "url", "type": "STRING", "mode": "NULLABLE"},
    {"name": "delivery_date", "type": "STRING", "mode": "NULLABLE"},
    {"name": "param", "type": "RECORD", "mode": "REPEATED", "fields": [
        {"name": "PARAM_NAME", "type": "STRING", "mode": "REQUIRED"},
        {"name": "VAL", "type": "STRING", "mode": "REQUIRED"}
    ]},
    {"name": "imgurl", "type": "STRING", "mode": "NULLABLE"},
    {"name": "price_vat", "type": "STRING", "mode": "NULLABLE"},
    {"name": "manufacturer", "type": "STRING", "mode": "NULLABLE"},
    {"name": "extra_message", "type": "STRING", "mode": "NULLABLE"},
    {"name": "itemgroup_id", "type": "STRING", "mode": "NULLABLE"},
    {"name": "ean", "type": "STRING", "mode": "NULLABLE"},
    {"name": "categorytext", "type": "STRING", "mode": "NULLABLE"},
    {"name": "promotion_id", "type": "STRING", "mode": "NULLABLE"},
    {"name": "imgurl_alternative", "type": "STRING", "mode": "REPEATED"},
    {"name": "first_cat", "type": "STRING", "mode": "NULLABLE"},
    {"name": "skladovost", "type": "STRING", "mode": "NULLABLE"},
    {"name": "vyprodej", "type": "STRING", "mode": "NULLABLE"},
    {"name": "extract_timestamp", "type": "TIMESTAMP", "mode": "NULLABLE"}

]
'''

schema = [bigquery.SchemaField.from_api_repr(field) for field in json.loads(schema_json)]
table_id = 'ksporting.dbt__sourcing.MERGADO__heureka_feed'
client = bigquery.Client(project="ksporting")
config= bigquery.LoadJobConfig(autodetect=False)

table = bigquery.Table(table_ref = table_id, schema=schema)
try:
    client.create_table(table, exists_ok=False)
except Exception as e:
    client.delete_table(table_id, not_found_ok=True)
    client.create_table(table, exists_ok=True)
status=client.load_table_from_json(data, table_id, project="ksporting", job_config=config) # LoadJobConfig() is optional
print(status)
