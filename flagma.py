import requests
from bs4 import BeautifulSoup as bs
import json

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                  'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36'
}

import re

def clean_string(s):
    # Заменяем все символы, кроме цифр и плюса, на пустую строку
    return re.sub(r'[^0-9+]', '', s)

# Пример использования
# input_string = "a+b=c123+456"
# cleaned_string = clean_string(input_string)
# print(cleaned_string)  # Вывод: "+123+456"


response = requests.get('https://flagma.cz/ru/vacancies/page-1/')
html = response.text
# print(response.status_code)
response.encoding = 'utf-8'
soup = bs(html, "html.parser")

links = []
data_ads = soup.findAll('div', 'header job')
# for name_ad in data_ads:
#     job_name = name_ad.find('h2').text

for limk_ad in data_ads:
    link = limk_ad.find('a')['href']
    links.append(link)

for link in links:
    response = requests.get(link)
    html = response.text
    soup = bs(html, "html.parser")

contacts = []
response = requests.get(links[0])
html = response.text
soup = bs(html, "html.parser")

type_id = 4
title = soup.find('h1').text
description = soup.find(id='description-text').text
name = soup.find('div', 'user-name').text

phone = clean_string(soup.find('a', 'tel').text)
cont = {
    "type": "phone",
    "contact": phone
}
contacts.append(cont)
author = {
    "name": name,
    "contacts": contacts
}


data = {
    "type_id": type_id,
    "title": title,
    "description": description,
    "view_url": links[0],
    "author": author
}
print(data)

file_path = 'data.jsonl'
with open(file_path, 'w', encoding='utf-8') as f:
    # Преобразование словаря в строку формата JSON и запись в файл
    f.write(json.dumps(data, ensure_ascii=False) + '\n')

print(f"Данные успешно сохранены в файл {file_path}")

url = 'https://base.eriar.com/api/ads/import'
files = {'file': open('data.jsonl', 'rb')}
headers = {'Api-Key': 'ITmXtu3zu9OySyWSx9W7vWPARatx9YaG'}

response = requests.post(url, files=files, headers=headers)

print(response.status_code)
print(response.text)

url = 'https://base.eriar.com/api/ads/import/10'
headers = {'Api-Key': 'ITmXtu3zu9OySyWSx9W7vWPARatx9YaG'}

response = requests.get(url, headers=headers)

print(response.status_code)
print(response.text)
# for i in range(len(data_ads)):
#     data_ad = {
#         'title': job_name,
#         'link': link,
#     }
#     data_ads[i] = data_ad
# print(len(links))
