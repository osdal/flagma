import requests
from bs4 import BeautifulSoup as bs
import pandas as pd
import json
import re
import time
import random
import os
import csv


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
# print(soup)


# Пример списка, содержащего словари
data = [
    {"name": "Alice", "age": 30, "city": "New York"},
    {"name": "Bob", "age": 25, "city": "San Francisco"},
    {"name": "Charlie", "age": 35, "city": "Los Angeles"}
]

# Путь к вложенной папке и имя файла
nested_folder = "nested/folder"
file_name = "data.jsonl"
file_path = os.path.join(nested_folder, file_name)

# Создание вложенной папки, если она не существует
os.makedirs(nested_folder, exist_ok=True)

# Запись списка в файл в формате JSONL
with open(file_path, 'w', encoding='utf-8') as f:
    for item in data:
        json_line = json.dumps(item)
        f.write(json_line + '\n')

print(f"Данные успешно сохранены в файл {file_path}")

# Пример новых данных, которые нужно добавить в файл
new_data = [
    {"name": "David", "age": 40, "city": "Seattle"},
    {"name": "Eve", "age": 28, "city": "Boston"}
]

# Путь к вложенной папке и имя файла
nested_folder = "nested/folder"
file_name = "data.jsonl"
file_path = os.path.join(nested_folder, file_name)

# Создание вложенной папки, если она не существует
os.makedirs(nested_folder, exist_ok=True)

# Добавление новых данных в файл в формате JSONL
with open(file_path, 'a', encoding='utf-8') as f:
    for item in new_data:
        json_line = json.dumps(item)
        f.write(json_line + '\n')

print(f"Новые данные успешно добавлены в файл {file_path}")

def getPagesLinks():
    baseUrl = 'https://flagma.cz/ru/vacancies/page-'
    pageNumber = int((soup.find('div', id='paginator').
                      find('li', class_='notactive').find('span')).text)
    pagesLinks = []
    for i in range(1, pageNumber + 1):
        pageLink = baseUrl + str(i)
        pagesLinks.append(pageLink)
    return (pagesLinks)

def getVacancyLinks(pagesLinks):
    links = []
    for pageLink in pagesLinks:
        # Выбор случайного времени задержки от 10 до 20 секунд
        delay = random.uniform(5, 15)
        # Печать времени задержки (опционально)
        print(f"Задержка на {delay:.2f} секунд")
        # Задержка выполнения программы
        time.sleep(delay)

        response = requests.get(pageLink)
        html = response.text
        soup = bs(html, "html.parser")
        print(f'Собираю со страницы {pageLink}')
        data_ads = soup.findAll('div', 'header job')
        for block in data_ads:
            link = block.find('a')['href']
            links.append(link)
    return links

pageslinks = getPagesLinks()
links = getVacancyLinks(pageslinks)
# Путь к вложенной папке и имя файла
nested_folder = "DATA/links"
file_name = "vacancies_links.csv"
file_path = os.path.join(nested_folder, file_name)

# Создание вложенной папки, если она не существует
os.makedirs(nested_folder, exist_ok=True)

# Открываем файл в режиме записи ('w' - write) по полному пути
with open(file_path, 'w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    for item in links:
        writer.writerow([item])

# Путь к вашему CSV файлу во вложенной папке
file_path = 'DATA/links/vacancies_links.csv'

# Список для хранения данных
data_list = []

# Открываем файл и читаем его содержимое
with open(file_path, newline='', encoding='utf-8') as csvfile:
    csvreader = csv.reader(csvfile)
    for row in csvreader:
        data_list.append(row)

# Выводим данные, чтобы убедиться, что они считаны правильно
for row in data_list:
    print(row)

