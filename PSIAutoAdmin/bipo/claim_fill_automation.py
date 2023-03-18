from playwright.sync_api import sync_playwright
from PSIAutoAdmin.util import csv_processor,browser_initiator
import json
import logging

MODULE_LOGGER=logging.getLogger()

def login_check(credential,page,page_number,browser_type):
    """
    Initial check of what browser needed to be run by playwright.
    Also check if you need to login or not.
    Auto fill the login form if needed.
    """
    MODULE_LOGGER.debug("Login checker method called")
    if credential is None:
        try:
            with open('secret.json', 'r') as stream:
                data_json = json.load(stream)
            used_credential = data_json["bipo"]
            MODULE_LOGGER.info("Credential obtained from json")
        except:
            MODULE_LOGGER.error("Credential not provided via json file or cli ui")
            raise ImportError("""
            Credential is not provided and the json file is not found.
            Please provide the credential by creating json file based on the template.
            Or provide it on the CLI Prompter UI.
            """)
    else:
        used_credential = credential
        MODULE_LOGGER.info("Credential obtained from ui")

    if page_number is None or browser_type in ["HEADLESS","HEADED"]:
        while page.url != 'https://ap2.bipocloud.com/PSI/EMP/SSApp':
            MODULE_LOGGER.info("Trying to Login to the site")
            MODULE_LOGGER.info(f"Currently at: {page.url}")
            page.goto('https://ap2.bipocloud.com/PSI/Login')
            page = login_navigator(page,used_credential)
    MODULE_LOGGER.info(f"Currently at: {page.url}")

def login_navigator(page,credential):
    """
    Navigate the login process. 
    From input username password to MFA.
    """
    # page.pause()
    
    MODULE_LOGGER.debug("Login Navigator method called")
    MODULE_LOGGER.info("Navigating trough the site")
    while page.locator("div.pa-welcome-title span").is_hidden():
        # page.goto("https://ap2.bipocloud.com/PSI/Login")
        page.get_by_placeholder("Enter Login ID").fill(credential["username"].replace("@packet-systems.com",""))
        page.locator("a:has-text(\"Sign In with Microsoft\")").click()

        page.locator("div :text-matches('sign in|pick an account','i')").wait_for()
        if page.get_by_role("heading", name="Pick an account").is_visible():
            page.get_by_role("button", name="Use another account").click()

        
        page.get_by_placeholder("someone@packet-systems.com").fill(credential["username"])
        page.get_by_role("button", name="Next").click()

        page.locator("div :text-matches('incorrect|error|couldn?t find|enter password','i')").wait_for()
        if page.get_by_text("This username may be incorrect.").is_visible():
            raise EnvironmentError("This username may be incorrect.")
        if page.get_by_text("We couldn't find an account with that username.").is_visible():
            raise EnvironmentError("We couldn't find an account with that username.")

        page.get_by_placeholder("Password").fill(credential["password"])
        page.get_by_role("button", name="Sign in").click()
        
        
        page.locator('div :text-matches("incorrect","si"),h1:text-matches("duo","si")').wait_for()
        if page.get_by_text("Your account or password is incorrect.").is_visible():
            raise EnvironmentError("Your account or password is incorrect.")
            
        if page.get_by_role("heading", name="Check for a Duo Push").is_visible():
            MODULE_LOGGER.info("Waiting for Multi Factor Authentication. Please check your phone!")
            print("Waiting for Multi Factor Authentication. Please check your phone!")

        page.get_by_role("heading", name="Check for a Duo Push").wait_for(state="hidden")
        if page.get_by_role("heading", name="Duo Push timed out").is_visible():
            page.get_by_role("button", name="Try again").click()

        page.locator('div h1:text-matches("trust","i"),div:text-matches("stay","i")').wait_for()
        if page.get_by_role("heading", name="Trust this browser?").is_visible():
            page.get_by_role("button", name="Yes, trust browser").click()

        page.locator('div h1:text-matches("trust","i"),div:text-matches("stay","i")').wait_for()
        if page.get_by_role("heading", name="Stay signed in?").is_visible():
            page.get_by_role("button", name="No").click()


        page.locator(':text-matches("Your Login ID does not match your Microsoft Account.","i"),:text-matches("click me!","i")').wait_for()
        if page.get_by_text("Your Login ID does not match your Microsoft Account.").is_visible():
            MODULE_LOGGER.error("Credential wrong!")
            raise EnvironmentError("Your Login ID does not match your Microsoft Account.")
            

    if page.get_by_text("Click Me!").is_visible():
         page.get_by_role("button", name="OK").click()
    
    return page

