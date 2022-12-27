from bs4 import BeautifulSoup
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from time import sleep
from datetime import datetime
from os import path, mkdir

def set_chrome_driver():
    chrome_options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=chrome_options
    )
    return driver

def open_url(driver, url):
    driver.get(url)
    SCROLL_PAUSE_SEC = 1
    last_height = driver.execute_script("return document.body.scrollHeight")

    while True:
        # scroll down to end of view
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # sleep for loading
        sleep(SCROLL_PAUSE_SEC)

        # get new height
        new_height = driver.execute_script("return document.body.scrollHeight")

        # first, check height again
        if last_height == new_height:
            # sleep for loading
            sleep(SCROLL_PAUSE_SEC)

            # get new height
            new_height = driver.execute_script("return document.body.scrollHeight")

            # break on second time
            if last_height == new_height:
                break

        last_height = new_height


def enter_input_keyword():
    keyword = input("Enter word what you want to get result.\n")
    if keyword is None or len(keyword) < 1:
        raise ValueError("the value is incorrect.")
    else:
        print(f"Entered keyword : {keyword}")
        return keyword

def do_job_scrapper(driver, base_url, keyword):
    results = []
    request_url = f"{base_url}/search?query={keyword}"
    print(f"Do Extract With this URL({request_url})")
    
    open_url(driver, request_url)

    soup = BeautifulSoup(driver.page_source, "html.parser")
    job_card_list = soup.find_all("div", {"data-cy": "job-card"})

    for job_card in job_card_list:
        link = job_card.select_one("a")['href']
        if link is not None:
            link = f"{base_url}{link}"
        position = job_card.select_one("div.job-card-position").string.replace(",", " ")
        company = job_card.select_one("div.job-card-company-name").string.replace(",", " ")
        location = ''.join(list(job_card.select_one("div.job-card-company-location").stripped_strings)).replace(",", " ")

        results.append({
            "company": company,
            "position": position,
            "location": location,
            "link": link
        })

    return results

def write_result_to_file(dirpath, filename, job_results):
    if path.isdir(dirpath) is False:
        mkdir(dirpath)
    file = open(path.join(dirpath, filename), "w", encoding="utf-8")
    file.write("Position,Company,Location,URL\n")

    for job_result in job_results:
        position = job_result['position']
        company = job_result['company']
        location = job_result['location']
        link = job_result['link']
        file.write(f"{position},{company},{location},{link}\n")
    file.close()

if __name__ == "__main__":
    BASE_URL = "https://www.wanted.co.kr"
    keyword = enter_input_keyword()

    driver = set_chrome_driver()

    job_scrap_results = do_job_scrapper(driver, BASE_URL, keyword)

    now = datetime.now()
    dateformat_str = now.strftime("%Y_%m_%d_%H_%M_%S")
    filename = f"{dateformat_str}-{keyword}.csv"

    ROOT_DIR = path.dirname(path.abspath(__file__))
    RESULT_DIR_PATH = path.join(ROOT_DIR, "../../results")
    write_result_to_file(RESULT_DIR_PATH, filename, job_scrap_results)
