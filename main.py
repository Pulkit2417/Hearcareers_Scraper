# For daily update we can add time.sleep(seconds)
# after those particular seconds it will run again
# we can also add random.randint so that it won't be dtected by bots
# if we don't want to duplicate the jobs, we can fetch the job links from the links column in csv file we created from df.to_csv
# if the link already exists then we can ignore that job.
# we are not using a headless webdriver because it causes timeout error.


from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import csv
import time
import pandas as pd


def DriverOptions():
    options = Options()
    options.add_argument("--window-size=1920,1080")
    #options.add_argument("--headless==new")
    driver = webdriver.Chrome(options=options)
    return driver


def applyFilters(driver, keyword):
    driver.get("https://hearcareers.audiology.org/jobs/")
    inputElement = driver.find_element(By.ID, "jobTitle")
    inputElement.send_keys(keyword)
    inputElement.send_keys(Keys.RETURN)
    time.sleep(5)

    # click on sort dropdown
    driver.find_element(By.ID, "bti-dropdown-sort-search").click()
    time.sleep(2)
    # select the most recent option in the dropdown list
    dropdown_items = driver.find_elements(By.CLASS_NAME, "dropdown-item")
    for item in dropdown_items:
        if item.text == "Newest":
            item.click()
            break
    time.sleep(5)
    return driver


def saveTocsv(job_details, saved_job_links):
    with open("jobs.csv", "a+", newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=job_details.keys())
        if not saved_job_links:  # If file is empty, write header
            writer.writeheader()
        writer.writerow(job_details)


def scrapeSave(driver, saved_job_links):
    jobCount = driver.find_element(By.CLASS_NAME, 'bti-result-count-display').text
    count = 0
    while count<int(jobCount):
        jobList = driver.find_element(By.CLASS_NAME, "bti-job-search-results").find_elements(By.CLASS_NAME, "card")
        for job in jobList:
            count+=1
            url = job.find_element(By.TAG_NAME, "a").get_attribute('href')
            if url in saved_job_links: continue
            element = WebDriverWait(driver, 20).until(EC.visibility_of(job))
            # Scroll the element into view
            driver.execute_script("arguments[0].scrollIntoView(true);", element)
            action = ActionChains(driver)
            action.move_to_element(element).click().perform()
            time.sleep(2)
            print(f"{count}: {url}")
            jobTitle = driver.find_element(By.CLASS_NAME, "border-bottom").find_element(By.CLASS_NAME, "h4").text
            jobCompany = driver.find_element(By.CLASS_NAME, "border-bottom").find_element(By.CLASS_NAME, "h5").text
            jobDetails = driver.find_element(By.CLASS_NAME, "bti-jd-main-container").find_elements(By.TAG_NAME, "p")
            job_details = {
                            "Job Link": url,
                            "Job Title": jobTitle,
                            "Company": jobCompany,
                        }
            for detail in jobDetails:
                try:
                    key, value = detail.text.split(":")
                    job_details[key] = value
                    #print(f"{key} : {value}")
                except:
                    #print(f"Description: {detail.text}")
                    job_details["Description"] = detail.text
                    break
            saveTocsv(job_details, saved_job_links)
            print()
            time.sleep(2)

        try:
            driver.execute_script('window.scrollTo(0,document.body.scrollHeight)')
            element = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.LINK_TEXT, "Load More")))
            # Scroll the element into view
            driver.execute_script("arguments[0].scrollIntoView(true);", element)
            # Move to the element's location and click
            action = ActionChains(driver)
            action.move_to_element(element).click().perform()
            time.sleep(5)
        except:
            print(f"All Jobs Done!")
            break


if __name__ =="__main__":
    keyword = "Audiologist"
    # Load previously saved job links to avoid duplicates
    try:
        df = pd.read_csv("jobs.csv")
        saved_job_links = df['Job Link'].tolist()
    except FileNotFoundError:
        saved_job_links = []
    
    while True:
        driver = DriverOptions()
        driver = applyFilters(driver, keyword)
        scrapeSave(driver, saved_job_links)
        driver.quit()
        # wait for 10 minutes before scraping the site again
        # 10*60 is equal to 600. i.e. 600s
        time.sleep(600)
