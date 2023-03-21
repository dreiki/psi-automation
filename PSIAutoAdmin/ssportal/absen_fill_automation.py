from playwright.sync_api import sync_playwright
from PSIAutoAdmin.util import csv_processor,browser_initiator,config_json
from datetime import datetime
from pathlib import Path
import re
import json
import logging

MODULE_LOGGER = logging.getLogger()

def login_check(credential,page,page_number,browser_type):
    """
    Initial check of what browser needed to be run by playwright.
    Also check if you need to login or not.
    Auto fill the login form if needed.

    Currently not being used by this scripts.
    """

    MODULE_LOGGER.debug("Login check method called")
    if credential is None:
        try:
            with open('secret.json', 'r') as stream:
                data_json = json.load(stream)
            used_credential = data_json["ssportal"]
            MODULE_LOGGER.info("Credential succesfully obtained from json file")
        except:
            MODULE_LOGGER.error("Credential not provided via json file or cli ui")
            raise ImportError("""
            Credential is not provided and the json file is not found.
            Please provide the credential by creating json file based on the template.
            Or provide it on the CLI Prompter UI.
            """)
    else:
        MODULE_LOGGER.info("Credential succesfully obtained from cli ui")
        used_credential = credential

    if page_number is None or browser_type in ["HEADLESS","HEADED"]:
        while page.url != 'https://ssportal-tbs-2.packet-systems.com/activity/new_add_form':
            MODULE_LOGGER.info("Trying to login and navigate to site")
            MODULE_LOGGER.info(f"Currently at : {page.url}")
            page.goto('https://ssportal-tbs-2.packet-systems.com/activity/new_add_form')
            if page.url == 'https://ssportal-tbs-2.packet-systems.com/login':
                page.fill('id=username',used_credential["username"])
                page.fill('id=password',used_credential["password"])
                page.click('id=submitBtn')
            elif re.search(r"login\/error",page.url):
                MODULE_LOGGER.error("Something wrong while logging to the site. Retry the program.")
                raise EnvironmentError("""
                Either Username or Password is invalid while logging in!
                Please rerun the script.
                """)
    MODULE_LOGGER.info(f"Currently at : {page.url}")

