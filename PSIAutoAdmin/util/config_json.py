from datetime import datetime
import json
import logging

MODULE_LOGGER = logging.getLogger()

def read(path):
    MODULE_LOGGER.debug("Json reader method is called")
    with open(path) as f:
        MODULE_LOGGER.info(f"Reading json : {path}")
        data = json.load(f)
    return data

def update(script,path='config.json',data=None):
    MODULE_LOGGER.debug("Update config.json method is called")
    MODULE_LOGGER.info(f"Updating config from {script} script")
    MODULE_LOGGER.info(f"Updating config json called : {path}")
    initial_data = read(path)

    if script == "bipo_fill" and data is not None:
        initial_data["ssportal_claim"]["last_claimed"] = data

    initial_data[script]["last_run"] = datetime.now().strftime('%d %b %Y %H:%M')
    
    with open(path, 'w') as f:
        json.dump(initial_data, f, indent=4)
        MODULE_LOGGER.info(f"Write to {path} has done")
