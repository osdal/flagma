import csv
import json
import os
import random
import re
import time
import httpx
import requests
from bs4 import BeautifulSoup as bs
from datetime import datetime
import logging
import sys
import io
import pandas as pd


def main():
    try:

        # Получить текущую дату и время
        current_datetime = datetime.now()

        # Преобразовать дату в строку
        current_date = current_datetime.strftime("%Y-%m-%d-%H-%M")

        start_time = time.time()

        def get_custom_proxies():
            # Прокси, которые вы хотите использовать
            return [
                'http://51.159.4.17:15001',
                'http://163.172.36.211:16001',
                'http://83.149.70.159:13010',
            ]

        def clean_string(s):
            return re.sub(r'[^0-9+]', '', s)

        def modify_string(input_string):
            modified_string = input_string.replace("Работа в ", "")
            return modified_string

        def fetch_url_with_proxy(url, proxies, headers, max_retries=5):
            for i in range(max_retries):
                proxy = random.choice(proxies)
                proxy_dict = {"http://": proxy, "https://": proxy}
                try:
                    with httpx.Client(proxies=proxy_dict, timeout=10, verify=False) as client:
                        response = client.get(url, headers=headers, follow_redirects=True)
                        response.raise_for_status()
                        print(response.status_code)
                        if response.status_code == 200:
                            return response
                except httpx.RequestError as e:
                    print(f"Ошибка при подключении к прокси {proxy}: {e}")
                    time.sleep(2)  # Задержка перед следующей попыткой
            raise Exception("Не удалось подключиться ни к одному прокси-серверу")

        # Настройки заголовков
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                          'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36'
        }

        # Получение списка прокси
        proxies = get_custom_proxies()

        # URL страницы, с которой начинаем парсинг
        url = 'https://flagma.cz/ru/vacancies/page-1/'

        # Получение HTML страницы с использованием прокси и заголовков
        response = requests.get(url, headers=headers)
        response.encoding = 'utf-8'
        html = response.text
        print(response.status_code)

        # Парсинг страницы с помощью BeautifulSoup
        soup = bs(html, "html.parser")

        # Функция для получения ссылок на все страницы
        def getPagesLinks():
            baseUrl = 'https://flagma.cz/ru/vacancies/page-'
            pageNumber = int((soup.find('div', id='paginator').
                              find('li', class_='notactive').find('span')).text)
            pagesLinks = []
            for i in range(1, pageNumber + 1):
                pageLink = baseUrl + str(i)
                pagesLinks.append(pageLink)
            return pagesLinks

        pagelinks = getPagesLinks()

        # Функция для получения ссылок на вакансии со всех страниц
        def getVacancyLinks(pagesLinks):
            random_number = random.randint(0, 4)
            # randomList = [{'start': 1, 'finish': 2}, {'start': 11, 'finish': 12}, {'start': 21, 'finish': 22},
            #               {'start': 31, 'finish': 32}, {'start': 41, 'finish': 42}]
            # start = randomList[random_number]['start']
            # finish = randomList[random_number]['finish']
            links = []
            # for pageLink in pagesLinks[start:finish]:
            for pageLink in pagesLinks:
                delay = random.uniform(5, 15)
                print(f"Задержка на {delay:.2f} секунд")
                time.sleep(delay)

                response = requests.get(pageLink, headers=headers)
                html = response.text
                soup = bs(html, "html.parser")
                print(f'Собираю со страницы {pageLink}')
                data_ads = soup.findAll('div', 'header job')
                for block in data_ads:
                    link = block.find('a')['href']
                    links.append(link)
                # Задаем путь к файлу
                file_path = 'DATA/links/vacancies_links.csv'

                # Проверяем, существует ли файл
            if os.path.exists(file_path):
                current_datetime = datetime.now()
                current_date = current_datetime.strftime("%Y-%m-%d-%H-%M")
                file_path = f'DATA/links/vacancies_links-{current_date}.csv'
                vacancy_new = file_path
                with open(file_path, 'w', encoding='utf-8') as file:
                    for item in links:
                        file.write(item + "\n")
                print(f'Файл {vacancy_new} создан')
            else:
                print(f'Файл {file_path} не существует. Создаем его')
                with open(file_path, 'w', encoding='utf-8') as file:
                    # Запись каждого элемента списка в файл
                    for item in links:
                        file.write(item + "\n")
            return links, vacancy_new

        def compareVacanciesLinks(vacancy_old, vacancy_new):
            try:
                file_path = 'DATA/links/vacancy_diff.csv'
                os.remove(file_path)
                print(f"Файл {file_path} успешно удалён")
            except FileNotFoundError:
                print(f"Файл {file_path} не найден")
            except PermissionError:
                print(f"Нет прав для удаления файла {file_path}")
            except Exception as e:
                print(f"Ошибка при удалении файла {file_path}: {e}")
            try:
                with open(vacancy_old, 'r') as file:
                    # Читаем все строки файла, убираем символы новой строки и сохраняем их в список
                    lines = [line.strip() for line in file]
                with open(vacancy_new, 'r') as file:
                    # Читаем все строки файла, убираем символы новой строки и сохраняем их в список
                    lines_new = [line.strip() for line in file]
                vacancies_diff = [item for item in lines_new if item not in lines]
                print('Изменения в вакансиях')
                print(vacancies_diff)
                with open(f'report-{current_date}.txt', 'a') as file:
                    # Запись строки в конец файла
                    file.write(f"Новых вакансий + {str(len(vacancies_diff))}.\n")
                if not vacancies_diff:
                    print("Нет различий между файлами вакансий. Прекращение выполнения программы.")
                    sys.exit(0)
                return vacancies_diff
            except:
                pass

        pageLinks = getPagesLinks()
        links, vacancy_new = getVacancyLinks(pageLinks)
        print('Собрано вакансий ' + str(len(links)))
        print(f'Они сохранены в файл {vacancy_new}')
        vacancy_old = 'DATA/links/vacancies_links.csv'

        # Функция для получения данных по каждой вакансии
        def getVacancies(links):
            export = []
            for index, link in enumerate(links, start=1):
                try:
                    delay = random.uniform(5, 15)
                    print(f"Задержка на {delay:.2f} секунд")
                    time.sleep(delay)
                    response = requests.get(link, headers=headers)
                    html = response.text
                    soup = bs(html, "html.parser")
                    type_id = 1
                    title = soup.find('h1').text.strip() if soup.find('h1') else ""
                    description = soup.find(id='description-text').text.strip() if soup.find(
                        id='description-text') else ""
                    name = soup.find('div', 'user-name').text.strip() if soup.find('div', 'user-name') else ""
                    phone = clean_string(soup.find('a', 'tel').text.strip() if soup.find('a', 'tel') else "")
                    contacts = [{"type": "phone", "value": phone}]
                    author = {
                        "name": name,
                        "contacts": contacts,
                    }
                    country = 'Чехия'
                    city = modify_string(soup.find('span', {'itemprop': 'name'}).text)
                    print(city)
                    category = soup.find('div', 'bread-crumbs-line').find_all('span')[3].find(
                        'a').text.strip() if soup.find(
                        'div', 'bread-crumbs-line') and soup.find_all('span')[3] and soup.find('a') else ""
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
                    print(f'Собрана вакансия {index}')
                    export.append(data)
                except Exception as e:
                    logging.error(f"Ошибка при сборе вакансии с ссылки {link}", exc_info=True)
                    print(f"Ошибка при сборе вакансии с ссылки {link}: {e}")
            return export

        diff = compareVacanciesLinks(vacancy_old=vacancy_old, vacancy_new=vacancy_new)
        print('Длина diff ' + str(len(diff)))
        vacancies = getVacancies(diff)

        # Функция для сохранения данных в формате JSONL
        def saveJSONL(vacancies, file_name):
            try:
                with open(file_name, 'w', encoding='utf-8') as f:
                    for item in vacancies:
                        f.write(json.dumps(item, ensure_ascii=False) + '\n')
                print(f"Данные сохранены в {file_name}")
                return file_name
            except Exception as e:
                logging.error(f"Ошибка при сохранении данных в файл {file_name}", exc_info=True)
                print(f"Ошибка при сохранении данных в файл {file_name}: {e}")
                return None

        file_name = 'DATA/data.jsonl'
        saveJSONL(vacancies, file_name)

        # Функция для отправки данных на сервер
        def sendData(file_name):
            url = 'https://base.eriar.com/api/ads/import'
            files = {'file': open(file_name, 'rb')}
            headers = {'Api-Key': 'ITmXtu3zu9OySyWSx9W7vWPARatx9YaG'}

            try:
                with httpx.Client() as client:
                    response = client.post(url, files=files, headers=headers)
                    print(response.status_code)
                    print(response.text)
                    imp_id = json.loads(response.text)
                    import_id = imp_id['import_id']
                    url = f'https://base.eriar.com/api/ads/import/{import_id}'
                    response = client.get(url, headers=headers)
                    print(response.status_code)
                    print(response.text)

                    current_datetime = datetime.now()
                    current_date = current_datetime.strftime("%Y-%m-%d-%H-%M")
                    file_name = f'DATA/logs/report-{current_date}.txt'

                    if response.status_code == 200:
                        with open(file_name, 'a', encoding='utf-8') as text_file:
                            text_file.write(response.text)
                    else:
                        with open(file_name, 'a', encoding='utf-8') as text_file:
                            text_file.write(str(response.status_code))

            except Exception as e:
                logging.error("Произошла ошибка при отправке данных на сервер", exc_info=True)
                print(f"Ошибка при отправке данных на сервер: {e}")

        file_name = 'DATA/data.jsonl'
        sendData(file_name)

        end_time = time.time()
        execution_time = end_time - start_time

        # Открываем файл в режиме добавления ('a')
        file_name = 'DATA/logs/' + current_date + '.txt'
        with open(file_name, 'a', encoding='utf-8') as file:
            # Пишем данные в файл
            file.write(f'Программа выполнялась {str(execution_time)} c.\n')
        # raise ValueError("Пример ошибки")
    except Exception as e:
        logging.error("Произошла ошибка", exc_info=True)
        print(f"Ошибка записана в файл error.log: {e}")

if __name__ == "__main__":
    main()