def data_fill_processor(page,data):
    """
    The main actual data processing method after the site is navigated.
    Will fill the form multiple time based on total data passed through the argument.
    """
    MODULE_LOGGER.debug("Fill processor method is called")
    MODULE_LOGGER.info(f"Total data to be inputted is : {len(data)}")
    for index,individualdata in enumerate(data):
        MODULE_LOGGER.debug("Waiting table element")
        MODULE_LOGGER.info("Trying to navigate to add form page")
        if re.match(r"activity\/new_add_form",page.url) is None:
            page.goto("https://ssportal-tbs-2.packet-systems.com/activity/new_add_form")

        scheduled = individualdata["Scheduled"]
        try:
            datetime.strptime(scheduled,'%d %B %Y')
        except ValueError:
            scheduled = datetime.strptime(individualdata["Scheduled"],'%d/%m/%Y').strftime('%d %B %Y')

        MODULE_LOGGER.debug("Waiting table element")
        page.wait_for_load_state(state="networkidle")
        page.locator("table#table_form").wait_for()

        # PLAYWRIGHT DEBUGING CAN BE START HERE
        # page.pause()
        
        print(f"\nFilling data number {index+1} from {len(data)} data to the form\n")
        MODULE_LOGGER.info(f"Filling data number {index+1} from {len(data)} data to the form")

        if "" not in individualdata.values() and "WORK" in individualdata.get("Status"):

            activity_status_id = page.locator("select#activity_status_id option",has_text=individualdata["Status"]).get_attribute("value")
            activity_category_id = page.locator("select#activity_category_id option",has_text=individualdata["Category"]).get_attribute("value")
            location_activity = page.locator("select#location_activity option",has_text=individualdata["Location"]).get_attribute("value")
            start_time = individualdata["Time Start"].split(":")
            end_time = individualdata["Time End"].split(":")

            page.locator("select#activity_status_id").select_option(activity_status_id)
            page.locator("select#activity_category_id").select_option(activity_category_id)
            page.locator("select#location_activity").select_option(location_activity)
            page.locator("select#hour_start").select_option(f"{int(start_time[0])}")
            page.locator("select#minute_start").select_option(f"{int(start_time[1])}")
            page.locator("select#hour_end").select_option(f"{int(end_time[0])}")
            page.locator("select#minute_end").select_option(f"{int(end_time[1])}")

            page.fill("#scheduled",individualdata["Scheduled"])
            page.fill("#activity",individualdata["Description"])
            
            page.focus("input#customer")
            page.keyboard.type(individualdata["Customer"])
            page.locator(f"ul#finalResultCust li:text-matches(\"{individualdata['Customer']}\",\"i\")").click()

            page.focus("input#contract_id")
            page.keyboard.type(individualdata["Project"])
            page.locator(f"ul#finalResultContract li:text-matches(\"{individualdata['Project']}\",\"i\")").click()

            page.click("#saveButton")
            page.wait_for_load_state(state="networkidle")
            if page.locator("div#content",has=page.locator("font:text('ERROR....')")).is_hidden():
                print(f"\nSUCCESS\nData No-{index+1} / {len(data)} is succesfully submited \n**********\n")
                MODULE_LOGGER.info(f"Data No-{index+1} / {len(data)} is succesfully submited")
            else:
                print(f"\nFAILED\nFailed to submit data No-{index+1} / {len(data)}\n**********\n")
                MODULE_LOGGER.error(f"Failed to submit data No-{index+1} / {len(data)}")
        elif "LEAVE" in individualdata.get("Status"):
            MODULE_LOGGER.info(f"Data number {index+1} from {len(data)} is LEAVE data")
            activity_status_id = page.locator("select#activity_status_id option",has_text=individualdata["Status"]).get_attribute("value")
            page.locator("select#activity_status_id").select_option(activity_status_id)
            page.fill("#scheduled",individualdata["Scheduled"])
            page.fill("#activity",individualdata["Description"])
        else:
            MODULE_LOGGER.error(f"Data number {index+1} from {len(data)} is invalid")
            print(f"There is something wrong in data number {index+1} / {len(data)}")

def data_final_processor(page,operation=""):
    """
    Finishing method after all data is finished inputted.
    Will navigate back to home activity page.
    If operation empty (default) method will only navigate.
    Will try to click submit all button if Submit is passed trough operation.
    """
    MODULE_LOGGER.info("Submit method is called")
    page.goto("https://ssportal-tbs-2.packet-systems.com/activity")
    page.wait_for_url("https://ssportal-tbs-2.packet-systems.com/activity")

    if operation == "Submit":
        page.locator("table#custList").wait_for()
        page.locator("div.ui-pg-div:text('Submit All Pending List')").click()
        MODULE_LOGGER.info("Data should be submitted, check the screenshot or the page directly")
    else:
        MODULE_LOGGER.warning("Data is not submitted, check the screenshot or the page directly")

    Path("data/absen_result/").mkdir(parents=True, exist_ok=True)
    screenshot_path = f"data/absen_result/ssportal_after_input_{datetime.now().strftime('%Y-%m-%d_%H.%M')}.png"
    page.locator("table#custList").wait_for()
    page.screenshot(path=screenshot_path, full_page=True)
    MODULE_LOGGER.info(f"Screenshot saved in {screenshot_path}")


def run(url_chrome,page_number,credential,browser_type,data):
    """
    TESTED AND CURRENTLY WORKING WITH THE UI PROMPT
    Main method to run the absen fill automation scripts.
    """
    MODULE_LOGGER.info("SSPORTAL fill automation script called")
    print("\nRunning SSPORTAL fill automation scripts\n")
    csv_path = data["csv_file"]
    csv_data = csv_processor.parse(csv_path)
    MODULE_LOGGER.debug(f"Data length are : {len(csv_data)}")
    with sync_playwright() as playwright:
        page = browser_initiator.initial_browser_checker(playwright,url_chrome,page_number,browser_type)
        page.set_default_timeout(60000)
        login_check(credential,page,page_number,browser_type)
        data_fill_processor(page,csv_data)
        data_final_processor(page)
        config_json.update("ssportal_fill")
        MODULE_LOGGER.info("Script Finished")

