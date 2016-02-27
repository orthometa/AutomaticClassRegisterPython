"""
Class Register using Selenium and PhantomJS.
Created on Jan 28, 2016

@author: David Lam
"""

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
import datetime

def main():
    # Initialize Data.
    dataMap = getData()
    crnInput = dataMap["crn"]
    
    # Initialize PhantomJS webdriver and navigate to login page of BannerWeb.
    driver = webdriver.PhantomJS()
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
    while (True):
        currentTime = datetime.datetime.now()
        if (currentTime.hour != 7 or currentTime.minute != 28):
            print(currentTime)
            continue
        
        try:
            crnFields = getCRNFields(driver, crnInput)
            break
        except(NoSuchElementException):
            print("Page Not Ready.")
            driver.refresh() 
    
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
    driver.save_screenshot("confirmation.jpg")
    driver.close()

def getData():
    """
        Pulls user data from data.txt.
        
        Returns a dictionary of relevant data.
    """
    dataFile = open("data.txt", "r")
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
           :type driver :     webdriver.PhantomJS() 
               Selenium PhantomJS driver.
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
            :type driver :    webdriver.PhantomJS()
                Selenium PhantomJS drier.
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