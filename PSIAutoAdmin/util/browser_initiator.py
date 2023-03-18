from playwright.sync_api import sync_playwright
import logging

MODULE_LOGGER = logging.getLogger()

def list_page(url_chrome):
    MODULE_LOGGER.debug("List existing page method called")
    with sync_playwright() as playwright:
        browser = playwright.chromium.connect_over_cdp(url_chrome)
        return browser.contexts[0].pages

def change_page(playwright,page_number,url_chrome,url_page="http://example.com"):
    browser = playwright.chromium.connect_over_cdp(url_chrome)
    page = browser.contexts[0].pages[page_number]
    page.goto(url_page)

def open_page(playwright,url_chrome,url_page="http://example.com"):
    browser = playwright.chromium.connect_over_cdp(url_chrome)
    page = browser.new_page()
    page.goto(url_page)
    page.wait_for_timeout(10000) 

def test_locator(playwright,url_chrome,data):
    browser = playwright.chromium.connect_over_cdp(url_chrome)
    page1 = browser.contexts[0].pages[data["page_number"]]
    page2 = browser.contexts[0].pages[data["page_number"]+1]
    test_a1 = page1.locator("div#content",has=page1.locator("font",has_text="ERROR.... Overlapping Activity")).is_hidden()
    test_a2 = page1.locator("div#content",has=page1.locator("font",has_text="ERROR.... Overlapping Activity")).is_visible()
    test_b1 = page2.locator("div#content",has=page2.locator("font",has_text="ERROR.... Overlapping Activity")).is_hidden()
    test_b2 = page2.locator("div#content",has=page2.locator("font",has_text="ERROR.... Overlapping Activity")).is_visible()
    print(page1.url)
    print(test_a1)
    print(test_a2)
    print()
    print(page2.url)
    print(test_b1)
    print(test_b2)

def initial_browser_checker(playwright,url_chrome,page_number,browser_type):
    """
    Checking what browser needed to be run by playwright.
    """
    MODULE_LOGGER.debug("Initial browser checker method called")
    MODULE_LOGGER.info("Playwright session is started")
    if browser_type == "EXISTING" and page_number is None:
        page = initial_page_opener(playwright,url_chrome)
    elif browser_type == "HEADED":
        page = headed_mode_opener(playwright)
    elif browser_type == "HEADLESS":
        page = headless_mode_opener(playwright)
    else:
        page = initial_page_selector(playwright,url_chrome,page_number)

    return page

def initial_page_selector(playwright,url_chrome,page_number):
    """
    Method to use the existing browser instead of opening new browser.
    Navigate to the corresponding site manually first.
    """
    MODULE_LOGGER.debug("Existing page selector method called")
    MODULE_LOGGER.info("Using Existing browser session, will select mentioned page")
    browser = playwright.chromium.connect_over_cdp(url_chrome)
    return browser.contexts[0].pages[page_number]

def initial_page_opener(playwright,url_chrome):
    """
    Method for opening new browser window in existing browser session.
    """
    MODULE_LOGGER.debug("New page opener method called")
    MODULE_LOGGER.info("Will open new page in existing browser session")
    browser = playwright.chromium.connect_over_cdp(url_chrome)
    return browser.new_page(screen={"width":1366,"height":786},viewport={"width":1366,"height":786})

def headless_mode_opener(playwright):
    """
    Method to use headless mode.
    Will initialze new browser that is not visible to user.
    """
    MODULE_LOGGER.debug("Headless opener method called")
    browser = playwright.chromium.launch().new_context(
        ignore_https_errors=True,
        screen={"width":1366,"height":786},
        viewport={"width":1366,"height":786})
    return browser.new_page()

def headed_mode_opener(playwright):
    """
    Method to use headed mode.
    Will initialze new browser that is visible to user.
    """
    MODULE_LOGGER.debug("Headed opener method called")
    browser = playwright.chromium.launch(headless=False).new_context(
        ignore_https_errors=True,
        screen={"width":1366,"height":786},
        viewport={"width":1366,"height":786})
    return browser.new_page()
