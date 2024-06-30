import csv
import json
import os
import random
import re
import time
import httpx
from bs4 import BeautifulSoup as bs
from datetime import datetime
import pandas as pd
import logging
import sys
import io

def get_custom_proxies():
    # Прокси, которые вы хотите использовать
    return [
        'http://51.159.4.17:15001',
        'http://163.172.36.211:16001'
    ]

def fetch_url_with_proxy(url, proxies, headers, max_retries=5):
    for i in range(max_retries):
        proxy = random.choice(proxies)
        proxy_dict = {"http://": proxy, "https://": proxy}
        try:
            with httpx.Client(proxies=proxy_dict, timeout=10, verify=False) as client:
                response = client.get(url, headers={k: v.encode('ascii', 'ignore').decode('ascii') for k, v in headers.items()})
                response.raise_for_status()
                print(response.status_code)
                if response.status_code == 200:
                    return response
        except httpx.RequestError as e:
            print(f"Ошибка при подключении к прокси {proxy}: {e}")
            time.sleep(2)  # Задержка перед следующей попыткой
    raise Exception("Не удалось подключиться ни к одному прокси-серверу")

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                  'AppleWebKit/537.36 (KHTML, как Gecko) Chrome/81.0.4044.138 Safari/537.36'
}

proxies = get_custom_proxies()
print(proxies)
url = 'https://flagma.cz/ru/vacancies/page-1/'  # Добавляем завершающий слэш
response = fetch_url_with_proxy(url, proxies, headers)
response.encoding = 'utf-8'
html = response.text
print(response.status_code)
soup = bs(html, "html.parser")
print(soup)