from InquirerPy import inquirer as ui
from InquirerPy.validator import PathValidator
from PSIAutoAdmin.util import browser_initiator,csv_processor
from PSIAutoAdmin.notion import database_downloader
from PSIAutoAdmin.ssportal import absen_fill_automation,claim_data_collector
from PSIAutoAdmin.bipo import claim_fill_automation
from pathlib import PureWindowsPath,Path
from datetime import datetime
import requests
import re
import os
import logging

SECRET = Path("secret.json").is_file()

def initial_browser_prompter(site):
    """
    UI prompting user to choose playwright browser type.
    Also prompting credential if needed.
    """
    main_logger.debug("Browser prompter method called")
    browser_command_ui = ui.select(
        message="Select browser type to run:",
        choices=[
            "Existing browser, new page",
            "Existing browser, existing page",
            "New browser, headed session",
            "New browser, headless session",
        ]
    ).execute()

    main_logger.info(f"Browser type for playwright is : {browser_command_ui}")

    if re.search("Existing browser",browser_command_ui):
        print("Trying to find browser . . .")
        try:
            url_browser = requests.get("http://localhost:9222/json/version").json()["webSocketDebuggerUrl"]
            browser_type = "EXISTING"
            main_logger.info(f"Existing browser session found with url:\n{url_browser}\n")
        except:
            main_logger.error(f"Existing browser not found")
            raise EnvironmentError("""
            Something wrong while connecting to browser.
            Please make sure chrome browser with remote-debugging at port 9222 is running.
            Please refer to README again if confused.
            """)
    elif re.search("headed session",browser_command_ui):
        browser_type = "HEADED"
        url_browser = None
    elif re.search("headless session",browser_command_ui):
        browser_type = "HEADLESS"
        url_browser = None


    if re.search("existing page",browser_command_ui):
        pages = browser_initiator.list_page(url_browser)
        while True:
            page_list_ui = ui.select(
                message="Select page:",
                choices=enumerate(pages)
            ).execute()
            main_logger.info(f"Selected tab : {page_list_ui}")
            if re.search(f"^https?\:\/{{2}}{site}",page_list_ui[1].url):
                existing_page_number = page_list_ui[0]
                existing_page_url = page_list_ui[1].url
                break
            else:
                main_logger.error(f"Wrong tab selected")
                print("Wrong url in the selected page for this script")
    else:
        existing_page_url = None
        existing_page_number = None

    if existing_page_number is None and SECRET is False:
        credential_data = login_prompter()
    else:
        credential_data = None

    return {
        "page_number":existing_page_number,
        "url":existing_page_url,
        "credential":credential_data,
        "url_browser":url_browser,
        "browser_type":browser_type,
        }
    
def login_prompter():
    """
    UI to prompt for login credential
    """

    main_logger.debug("Login prompter method called")
    while True:
        email_ui = ui.text(
            message="Please type the email:"
        ).execute()

        if re.search("@packet-systems.com$",email_ui) is None:
            main_logger.error("Email not correct")
        else:
            break
    
    while True:
        password_ui = ui.secret(
            message="Please type the password:"
        ).execute()

        if password_ui is None or password_ui == "":
            main_logger.error("Empty password")
        else:
            break

    return {"username":email_ui,"password":password_ui}

def file_selector(dialog,extension,path=""):
    """
    UI to prompt for file. 
    Also check for file extension. 
    Return posix-base path from windows-base path.
    """
    main_logger.debug("File prompter method called")
    main_logger.info(f'Current working directory is : {os.getcwd()}')
    while True:
        file_selector_ui = ui.filepath(
            message=dialog,
            default=path,
            validate=PathValidator(is_file=True, message="Input is not a file")
        ).execute()
        path_result = str(PureWindowsPath(file_selector_ui).as_posix())
        if re.search(f"\.{extension}$",path_result):
            break
        else:
            main_logger.error(f'File type is not correct. Must have {extension} extension\n')
    main_logger.info(f"Path of file selected is in : {file_selector_ui}")
    return path_result

