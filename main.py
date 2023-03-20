import telebot
from utils import storage
from decouple import config

bot = telebot.TeleBot(config('token'))

@bot.message_handler(commands=['start'])
def handle_start(message):
    res = storage.add_new_user(message)
    if res == 0:
       bot.send_message(message.chat.id, 'Привет, ты уже есть в базе')
    elif res == 1:
         bot.send_message(message.chat.id, 'Привет, добавил тебя в базу')  

@bot.message_handler(content_types=['text'])
def handle_text(message):
    answer = ''

    if message.text == 'pwd':
        answer = storage.pwd(message)
    elif 'mkdir ' in message.text and len(message.text.split(' ')) == 2:
        storage.mkdir(message)
        answer = 'Создал папку'
    elif 'cd ' in message.text and len(message.text.split(' ')) == 2:
        res = storage.cd(message)
        if res == -1:
            answer = 'Нет такой папки'
        elif res == -2:
            answer = 'Несколько папок с таким именем'
        elif res == -3:
            answer = 'Вы находитесь в корневой папке'
        else:
            answer = 'Перешел в папку'
    elif message.text == 'ls':
        res = storage.ls(message)

        if (len(res) == 0):
            answer = 'Папка пуста'
            return 0

        for i in res:
            answer += i[2] + ' '

    bot.send_message(message.chat.id, answer)

@bot.message_handler(content_types=['document'])
def handle_document(message):
    # получаем информацию о файле
    file_info = bot.get_file(message.document.file_id)
    file_url = 'https://api.telegram.org/file/bot{}/{}'.format(bot.token, file_info.file_path)
    file_name = message.document.file_name

    # выводим информацию на экран
    print('Получен файл:')
    print('Ссылка: {}'.format(file_url))
    print('Название файла: {}'.format(file_name))


bot.polling(none_stop=True)
