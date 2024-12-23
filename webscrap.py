from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time

from webdriver_manager.chrome import ChromeDriverManager

# Set up Selenium with ChromeDriver
chrome_service = Service(ChromeDriverManager().install())
chrome_options = Options()
chrome_options.add_argument("--headless")  # Run in headless mode

driver = webdriver.Chrome(service=chrome_service, options=chrome_options)

url = "https://www.tripadvisor.com/Attractions-g30196-Activities-c57-Austin_Texas.html"
driver.get(url)

# Wait for the page to load
time.sleep(5)

# Get page source and parse with BeautifulSoup
soup = BeautifulSoup(driver.page_source, "html.parser")

items = soup.find_all("span", {"name": "title"})

for i in items:
    print(i.text)
