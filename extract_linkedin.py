import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
 
options = Options()
# options.add_argument('--headless')
# options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument(r"--user-data-dir=/home/skidooman/.config/google-chrome") #e.g. C:\Users\You\AppData\Local\Google\Chrome\User Data
chrome_options.add_argument(r'--profile-directory=Default') #e.g. Profile 3
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
driver.get('http://www.linkedin.com')
input('First log in to LinkedIn, then press any key')

#search = driver.find_element(by=By.NAME, value="q")
#search.send_keys("Hey, Tecadmin")
#search.send_keys(Keys.RETURN)

driver.get('https://www.linkedin.com/in/steve-barriault/recent-activity/all/')
time.sleep(7)

SCROLL_PAUSE_TIME = 2

# Get scroll height
last_height = driver.execute_script("return document.body.scrollHeight")

while True:
    # Scroll down to bottom
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    # Wait to load page
    time.sleep(SCROLL_PAUSE_TIME)

    # Calculate new scroll height and compare with last scroll height
    new_height = driver.execute_script("return document.body.scrollHeight")
    if new_height == last_height:
        break
    last_height = new_height

print ('END OF PAGE')
with open("linkedin_dump.html", "w", encoding='utf-8') as f:
    f.write(driver.page_source)
input ('press any key')
 
time.sleep(5)
driver.close()

