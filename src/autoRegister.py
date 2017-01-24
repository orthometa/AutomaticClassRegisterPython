"""
Class Register using Selenium.

Default driver is PhantomJS.

Supported drivers:
    PhantomJS
    Chrome
    Mozilla Firefox (unrealiable since marionette update)
Created on Jan 28, 2016

@author: David Lam
"""

from selenium import webdriver
from selenium.webdriver.common.alert import Alert
from selenium.common.exceptions import NoSuchElementException
import datetime
import os
import sys
import time

BANNER_WEB_URL = "https://prod11gbss8.rose-hulman.edu/BanSS/twbkwbis.P_WWWLogin"


def setup_directory():
    """
        Creates the logs and img files if not created.
    """
    # Make directory for logs and images if necessary.
    if (not os.path.isdir("../logs/")):
        os.makedirs("../logs/")
    if (not os.path.isdir("../img/")):
        os.makedirs("../img/")


def main():
    # Ensure a data file path is given.
    if (len(sys.argv) < 2):
        print("AutoRegister.py <dataFile> <opt:browser>")
        return
    setup_directory()

    # Initialize Data.
    dataMap = getData(sys.argv[1])
    # Initialize Webdriver.
    driver = getDriver(sys.argv[2].lower())
    # login into banner
    login(driver, dataMap["username"], dataMap["password"])
    # navigate to registeration page
    enterRegisterationPage(driver, dataMap["pin"])

    # Take picture of the waiting page
    driver.save_screenshot("../img/waitPage.jpg")

    # Refresh page until crnFields are found.
    while True:
        # Prevent refreshing until two minutes before opening time
        currentTime = datetime.datetime.now()
        if (currentTime.hour < 7 and currentTime.minute < 28):
            print(currentTime)
            continue
        break

    # attempt to registerate
    if not attemptToRegisterate(driver, dataMap["crn"]):
        login(driver, dataMap["username"], dataMap["password"])
        enterRegisterationPage(driver, dataMap["pin"])
        # active waiting
        while True:
            # Enter CRN info and registerate
            if attemptToRegisterate(driver, dataMap["crn"]):
                break;

    # Take picture and close driver.
    driver.save_screenshot("../img/confirmation.jpg")

    # quiting the program
    if (isinstance(driver, webdriver.PhantomJS)):
        driver.close()
    else:
        print("Waiting For User to terminate (Ctrl-C)")
        while(True):
            pass

def login(driver, userName, password):
    # Navigate to BannerWeb.
    driver.get(BANNER_WEB_URL)

    # Login to Bannerweb.
    driver.find_element_by_name("sid").send_keys(userName)
    driver.find_element_by_name("PIN").send_keys(password)
    clickTagWithValue(driver, "input", "Login")


def enterRegisterationPage(driver, pin):
    # Navigate to Registeration page and enter PIN.
    driver.get("https://prod11gbss8.rose-hulman.edu/BanSS/bwskfreg.P_AltPin")
    clickTagWithValue(driver, "input", "Submit")
    driver.find_element_by_name("pin").send_keys(pin)
    clickTagWithValue(driver, "input", "Submit")

def getDriver(browser):
    if (browser == "chrome"):
        return webdriver.Chrome(
            "../drivers/chromedriver.exe", service_log_path="../logs/chrome.log")
    elif (browser == "phantom"):
        return webdriver.PhantomJS(
            "../drivers/phantomjs.exe", service_log_path="../logs/phantom.log")
    elif (browser == "firefox"):
        # Based on MDN. Import when only required to. (Firefox has Alert(driver))
        from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
        caps = DesiredCapabilities.FIREFOX
        caps["marionette"] = True
        return webdriver.Firefox(
            executable_path="../drivers/geckodriver.exe", capabilities=caps)
    else:
        print("Invalid option...using PhantomJS")
        return webdriver.PhantomJS(
            "../drivers/phantomjs.exe", service_log_path="../logs/phantom.log")

def getData(dataFile):
    """
        Pulls user data from data.txt.

        Returns a dictionary of relevant data.
    """
    dataFile = open(dataFile, "r")
    dataMap = {}

    for line in dataFile:
        lineList = line.split()
        dataMap[lineList[0]] = lineList[1:len(lineList)]

    dataFile.close()

    return dataMap


def clickTagWithValue(driver, tagName, value):
    """
       Attempts to click on a button with a specific tag name and value.
       It will click the first button with specified value.

       Arguments:
           :type driver :     webdriver
               Selenium Webdriver.
           :type tagName :    str
               Specified HTML tag name.
           :type value :      str
               Specified HTML value related to tag name.

        Returns nothing.
    """
    inputList = driver.find_elements_by_tag_name(tagName)

    for element in inputList:
        if (element.get_attribute("value") == value):
            element.click()
            break


def attemptToRegisterate(driver, crnInput):
    """
        Gets the CRN text box and fills it in with crn numbers.

        Arguments:
            :type driver :    webdriver
                Selenium Webdriver.
            :type crnInput :  list
                List of CRN numbers.

        Returns a list of CRN text box.
        Raises Selenium.NoSuchElementException
    """
    crnFields = []
    identifier = 1

    try:
        while (len(crnFields) < len(crnInput)):
            crnFields.append(driver.find_element_by_id(
                "crn_id" + str(identifier)).send_keys(crnInput[identifier - 1]))
            identifier += 1
        clickTagWithValue(driver, "input", "Submit Changes")
        return True
    except(NoSuchElementException):
        print("Page Not Ready.")
        driver.refresh()
        if (isinstance(driver, webdriver.Firefox)):
            Alert(driver).accept()
    return False

if __name__ == "__main__":
    main()
