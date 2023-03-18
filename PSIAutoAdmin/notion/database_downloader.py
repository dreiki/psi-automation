from PSIAutoAdmin.util import csv_processor
from datetime import datetime
import requests
import json
import logging

MODULE_LOGGER = logging.getLogger()

try:
    with open('secret.json', 'r') as stream:
        data_json = json.load(stream)
    used_credential = data_json["notion"]
    MODULE_LOGGER.info("Notion credential obtained from json")
except:
    MODULE_LOGGER.error("Credential not provided via json file or cli ui")
    raise ImportError("""
    Credential is not provided and the json file is not found.
    Please provide the credential by creating json file based on the template.
    Or provide it on the CLI Prompter UI.
    """)

def page_block_get(id=None,data=""):
    MODULE_LOGGER.debug("Individual data page collector method called")
    if id is not None:
        url = f"https://api.notion.com/v1/blocks/{id}/children"

        headers = {
            "accept": "application/json",
            "Notion-Version": "2022-06-28",
            "authorization": f"Bearer {used_credential['token']}"
        }

        response = requests.get(url, headers=headers)

        for individual_block_data in response.json()['results']:
            if individual_block_data['type'] == 'bulleted_list_item':
                data += f"- {individual_block_data['bulleted_list_item']['rich_text'][0]['plain_text']}\n"

        return data

def get(path="data"):
    MODULE_LOGGER.debug("Notion data collector method is called")
    url = f"https://api.notion.com/v1/databases/{used_credential['db_id']}/query"

    payload = {
        "page_size": 100,
        "filter": {
            "property": "Submitted",
            "checkbox": {"equals": False}
        }
    }
    headers = {
        "accept": "application/json",
        "Notion-Version": "2022-06-28",
        "content-type": "application/json",
        "authorization": f"Bearer {used_credential['token']}"
    }

    response = requests.post(url, json=payload, headers=headers)

    data = response.json()['results']
    processed_data = []

    for index,individual_data in enumerate(data):
        MODULE_LOGGER.info(f"Processing Notion Data {index+1} from {len(data)}")
        tanggal = datetime.strptime(individual_data['properties']['Scheduled']['date']['start'],'%Y-%m-%d')
        description = page_block_get(individual_data['id'],f"{individual_data['properties']['Description']['title'][0]['plain_text']}\n\n")
        processed_data.append({
            'Scheduled':tanggal.strftime('%d %B %Y'),
            'Description':description,
            'Status':individual_data['properties']['Status']['select']['name'],
            'Category':individual_data['properties']['Category']['select']['name'],
            'Customer':individual_data['properties']['Customer']['rich_text'][0]['plain_text'],
            'Project':individual_data['properties']['Project']['rich_text'][0]['plain_text'],
            'City':individual_data['properties']['City']['rich_text'][0]['plain_text'],
            'Location':individual_data['properties']['Location']['select']['name'],
            'Time Start':individual_data['properties']['Time Start']['rich_text'][0]['plain_text'],
            'Time End':individual_data['properties']['Time End']['rich_text'][0]['plain_text']
        })


    csv_path = f"{path}/ssportal_absen_data-{datetime.now().strftime('%d-%m-%Y')}-notion.csv"
    csv_processor.generate(processed_data,[
        'Scheduled',
        'Description',
        'Status',
        'Category',
        'Customer',
        'Project',
        'City',
        'Location',
        'Time Start',
        'Time End',
    ],csv_path)
    MODULE_LOGGER.info(f"Notion data CSV generated in : {csv_path}")
    return csv_path

if __name__ == "__main__":
    get()