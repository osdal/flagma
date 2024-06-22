from datetime import datetime
# Получить текущую дату и время
current_datetime = datetime.now()

# Преобразовать дату в строку
current_date = current_datetime.strftime("%Y-%m-%d-%H-%M")

file_name = 'DATA/logs/' + current_date + '.txt'

# Записываем строку в текстовый файл
with open(file_name, 'w', encoding='utf-8') as text_file:
    text_file.write('2222222222')