import requests
from bs4 import BeautifulSoup as bs
import pandas as pd
import json
import re
import time
import random

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                  'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36'
}

response = requests.get('https://flagma.cz/ru/vacancies/page-1/')
html = response.text
# print(response.status_code)
response.encoding = 'utf-8'
if response.status_code == 200:
    html = response.text
soup = bs(html, "html.parser")
print(soup)