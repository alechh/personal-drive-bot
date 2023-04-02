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
            answer = 'Перешел в папку ' + storage.pwd(message)

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

    elif 'rm ' in message.text and len(message.text.split(' ')) > 1 and len(message.text.split(' ')) < 4:
        # First check if it's a file
        if storage.rm_file(message) != -1:
            answer = 'Удалил файл ' + message.text.split(' ')[1]
            bot.send_message(message.chat.id, answer)
            return
        
        # If it's not a file, check if it's a folder

        # Check if it's a rm command with -r flag
        if ' -r ' in message.text:
            rm_folder_res = storage.rm_folder_minus_r(message)

            if rm_folder_res == 0:
                answer = 'Удалил папку ' + message.text.split(' ')[2] + ' вместе с содержимым'
            elif rm_folder_res == -1:
                answer = 'Нет такого файла или папки для удаления'
            elif rm_folder_res == -2:
                answer = 'Папка не пуста и имеет вложенные папки, сначала удалите их'
        else:
            rm_folder_res = storage.rm_folder(message)

            if rm_folder_res == 0:
                answer = 'Удалил папку ' + message.text.split(' ')[1]
            elif rm_folder_res == -2:
                answer = 'Папка не пуста, чтобы удалить её вместе с содержимым, пропишите rm -r'
            else:
                answer = 'Нет такого файла или папки для удаления'

    elif './' in message.text:
        file_id = storage.get_file_id(message)
        if file_id != 0 and file_id != -1:
            bot.send_document(message.chat.id, file_id, reply_to_message_id=message.message_id)
            return
        else:
            answer = 'Нет такого файла'
        
    bot.send_message(message.chat.id, answer)

@bot.message_handler(content_types=['document'])
def handle_document(message):
    # Get file id, file name and file url
    file_info = bot.get_file(message.document.file_id)
    file_url = 'https://api.telegram.org/file/bot{}/{}'.format(bot.token, file_info.file_path)
    
    file_name = message.document.file_name
    file_name = file_name.replace(' ', '_')

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
