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
# print(response.status_code)
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
    return (pagesLinks)


def getVacancyLinks(pagesLinks, dataExist):
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

        nested_folder = "DATA/links"
        if dataExist:
            file_name_new = f"vacancies_links-{current_date}.csv"
            vacancy_new = file_name_new
        else:
            file_name_old = f"vacancies_links.csv"
            vacancy_old = file_name_old
        file_path = os.path.join(nested_folder, file_name)

        # Создание вложенной папки, если она не существует
        os.makedirs(nested_folder, exist_ok=True)

        # Открываем файл в режиме записи ('w' - write) по полному пути
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
    # Чтение данных из CSV файлов
    df1 = pd.read_csv(vacancy_old, header=None, names=['url'])
    df2 = pd.read_csv(vacancy_new, header=None, names=['url'])

    # Найти уникальные строки в каждом DataFrame
    unique_to_df1 = df1[~df1['url'].isin(df2['url'])]
    unique_to_df2 = df2[~df2['url'].isin(df1['url'])]

    # Объединить уникальные строки в один DataFrame
    result_df = pd.concat([unique_to_df1, unique_to_df2], ignore_index=True)

    # Сохранить отличающиеся строки в новый CSV файл
    result_df.to_csv('DATA/links/vacancy_diff.csv', index=False, header=False)


pageslinks = getPagesLinks()
dataExist = dataExistFunc()
links = getVacancyLinks(pageslinks, dataExist)

# Путь к вашему CSV файлу во вложенной папке
file_path = 'DATA/links/vacancy_diff.csv'

# Список для хранения данных
links = []

# Открываем файл и читаем его содержимое
with open(file_path, mode='r', newline='', encoding='utf-8') as csvfile:
    csvreader = csv.reader(csvfile)
    for row in csvreader:
        # Преобразуем список в строку, соединяя элементы через запятую
        line = ','.join(row)
        links.append(line)


def getVacancies(links):
    export = []
    for link in links:
        # Выбор случайного времени задержки от 10 до 20 секунд
        delay = random.uniform(5, 15)

        # Печать времени задержки (опционально)
        print(f"Задержка на {delay:.2f} секунд")

        # Задержка выполнения программы
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
        contacts = []
        contacts.append(cont)
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
        # vacancies = json.dumps(export, indent=4, ensure_ascii=False)

        # Имя файла для сохранения
        file_name = 'DATA/data.jsonl'
    return export


# Имя файла для сохранения
file_name = 'DATA/data.jsonl'


def saveJSONL(file_name):
    # Сохранение списка словарей в формате JSONL
    with open(file_name, 'w', encoding='utf-8') as f:
        for item in vacancies:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')

    print(f"Data has been saved to {file_name}")


def sendData(file_name):
    url = 'https://base.eriar.com/api/ads/import'
    files = {'file': open('DATA/data.jsonl', 'rb')}
    headers = {'Api-Key': 'ITmXtu3zu9OySyWSx9W7vWPARatx9YaG'}

    response = requests.post(url, files=files, headers=headers)

    print(response.status_code)
    print(response.text)
    imp_id = json.loads(response.text)
    import_id = imp_id['import_id']
    url = f'https://base.eriar.com/api/ads/import/{import_id}'
    print(url)
    headers = {'Api-Key': 'ITmXtu3zu9OySyWSx9W7vWPARatx9YaG'}

    response = requests.get(url, headers=headers)
    #
    print(response.status_code)
    print(response.text)

    # Получить текущую дату и время
    current_datetime = datetime.now()

    # Преобразовать дату в строку
    current_date = current_datetime.strftime("%Y-%m-%d")
    file_name = 'DATA/logs/' + current_date + '.txt'

    if response.status_code == 200:
        # Записываем строку в текстовый файл
        with open(file_name, 'w', encoding='utf-8') as text_file:
            text_file.write(response.text)
    else:
        with open(file_name, 'w', encoding='utf-8') as text_file:
            text_file.write(response.status_code)


compareVacanciesLinks(vacancy_old=vacancy_old, vacancy_new=vacancy_new)
vacancies = getVacancies(links)
saveJSONL(file_name)
# sendData(file_name)


end_time = time.time()
execution_time = end_time - start_time

# Открываем файл в режиме добавления ('a')
file_name = 'DATA/logs/' + current_date + '.txt'
with open(file_name, 'a', encoding='utf-8') as file:
    # Пишем данные в файл
    file.write(f'Программа выполнялась {str(execution_time)} c.\n')
