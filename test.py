import requests
from bs4 import BeautifulSoup as bs
import pandas as pd
import json
import re
import time
import random
import os


headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                  'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36'
}

# response = requests.get('https://flagma.cz/ru/vacancies/page-1/')
# html = response.text
# # print(response.status_code)
# response.encoding = 'utf-8'
# if response.status_code == 200:
#     html = response.text
# soup = bs(html, "html.parser")
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
