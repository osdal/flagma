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
import sys

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
        # Чтение файлов в DataFrame
        df1 = pd.read_csv(vacancy_old)
        df2 = pd.read_csv(vacancy_new)

        # Сравнение DataFrame
        df_diff = pd.concat([df1, df2]).drop_duplicates(keep=False)
        print(df_diff)
        if not df_diff.empty:
            # Сохранение различий в файл без заголовка url
            nested_folder = "DATA/links/"
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
            print(num_new_vacancies)
            return num_new_vacancies

        else:
            print("Нет различий между файлами вакансий. Файл vacancy_diff.csv не будет создан.")
            return 0

    except Exception as e:
        print(f"Ошибка при сравнении файлов вакансий: {e}")
        return -1
compareVacanciesLinks('DATA/links/vacancies.csv', 'DATA/links/vacancies_links2.csv')