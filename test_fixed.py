import csv
import json
import os
import random
import re
import time
from datetime import datetime
import pandas as pd

import requests
from bs4 import BeautifulSoup as bs

# Получить текущую дату и время
current_datetime = datetime.now()

# Преобразовать дату в строку
current_date = current_datetime.strftime("%Y-%m-%d-%H-%M")

start_time = time.time()
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                  'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36'
}

response = requests.get('https://flagma.cz/ru/vacancies/page-1/')
html = response.text
response.encoding = 'utf-8'
if response.status_code == 200:
    html = response.text
soup = bs(html, "html.parser")


def clean_string(s):
    # Заменяем все символы, кроме цифр и плюса, на пустую строку
    return re.sub(r'[^0-9+]', '', s)


def modify_string(input_string):
    # Удаление вхождения "Работа в "
    modified_string = input_string.replace("Работа в ", "")

    # Удаление последней буквы из оставшегося слова
    if modified_string:
        modified_string = modified_string[:-1]

    return modified_string


def dataExistFunc(root_dir, filename):
    for dirpath, dirnames, filenames in os.walk(root_dir):
        if filename in filenames:
            dataExist = True
            return dataExist
    dataExist = False
    return dataExist


# Пример использования
root_directory = 'DATA'  # Укажите путь к папке DATA
file_to_find = 'data.jsonl'


def getPagesLinks():
    baseUrl = 'https://flagma.cz/ru/vacancies/page-'
    pageNumber = int((soup.find('div', id='paginator').
                      find('li', class_='notactive').find('span')).text)
    pagesLinks = []
    for i in range(1, pageNumber + 1):
        pageLink = baseUrl + str(i)
        pagesLinks.append(pageLink)
    return pagesLinks


def getVacancyLinks(pagesLinks, dataExist):
    links = []
    vacancy_new = None
    vacancy_old = None
    for pageLink in pagesLinks:
        delay = random.uniform(5, 15)
        print(f"Задержка на {delay:.2f} секунд")
        time.sleep(delay)

        response = requests.get(pageLink)
        html = response.text
        soup = bs(html, "html.parser")
        print(f'Собираю со страницы {pageLink}')
        data_ads = soup.findAll('div', 'header job')
        for block in data_ads:
            link = block.find('a')['href']
            links.append(link)

        nested_folder = "DATA/links"
        if dataExist:
            file_name_new = f"vacancies_links-{current_date}.csv"
            vacancy_new = file_name_new
            file_path = os.path.join(nested_folder, file_name_new)
        else:
            file_name_old = f"vacancies_links.csv"
            vacancy_old = file_name_old
            file_path = os.path.join(nested_folder, file_name_old)

        os.makedirs(nested_folder, exist_ok=True)

        with open(file_path, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            for item in links:
                writer.writerow([item])
    return links, vacancy_new, vacancy_old


if dataExistFunc(root_directory, file_to_find):
    print(f"Файл '{file_to_find}' найден в '{root_directory}' или одной из его вложенных папок.")
    dataExist = True
else:
    print(f"Файл '{file_to_find}' не найден в '{root_directory}' или одной из его вложенных папок.")
    dataExist = False


def compareVacanciesLinks(vacancy_old, vacancy_new):
    df1 = pd.read_csv(vacancy_old, header=None, names=['url'])
    df2 = pd.read_csv(vacancy_new, header=None, names=['url'])

    unique_to_df1 = df1[~df1['url'].isin(df2['url'])]
    unique_to_df2 = df2[~df2['url'].isin(df1['url'])]

    result_df = pd.concat([unique_to_df1, unique_to_df2], ignore_index=True)

    result_df.to_csv('DATA/links/vacancy_diff.csv', index=False, header=False)


pageslinks = getPagesLinks()
dataExist = dataExistFunc(root_directory, file_to_find)  # Исправлено: передача аргументов
links, vacancy_new, vacancy_old = getVacancyLinks(pageslinks, dataExist)

file_path = 'DATA/links/vacancy_diff.csv'

links = []

with open(file_path, mode='r', newline='', encoding='utf-8') as csvfile:
    csvreader = csv.reader(csvfile)
    for row in csvreader:
        line = ','.join(row)
        links.append(line)


def getVacancies(links):
    export = []
    for link in links:
        delay = random.uniform(5, 15)
        print(f"Задержка на {delay:.2f} секунд")
        time.sleep(delay)
        response = requests.get(link)
        html = response.text
        soup = bs(html, "html.parser")
        type_id = 4
        title = soup.find('h1').text
        if soup.find(id='description-text').text is not None:
            description = soup.find(id='description-text').text
        else:
            print(f'У вакансии {link} нет описания')
            description = ""
        name = soup.find('div', 'user-name').text

        phone = clean_string(soup.find('a', 'tel').text)
        cont = {
            "type": "phone",
            "contact": phone
        }
        contacts = [cont]
        author = {
            "name": name,
            "contacts": contacts
        }
        country = "Чехия"
        city = modify_string(soup.find('span', itemprop='name').text)
        bread_crumbs_div = soup.find('div', class_='bread-crumbs-line')
        spans = bread_crumbs_div.find_all('span')
        category = spans[3].find('a').text
        data = {
            "type_id": type_id,
            "title": title,
            "description": description,
            "view_url": link,
            "author": author,
            "country": country,
            "city": city,
            "category": category
        }
        export.append(data)
    return export


vacancies = getVacancies(links)  # Исправлено: определение переменной до вызова функции saveJSONL


def saveJSONL(file_name, vacancies):  # Исправлено: передача аргументов в функцию
    with open(file_name, 'w', encoding='utf-8') as f:
        for item in vacancies:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')

    print(f"Data has been saved to {file_name}")


def sendData(file_name):
    url = 'https://base.eriar.com/api/ads/import'

