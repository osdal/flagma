import  httpx
import json
import time
import logging
import datetime

import requests

url = "https://base.eriar.com/api/ads/import/71/rollback"
headers = {
    "Api-Key": 'ITmXtu3zu9OySyWSx9W7vWPARatx9YaG'
}
data = {
    # Вставьте ваши данные здесь
}

response_get = requests.get(url, headers=headers)

print("GET:", response_get.status_code)
print("GET:", response_get.text)

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