def data_source_prompter(extension,special_choice=None):
    """
    UI to prompt user for data source location.
    Currently being used primarily by ssportal claim fill automation scripts.
    """
    main_logger.debug("Data source prompter method called")
    data_source_choice = [f"Internet {extension}",f"Local {extension}"]

    if special_choice is not None:
        data_source_choice.extend(special_choice)

    data_source_ui = ui.select(
        message="Select where data source come from:",
        choices=data_source_choice,
        default=f"Local {extension}"
    ).execute()

    main_logger.info(f"Data sources from : {data_source_ui}")
    if re.search("Internet",data_source_ui):
        while True:
            url_prompt_ui = ui.text(
                message=f"Input the url to get the {extension} file:",
            ).execute()

            if url_prompt_ui is None or url_prompt_ui == "":
                main_logger.error("Empty URL")
            elif re.search("^https?\:\/{2}|^www\.",url_prompt_ui) is None:
                main_logger.error("URL wrong")
            else:
                break
        data_source_path = csv_processor.get(url_prompt_ui)
    elif re.search("Local",data_source_ui):
        data_source_path = file_selector(f"Choose file {extension}:",extension)
    elif re.search("Notion",data_source_ui):
        data_source_path = database_downloader.get()
        
    return data_source_path

def main():
    """
    The main menu ui in the start of the script. 
    Prompting of what actual scripts to run.
    Checking browser connectivity & what behavior of browser user want.
    Also set some parameter needed to run the actual scripts.
    """

 
    print("Welcome to PSI Administration Automation")
    main_logger.debug("Main method started")
    main_command_ui = ui.select(
        message="Select main script to run:",
        choices=[
            "SSPORTAL Claim Data Collector",
            "SSPORTAL Fill Automation",
            "BIPO Claim Automation",
            "TEST"
        ]
    ).execute()
    

    if re.match("^SSPORTAL",main_command_ui):
        site = "ssportal-tbs-2.packet-systems.com"
    elif re.match("^BIPO",main_command_ui):
        site = "ap2.bipocloud.com"
    else:
        site = ""

    main_logger.info(f"Main script to run is : {main_command_ui}")
    browser_data = initial_browser_prompter(site)


    if main_command_ui == "SSPORTAL Claim Data Collector":
        claim_data_collector.run(
            browser_data["url_browser"],
            browser_data["page_number"],
            browser_data["credential"],
            browser_data["browser_type"]
            )
    elif main_command_ui == "SSPORTAL Fill Automation":
        file_data = {
            "csv_file" : data_source_prompter("csv",["Notion Database"])
            }
        absen_fill_automation.run(
            browser_data["url_browser"],
            browser_data["page_number"],
            browser_data["credential"],
            browser_data["browser_type"],
            file_data,
            )
    elif main_command_ui == "BIPO Claim Automation":
        file_data = {
            "csv_file" : file_selector("Choose file csv:","csv"),
            "docx_file" : file_selector("Choose file docx:","docx")
            }
        claim_fill_automation.run(
            browser_data["url_browser"],
            browser_data["page_number"],
            browser_data["credential"],
            browser_data["browser_type"],
            file_data,
            )
    elif main_command_ui == "TEST":
        browser_initiator.test_locator(browser_data["url_browser"],browser_data)

if __name__ == "__main__":
    main_logger = logging.getLogger()

    current_time = datetime.now().strftime('%H.%M-%d-%m-%Y')

    stdout_handler = logging.StreamHandler()
    file_handler = logging.FileHandler(f"log/session-{current_time}.log")

    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s : %(message)s'))
    stdout_handler.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))

    main_logger.setLevel(logging.DEBUG)
    stdout_handler.setLevel(logging.INFO)
    file_handler.setLevel(logging.DEBUG)

    main_logger.addHandler(stdout_handler)
    main_logger.addHandler(file_handler)

    main_logger.info(f"Script called directly started at : {datetime.now().strftime('%H:%M %d-%m-%Y')}")
    main()