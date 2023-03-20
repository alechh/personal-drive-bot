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
        if storage.check_user(message):
            answer = storage.pwd(message)
        else:
            answer = 'Вас нет в базе, пропишите /start'
    elif 'mkdir ' in message.text and len(message.text.split(' ')) == 2:
        if storage.check_user(message):
            storage.mkdir(message)
            answer = 'Создал папку'
        else:
            answer = 'Вас нет в базе, пропишите /start'
    elif 'cd ' in message.text and len(message.text.split(' ')) == 2:
        if storage.check_user(message):
            res = storage.  cd(message)
            if res == -1:
                answer = 'Нет такой папки'
            elif res == -2:
                answer = 'Несколько папок с таким именем'
            elif res == -3:
                answer = 'Вы находитесь в корневой папке'
            else:
                answer = 'Перешел в папку'
        else:
            answer = 'Вас нет в базе, пропишите /start'
    elif message.text == 'ls':
        if storage.check_user(message):
            folders_res, files_res = storage.ls(message)
            if folders_res == '':
                answer += 'Папок нет'
            else:
                answer += 'Папки: ' + folders_res

            if files_res == '':
                answer += '\nФайлов нет'
            else:
                answer += '\nФайлы: ' + files_res
        else:
            answer = 'Вас нет в базе, пропишите /start'


    bot.send_message(message.chat.id, answer)

@bot.message_handler(content_types=['document'])
def handle_document(message):
    # получаем информацию о файле
    file_info = bot.get_file(message.document.file_id)
    file_url = 'https://api.telegram.org/file/bot{}/{}'.format(bot.token, file_info.file_path)
    file_name = message.document.file_name

    if not storage.check_user(message):
        bot.send_message(message.chat.id, 'Вас нет в базе, пропишите /start')
        return

    # save file to database
    if storage.save_file(message, file_name, file_url) == 0:
        bot.send_message(message.chat.id, 'Файл успешно сохранен')


bot.polling(none_stop=True)
