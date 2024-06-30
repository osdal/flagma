# Открываем файл для чтения
with open('DATA/links/vacancies_links.csv', 'r') as file:
    # Читаем все строки файла, убираем символы новой строки и сохраняем их в список
    lines = [line.strip() for line in file]
with open('DATA/links/vacancies_links-2024-06-29-07-45.csv', 'r') as file:
    # Читаем все строки файла, убираем символы новой строки и сохраняем их в список
    lines_new = [line.strip() for line in file]

# Выводим список строк
print(len(lines))
print(len(lines_new))

list1 = [1, 2, 3, 4, 5]
list2 = [4, 5, 6, 7, 8]

# Элементы, которые есть в list2, но нет в list1
difference = [item for item in list2 if item not in list1]
vacancies_diff = [item for item in lines_new if item not in lines]
print(difference)
print(len(vacancies_diff))

