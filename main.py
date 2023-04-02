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
    answer = 'Что-то пошло не так...'

    if not storage.check_user(message):
        answer = 'Вас нет в базе, пропишите /start'
        bot.send_message(message.chat.id, answer)
        return
        
    if message.text == 'pwd':
        answer = storage.pwd(message)
    elif 'mkdir ' in message.text and len(message.text.split(' ')) == 2:
        if storage.mkdir(message) != -1:
            answer = 'Создал папку'
        else:
            answer = 'Папка с таким именем уже есть'
    elif 'cd ' in message.text and len(message.text.split(' ')) == 2:
        res = storage.cd(message)
        if res == -1:
            answer = 'Нет такой папки'
        elif res == -3:
            answer = 'Вы находитесь в корневой папке'
        else:
            answer = 'Перешел в папку'
    elif message.text == 'ls':
        folders_res, files_res = storage.ls(message)

        if folders_res != None or files_res != None:
            answer = ''

        if folders_res == '':
            answer += 'Папок нет'
        else:
            answer += 'Папки: ' + folders_res

        if files_res == '':
            answer += '\nФайлов нет'
        else:
            answer += '\nФайлы: ' + files_res
    elif 'rm ' in message.text and len(message.text.split(' ')) == 2:
        if storage.rm_file(message) != -1:
            answer = 'Удалил файл ' + message.text.split(' ')[1]
        elif storage.rm_folder(message) != -1:
            answer = 'Удалил папку ' + message.text.split(' ')[1]
        else:
            answer = 'Нет такого файла или папки для удаления'

    bot.send_message(message.chat.id, answer)

@bot.message_handler(content_types=['document'])
def handle_document(message):
    # получаем информацию о файле
    file_info = bot.get_file(message.document.file_id)
    file_url = 'https://api.telegram.org/file/bot{}/{}'.format(bot.token, file_info.file_path)
    file_name = message.document.file_name
    file_id = message.document.file_id

    if not storage.check_user(message):
        bot.send_message(message.chat.id, 'Вас нет в базе, пропишите /start')
        return

    # Save file to database
    if storage.save_file(message, file_id, file_name, file_url) == 0:
        bot.send_message(message.chat.id, 'Файл успешно сохранен')
    else:
        bot.send_message(message.chat.id, 'Такой файл уже есть')


bot.polling(none_stop=True)
