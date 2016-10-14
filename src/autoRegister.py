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
import time
import sys
import os

def main():
    # Ensure a data file path is given.
    if (len(sys.argv) < 2):
        print("main.py <dataFile> <opt:browser>")
        return

    # Make directory for logs and images if necessary.
    if (not os.path.isdir("../logs/")):
        os.makedirs("../logs/")
    if (not os.path.isdir("../img/")):
        os.makedirs("../img/")

    # Initialize Data.
    dataMap = getData(sys.argv[1])
    crnInput = dataMap["crn"]

    # Initialize boolean
    isFirefox = False # (Firefox has Alert(driver))

    # Initialize Webdriver.
    if (len(sys.argv) > 2):
        if (sys.argv[2].lower() == "chrome"):
            driver = webdriver.Chrome("../drivers/chromedriver.exe", service_log_path="../logs/chrome.log")
        elif (sys.argv[2].lower() == "phantom"):
            driver = webdriver.PhantomJS("../drivers/phantomjs.exe", service_log_path="../logs/phantom.log")
        elif (sys.argv[2].lower() == "firefox"):
            # Based on MDN. Import when only required to.
            isFirefox = True
            from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
            caps = DesiredCapabilities.FIREFOX
            caps["marionette"] = True
            driver = webdriver.Firefox(executable_path="../drivers/geckodriver.exe",capabilities=caps)
        else:
            print("Invalid option...using PhantomJS")
            driver = webdriver.PhantomJS("../drivers/phantomjs.exe", service_log_path="../logs/phantom.log")
    else:
        driver = webdriver.PhantomJS("../drivers/phantomjs.exe", service_log_path="../logs/phantom.log")

    # Make the window relatively small so it doesn't cover the screen.
    driver.set_window_size(600, 480)

    # Navigate to BannerWeb.
    driver.get("https://prod11gbss8.rose-hulman.edu/BanSS/twbkwbis.P_WWWLogin")

    # Login to Bannerweb.
    driver.find_element_by_name("sid").send_keys(dataMap["username"])
    driver.find_element_by_name("PIN").send_keys(dataMap["password"])
    clickTagWithValue(driver, "input", "Login")

    # Navigate to Registeration page and enter PIN.
    driver.get("https://prod11gbss8.rose-hulman.edu/BanSS/bwskfreg.P_AltPin")
    clickTagWithValue(driver, "input", "Submit")
    driver.find_element_by_name("pin").send_keys(dataMap["pin"])
    clickTagWithValue(driver, "input", "Submit")

    # Refresh page until crnFields are found.
    firstTimeWaiting = True
    while (True):
        # Screenshot the first time it reaches this loop.
        if (firstTimeWaiting):
            driver.save_screenshot("../img/waitPage.jpg")
            firstTimeWaiting = False

        # Prevent refreshing until two minutes before opening time
        currentTime = datetime.datetime.now()
        if (currentTime.hour < 7 or currentTime.minute < 28):
            print(currentTime)
            continue

        try:
            crnFields = getCRNFields(driver, crnInput)
            break
        except(NoSuchElementException):
            print("Page Not Ready.")
            driver.refresh()
            if (isFirefox):
                Alert(driver).accept()

    # Get potential submit buttons.
    regButtons = driver.find_elements_by_name("REG_BTN")

    # Enter CRN numbers.
    crnIndex = 0
    for element in crnFields:
        if (element.get_attribute("type") == "text" and element.get_attribute("name") == "CRN_IN"):
            element.send_keys(crnInput[crnIndex])
            crnIndex += 1

    # Submit Changes
    for element in regButtons:
        if (element.get_attribute("value") == "Submit Changes"):
            element.click()
            break

    # Take picture and close driver.
    driver.save_screenshot("../img/confirmation.jpg")
    driver.close()

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

def getCRNFields(driver, crnInput):
    """
        Gets the CRN text box.

        Arguments:
            :type driver :    webdriver
                Selenium Webdriver.
            :type crnInput :  list
                List of CRN numbers.

        Returns a list of CRN text box.
        Raises Selenium.NoSuchElementException
    """
    crnFields = []

    while(len(crnFields) < len(crnInput)):
        for k in range(len(crnInput)):
            crnFields.append(driver.find_element_by_id("crn_id" + str(k + 1)))

    return crnFields

if __name__ == "__main__":
    main()
