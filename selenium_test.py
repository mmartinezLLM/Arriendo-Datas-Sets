from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

opts = Options()
opts.add_argument('--headless=new')
opts.add_argument('--disable-gpu')
service = Service(ChromeDriverManager().install())
try:
    d = webdriver.Chrome(service=service, options=opts)
    d.get('https://www.example.com')
    print('TITLE:', d.title)
    d.quit()
except Exception as e:
    print('ERROR:', e)
