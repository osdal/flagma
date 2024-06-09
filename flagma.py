import requests
from bs4 import BeautifulSoup as bs

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                  'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36'
}

response = requests.get('https://flagma.cz/ru/vacancies/page-1/')
html = response.text
# print(response.status_code)
response.encoding = 'utf-8'
soup = bs(html, "html.parser")

data_ad = {}
data_ads = soup.findAll('div', 'header job')
for name_ad in data_ads:
    job_name = name_ad.find('h2').text

for limk_ad in data_ads:
    link = limk_ad.find('a')['href']

for i in range(len(data_ads)):
    data_ad = {
        'title': job_name,
        'link': link,
    }
    data_ads[i] = data_ad
print(data_ads)
# print(len(data_ads))
