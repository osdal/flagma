import httpx

# Замените на свой адрес и порт прокси
proxy = "http://163.172.36.211:16001"

# Настройки клиента с прокси
client = httpx.Client(proxies={"http://": proxy, "https://": proxy})

try:
    response = client.get("https://flagma.cz/ru/vacancies/page-1/")
    response.raise_for_status()
    print(response.text)
except httpx.RequestError as exc:
    print(f"An error occurred while requesting {exc.request.url!r}.")
    print(f"Error details: {exc}")
