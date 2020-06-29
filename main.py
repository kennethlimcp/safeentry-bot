from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time, csv
from selenium.webdriver.support.ui import Select

DOWNLOAD_DIR = ""

UEN_ID = ""
CORPPASS_ID = ""
PASSWORD = ""
EMAIL_ADDRESSES = ""

chromeOptions = webdriver.ChromeOptions()
preferences = {"download.default_directory": DOWNLOAD_DIR ,
               "directory_upgrade": True,
               "safebrowsing.enabled": True }
chromeOptions.add_experimental_option("prefs", preferences)

driver = webdriver.Chrome(options=chromeOptions,executable_path="./chromedriver")

def waitForElementPresent(type, elementName):
    try:
        element = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((type, elementName))
        )
    except:
        element = None

    return element

def waitForElementNotPresent(type, elementName):
    try:
        element = WebDriverWait(driver, 10).until_not(
            EC.visibility_of_element_located((type, elementName))
        )
    except:
        element = None

    return element

def waitForUrl(timeout, desiredUrl):
    wait = WebDriverWait(driver, timeout)
    
    try:
       wait.until(lambda driver: driver.current_url == desiredUrl)
    except TimeoutException:
        print('Failed to authenticate login')
        driver.quit()
    
def main():
    driver.get("https://www.ndi-api.gov.sg/cplogin")
    driver.set_window_size(1280, 777)

    # Go to Safe Entry website
    waitForElementPresent(By.LINK_TEXT, "Proceed to Login")
    driver.find_element_by_link_text("Proceed to Login").click()

    time.sleep(5)
    waitForElementPresent(By.ID, "password")
    waitForElementNotPresent(By.CLASS_NAME, "loader")

    element = driver.find_element_by_id("entityId")
    element.send_keys(UEN_ID)

    element = driver.find_element_by_id("corpPassId")
    element.send_keys(CORPPASS_ID)

    element = driver.find_element_by_id("password")
    element.send_keys(PASSWORD)

    element = driver.find_element_by_xpath("//label[contains(.,'Remember Entity ID  ')]")
    element.click()

    # Click on login button
    element = driver.find_element_by_xpath("//button[contains(.,'Login ')]")
    element.click()

    # Wait up to 120 secs for the SingPass auth or else `TimeOutException` is raised.
    # Redirects to this page once Authentication is completed
    waitForUrl(120, 'https://www.ndi-api.gov.sg/partner/dashboard')


    lineCount = 0
    totalTime = 0 

    logFile =  open('./log.txt', "a+")
    with open('./locations.csv') as f:
        rows = csv.reader(f, delimiter=',')
        
        # Iterate through all the rows in CSV
        for r in rows:
            postalCode = r[0]
            venueName = r[1]
            lineCount += 1

            # Show what is read for that row in CSV file
            print("Original", postalCode, venueName, sep=",")
            start = time.time()

            # Click on Apply For SafeEntry (New)
            waitForElementPresent(By.LINK_TEXT, "Apply For SafeEntry New")
            element = driver.find_element_by_link_text("Apply For SafeEntry New")
            element.click()

            # Click on Premises with Address
            # element = driver.find_element_by_xpath("//mat-radio-button[@id='mat-radio-2']/label/div/div")
            # element.click()

            # Postal code of the location
            element = driver.find_element_by_id("postalCode")
            element.clear()
            element.send_keys(postalCode)

            # Venue name of the location
            element = driver.find_element_by_id("venueName")
            element.clear()
            element.send_keys(venueName)
            
            # Fill up email addresses
            element = driver.find_element_by_id('partnerEmails')
            element.clear()
            element.send_keys(EMAIL_ADDRESSES)

            input('Check dropdown list for Block information')

            # Submit the SafeEntry application
            element = driver.find_element_by_xpath("//button[contains(.,'Submit Request')]")
            element.click()

            # Confirm that we want to submit application
            waitForElementPresent(By.XPATH, "//button[contains(.,'Yes, create')]")
            element = driver.find_element_by_xpath("//button[contains(.,'Yes, create')]")
            element.click()

            # Download the QR code image
            waitForElementPresent(By.XPATH, "//b[contains(.,'QRCode')]")
            element = driver.find_element_by_xpath("//b[contains(.,'QRCode')]")
            element.click()
            time.sleep(2)

            # Click OK to dismiss Success modal box
            element = driver.find_element_by_xpath("//button[contains(.,'Ok')]")
            element.click()

            # Grab what is in the applied SafeEntry information and display it
            waitForElementPresent(By.ID, "venueName")
            applied_postalCode = driver.find_element_by_id("postalCode").get_attribute('value')
            applied_venueName = driver.find_element_by_id("venueName").get_attribute('value')

            # Calculate time taken to create a QR code
            end = time.time()
            timeTaken = end - start
            totalTime += timeTaken

            logFile.write(str(lineCount))
            logFile.write(',')
            logFile.write(applied_postalCode)
            logFile.write(',')
            logFile.write(applied_venueName)
            logFile.write(',')
            logFile.write(str(timeTaken))
            logFile.write('\n')
            

            # Print the applied SafeEntry information and display it
            print(lineCount, applied_postalCode, applied_venueName, timeTaken, sep=',')

    f.close()   
    logFile.close()
    driver.quit()
    print('Time taken: ', totalTime) 

if __name__ == "__main__":
    main()
