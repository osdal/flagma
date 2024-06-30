import csv
import json
import os
import random
import re
import requests
import time
from bs4 import BeautifulSoup as bs
from datetime import datetime
import pandas as pd
import logging

logging.basicConfig(filename='DATA/logs/error.log',
                    filemode='w',
                    format='%(name)s - %(levelname)s - %(message)s',
                    level=logging.ERROR)


def clean_string(s):
    return re.sub(r'[^0-9+]', '', s)


def main():
    try:
        current_datetime = datetime.now()
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

        def dataExistFunc(root_dir, filename):
            for dirpath, dirnames, filenames in os.walk(root_dir):
                if filename in filenames:
                    return True
            return False

        root_directory = 'DATA'
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
                    file_name = f"vacancies_links-{current_date}.csv"
                else:
                    file_name = f"vacancies_links.csv"
                file_path = os.path.join(nested_folder, file_name)

                os.makedirs(nested_folder, exist_ok=True)

                with open(file_path, 'w', newline='', encoding='utf-8') as file:
                    writer = csv.writer(file)
                    for item in links:
                        writer.writerow([item])
            return links

        dataExist = dataExistFunc(root_directory, file_to_find)
        if dataExist:
            print(f"Файл '{file_to_find}' найден в '{root_directory}' или одной из его вложенных папок.")
        else:
            print(f"Файл '{file_to_find}' не найден в '{root_directory}' или одной из его вложенных папок.")

        pageslinks = getPagesLinks()

        links = getVacancyLinks(pageslinks, dataExist)

        vacancy_old = 'DATA/links/vacancies_links.csv'
        vacancy_new = f'DATA/links/vacancies_links-{current_date}.csv'

        num_new_vacancies = compareVacanciesLinks(vacancy_old, vacancy_new)

        if num_new_vacancies >= 0:  # Убедимся, что результат не отрицательный
            if num_new_vacancies > 0:
                print(f"На дату {current_date} появилось {num_new_vacancies} новых вакансий.")
            else:
                print(f"На дату {current_date} новых вакансий не было.")
        else:
            print(
                f"Произошла ошибка при сравнении файлов вакансий. Пожалуйста, проверьте логи для дополнительной информации.")

        file_path = 'DATA/links/vacancy_diff.csv'
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as file:
                reader = csv.reader(file)
                next(reader)  # Пропускаем заголовок
                links = [line[0] for line in reader]
            if not links:
                with open('DATA/logs/report.txt', 'a', encoding='utf-8') as report_file:
                    report_file.write(f"На дату {current_date} изменений в вакансиях не было.\n")
                print(f"На дату {current_date} изменений в вакансиях не было. Программа завершена.")
                return
            else:
                with open('DATA/logs/report.txt', 'a', encoding='utf-8') as report_file:
                    report_file.write(f"На дату {current_date} появилось {len(links)} новых вакансий.\n")
                print(f"На дату {current_date} появилось {len(links)} новых вакансий.")

        vacancies = getVacancies(links)

        file_name = f'DATA/data-{current_date}.jsonl'
        file_name = saveJSONL(vacancies, file_name, dataExist)

        sendData(file_name)

        end_time = time.time()
        execution_time = end_time - start_time

        with open(f'DATA/logs/report-{current_date}.txt', 'a', encoding='utf-8') as file:
            file.write(f"Программа выполнялась {execution_time:.2f} сек.\n")

    except Exception as e:
        logging.error("Произошла ошибка", exc_info=True)
        print(f"Ошибка записана в файл error.log: {e}")


def compareVacanciesLinks(vacancy_old, vacancy_new):
    try:
        # Чтение файлов в DataFrame
        df1 = pd.read_csv(vacancy_old)
        df2 = pd.read_csv(vacancy_new)

        # Сравнение DataFrame
        df_diff = pd.concat([df1, df2]).drop_duplicates(keep=False)

        if not df_diff.empty:
            # Сохранение различий в файл без заголовка url
            nested_folder = "DATA/links"
            file_name = "vacancy_diff.csv"
            file_path = os.path.join(nested_folder, file_name)

            os.makedirs(nested_folder, exist_ok=True)

            df_diff.to_csv(file_path, index=False, header=False)

            print(f'Файл {file_path} успешно создан.')

            # Удаление старого файла и переименование нового
            if os.path.exists(vacancy_old):
                os.remove(vacancy_old)
                print(f"Файл {vacancy_old} удалён.")

            os.rename(vacancy_new, vacancy_old)
            print(f"Файл {vacancy_new} переименован в {vacancy_old}.")

            # Определение количества новых вакансий
            num_new_vacancies = len(df_diff)
            return num_new_vacancies

        else:
            print("Нет различий между файлами вакансий. Файл vacancy_diff.csv не будет создан.")
            return 0

    except Exception as e:
        print(f"Ошибка при сравнении файлов вакансий: {e}")
        return -1


def getVacancies(links):
    export = []
    for index, link in enumerate(links, start=1):
        try:
            delay = random.uniform(5, 15)
            print(f"Задержка на {delay:.2f} секунд")
            time.sleep(delay)
            response = requests.get(link)
            html = response.text
            soup = bs(html, "html.parser")
            type_id = 1
            title = soup.find('h1').text.strip() if soup.find('h1') else ""
            description = soup.find(id='description-text').text.strip() if soup.find(id='description-text') else ""
            name = soup.find('div', 'user-name').text.strip() if soup.find('div', 'user-name') else ""
            phone = clean_string(soup.find('a', 'tel').text.strip() if soup.find('a', 'tel') else "")
            contacts = [{"type": "phone", "value": phone}]
            author = {
                "name": name,
                "phone": phone,
            }
            country = soup.find('div', 'location').find('span', 'country-name').text.strip() if soup.find('div',
                                                                                                          'location') and soup.find(
                'span', 'country-name') else ""
            city = soup.find('div', 'location').find('span', 'locality').text.strip() if soup.find('div',
                                                                                                   'location') and soup.find(
                'span', 'locality') else ""
            category = soup.find('div', 'bread-crumbs-line').find_all('span')[3].find('a').text.strip() if soup.find(
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


def saveJSONL(vacancies, file_name, dataExist):
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


def sendData(file_name):
    url = 'https://base.eriar.com/api/ads/import'
    files = {'file': open(file_name, 'rb')}
    headers = {'Api-Key': 'ITmXtu3zu9OySyWSx9W7vWPARatx9YaG'}

    try:
        response = requests.post(url, files=files, headers=headers)
        print(response.status_code)
        print(response.text)
        imp_id = json.loads(response.text)
        import_id = imp_id['import_id']
        url = f'https://base.eriar.com/api/ads/import/{import_id}'
        response = requests.get(url, headers=headers)
        print(response.status_code)
        print(response.text)

        current_datetime = datetime.now()
        current_date = current_datetime.strftime("%Y-%m-%d")
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


if __name__ == "__main__":
    main()
