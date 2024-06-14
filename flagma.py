import requests
from bs4 import BeautifulSoup as bs
import json
import re
import pandas as pd
import time
import random

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                  'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36'
}


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
if response.status_code == 200:
    html = response.text
soup = bs(html, "html.parser")


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
        # Преобразуем список в DataFrame
        df = pd.DataFrame(links, columns=["links"])

        # Сохраняем DataFrame в CSV файл
        df.to_csv("links.csv", index=False)
        print('Ссылки на вакансии собраны')




# Чтение из CSV файла
df = pd.read_csv("links.csv")

# Преобразуем DataFrame обратно в список
links = df["links"].tolist()

def modify_string(input_string):
    # Удаление вхождения "Работа в "
    modified_string = input_string.replace("Работа в ", "")

    # Удаление последней буквы из оставшегося слова
    if modified_string:
        modified_string = modified_string[:-1]

    return modified_string

def getCategory():
    for link in links:
        response = requests.get(link)
        html = response.text
        soup = bs(html, "html.parser")
        bread_crumbs_div = soup.find('div', class_='bread-crumbs-line')
        spans = bread_crumbs_div.find_all('span')
        print(spans)

        if len(spans) >= 2:
            category = spans[2].find('a').text
            print(category)
        else:
            print("В этой вакансии категория не указана")
            category = "Категория не указана"  # Значение по умолчанию
        return category.text
# ----------------------------------

# response = requests.get('https://flagma.cz/ru/vakansiya-upakovka-yogurtov-danone-bez-nochnyh-smen-rv129962.html')
# html = response.text
# soup = bs(html, "html.parser")


# ------------------------------
def getVacancies():
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
        description = soup.find(id='description-text').text
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
    return(export)



# Имя файла для сохранения
file_name = 'data.jsonl'
def saveJSONL(file_name):
    # Сохранение списка словарей в формате JSONL
    with open(file_name, 'w', encoding='utf-8') as f:
        for item in vacancies:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')

    print(f"Data has been saved to {file_name}")


def sendData(file_name):
    url = 'https://base.eriar.com/api/ads/import'
    files = {'file': open('data.jsonl', 'rb')}
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

# pagesLinks = getPagesLinks()
# getVacancyLinks(pagesLinks)
vacancies = getVacancies()
saveJSONL()
sendData(file_name)


