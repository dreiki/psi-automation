from pprint import pprint
from datetime import datetime
import requests
import csv
import logging

MODULE_LOGGER = logging.getLogger()

'''
def internet_direct_parse(url):
    parsed_data=[]
    # csv_data = requests.get(f'https://docs.google.com/spreadsheets/d/{id}/gviz/tq?tqx=out:csv&sheet={sheet}')
    # with io.StringIO(csv_data.content.decode("utf-8-sig")) as file:
    #     for i in csv.DictReader(file,delimiter=";"):
    #         parsed_data.append(i)
    # return parsed_data
'''

def download(url,name):
    file_path = f"{name}-{datetime.datetime.now().strftime('%d-%m-%Y')}-internet.csv"
    with requests.Session() as session:
        download = session.get(url)

        print(f"Downloading csv file from: {url}")
        with open(file_path, "wb") as file:
            print(f"Saving csv file: {file_path}")
            file.write(download.content)
        print(f"Downloading csv file completed.")
    return file_path

def generate(data,header,file_path):
    MODULE_LOGGER.debug("Generate csv method called")
    with open(file_path,"w",newline="",encoding="utf-8-sig") as file:
        writer = csv.DictWriter(file,header,quoting=csv.QUOTE_ALL,delimiter=";")
        writer.writeheader()
        MODULE_LOGGER.info(f"Generate csv to : {file_path}")
        for index,row in enumerate(data):
            MODULE_LOGGER.info(f"Writing data {index+1}/{len(data)} as row")
            writer.writerow(row)
    MODULE_LOGGER.info("Generate csv completed")

def parse(file_path,separator=";"):
    MODULE_LOGGER.debug("Parse csv method called")
    MODULE_LOGGER.info(f"Parsing csv file : {file_path}")
    with open(f'{file_path}',encoding="utf-8-sig") as file:
        parsed_data=[]
        for index,idividual_data in enumerate(csv.DictReader(file,delimiter=separator)):
            MODULE_LOGGER.info(f"Reading row {index+1}")
            parsed_data.append(idividual_data)
    MODULE_LOGGER.info(f"Parse done")
    return parsed_data