def form_navigator(page):
    """
    Method to navigate bipo from home page to claim data form.
    """
    MODULE_LOGGER.debug("Form navigator method called")
    page.locator("a.hr-menu-item",has=page.locator("span",has_text="Home")).click()

    page.locator("div.pa-welcome-title span").wait_for()
    page.locator("a#hrSelectSystem").click()
    page.locator("div.popover-content",has=page.locator("text='Finance'")).click()
    page.locator("a.menuToggle",has=page.locator("span", has_text="Claim")).click()
    page.locator("li a.hr-menu-item",has_text="Apply Claim").click()

    page.locator("input#cboClaim_I").fill("Operational Claim")
    page.locator("input#cboClaim_I").press("Enter")
    page.locator("input#CFR08_I").fill("Cost Center")
    page.locator("input#CFR08_I").press("Enter")

def claim_fill_processor(page,csv_data,docx_path):
    """
    The actual data processing method after the site is navigated.
    Will automatically fill data based on csv provided,
    Also automatically upload the compiled screenshot in docx file provided.
    """
    MODULE_LOGGER.debug("Fill processor method called")
    MODULE_LOGGER.info(f"Total data is : {len(csv_data)}")
    for index,individual_data in enumerate(csv_data):
        MODULE_LOGGER.info(f"Filling data {index+1} / {len(csv_data)}")
        print(f"Filling data {index+1} / {len(csv_data)}")
        if index == 0:
            page.locator("td#DetailAttachment_B0").click()
            page.locator("span#hrPopupBoxTitle",has_text="Uploaded Files").wait_for()
            with page.expect_file_chooser() as fc_info:
                MODULE_LOGGER.info(f"docx file will be uploaded")
                page.locator("tr#FileUploadControl_FI0").click()
            file_chooser = fc_info.value
            file_chooser.set_files(docx_path)
            page.locator("td#FileUploadControl_Upload").click()
            page.locator("tr#gvFileUploadContainer_DXDataRow0").wait_for()
            page.locator("button#hrPopupBoxClose").click()
            page.locator("span#hrPopupBoxTitle",has_text="Uploaded Files").wait_for(state="hidden")
            MODULE_LOGGER.info(f"docx file in : {docx_path} has been uploaded")
        
        page.locator("input#ExpenseCode_I").fill("OTM - Overtime Meals")
        page.locator("input#ExpenseCode_I").press("Enter")

        page.locator("input#ReceiptDate_I").click()
        page.locator("input#ReceiptDate_I").type(individual_data["date"])
        page.locator("input#ReceiptDate_I").press("Enter")

        page.locator("input#ReceiptAmount_I").click()
        page.locator("input#ReceiptAmount_I").fill(individual_data["nominal"])
        page.locator("input#ReceiptAmount_I").press("Enter")

        page.locator("textarea#Remarks_I").fill(individual_data["activity"])

        if index == len(csv_data)-1:
            page.locator("button#btnUpdate").click()
        else:
            page.locator("button#btnCopySave").click()
            page.locator("div#hrMsgBoxContent",has_text="Do you want to copy the attachment as well?").wait_for()
            page.locator("button#hrMsgBoxButton1").click()

        page.locator("div#hrMsgBoxContent",has_text="Record has been updated.").wait_for()
        MODULE_LOGGER.info(f"Data {index+1} dari {len(csv_data)} filled to the form")
        page.locator("button#hrMsgBoxButton1").click()
        page.locator(f"tr#gvCRDetailMultiple_DXDataRow{index}").wait_for()

def claim_save(page,operation="save"):
    """
    Method to save or submit the form data after being automatically filled.
    Currently defaulted to save instead of submit.
    """
    MODULE_LOGGER.debug("Claim finalizer method called")
    if operation == "save":

        MODULE_LOGGER.info("Claim data has been saved as draft. Please validate it manually before submiting!")
        page.locator("button#btnSave").click()
        page.locator("div#hrMsgBoxContent",has_text="Record has been updated.").wait_for()
        page.locator("button#hrMsgBoxButton1").click()
        print("Claim data has been saved as draft. Please validate it manually before submiting!")
    elif operation == "submit":
        MODULE_LOGGER.info("Claim will be submitted")
        page.locator("button#btnSubmit").click()

def run(url_chrome,page_number,credential,browser_type,data):
    """
    TESTED AND CURRENTLY WORKING WITH THE UI PROMPT
    Main method to run the bipo claim fill automation scripts.
    """

    MODULE_LOGGER.info("BIPO claim filler script called")
    print("Running BIPO claim filler script")
    docx_path = data["docx_file"]
    csv_path = data["csv_file"]
    MODULE_LOGGER.info(f"docx file in path : {docx_path}")
    MODULE_LOGGER.info(f"csv file in path : {csv_path}")
    csv_data = csv_processor.parse(csv_path)

    with sync_playwright() as playwright:
        page = browser_initiator.initial_browser_checker(playwright,url_chrome,page_number,browser_type)
        login_check(credential,page,page_number,browser_type)

        form_navigator(page)
        claim_fill_processor(page,csv_data,docx_path)
        if data.get("submit"):
            claim_save(page,operation="submit")
        else:
            claim_save(page)
        MODULE_LOGGER.info("Script Finished")