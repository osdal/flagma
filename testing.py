import requests
from bs4 import BeautifulSoup as bs
import random

# Выбор случайного целого числа от 1 до 5
random_number = random.randint(1, 5)

headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                          'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36'
        }

response = requests.get('https://flagma.cz/ru/vacancies/page-1/', headers=headers)
html = response.text
response.encoding = 'utf-8'
if response.status_code == 200:
    html = response.text
soup = bs(html, "html.parser")


def parse_hidemyname_proxies():
    url = 'https://hidemy.name/en/proxy-list/'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                      '(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            soup = bs(response.text, 'html.parser')
            proxy_list = []

            table = soup.find('div', class_='table_block').find('table')
            rows = table.find_all('tr')
            for row in rows[1:]:  # Пропускаем заголовок таблицы
                cols = row.find_all('td')
                ip = cols[0].text.strip()
                port = cols[1].text.strip()
                proxy = f"{ip}:{port}"
                proxy_list.append(proxy)

            return proxy_list

        else:
            print(f"Ошибка при получении страницы: {response.status_code}")
            return None

    except requests.exceptions.RequestException as e:
        print(f"Ошибка запроса: {e}")
        return None


# Функция для проверки, работает ли прокси
def is_proxy_working(proxy):
    test_url = "https://flagma.cz/ru/vacancies/page-1/"
    proxy_dict = {
        "http": f"http://{proxy}",
        "https": f"https://{proxy}",
    }

    try:
        response = requests.get(test_url, proxies=proxy_dict, timeout=5)
        if response.status_code == 200:
            return True
    except requests.exceptions.RequestException as e:
        print(f"Прокси {proxy} не работает: {e}")

    return False


# Функция для получения рабочих прокси
def get_working_proxies(proxies, max_proxies=5):
    working_proxies = []
    for proxy in proxies:
        if is_proxy_working(proxy):
            working_proxies.append(proxy)
            if len(working_proxies) >= max_proxies:
                break
    return working_proxies


# Функция для выполнения запроса с использованием прокси
def fetch_with_proxy(url, proxies, retries=5):
    for _ in range(retries):
        if not proxies:
            print("Нет доступных прокси.")
            return None
        proxy = random.choice(proxies)
        proxy_dict = {
            "http": f"http://{proxy}",
            "https": f"https://{proxy}",
        }

        try:
            response = requests.get(url, proxies=proxy_dict, timeout=5)
            if response.status_code == 200:
                return response
        except requests.exceptions.RequestException as e:
            print(f"Не удалось подключиться через прокси {proxy}: {e}")
            proxies.remove(proxy)

    return None


# Получаем список прокси с HideMy.name
proxies = parse_hidemyname_proxies()
print(f"Получено прокси: {proxies}")

# Проверяем доступность прокси и берем первые 5 рабочих
working_proxies = get_working_proxies(proxies, max_proxies=5)
print(f"Рабочие прокси: {working_proxies}")

# Пример использования функции для парсинга с рабочими прокси
url = "https://flagma.cz/ru/vacancies/page-1/"
response = fetch_with_proxy(url, working_proxies)

if response:
    print("Успешный запрос:")
    print(response.text)
else:
    print("Не удалось получить данные после нескольких попыток.")