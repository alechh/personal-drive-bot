import telebot
from utils import storage
from decouple import config
import os

bot = telebot.TeleBot(config('token'))
BOT_VERSION = '1.0.0'

@bot.message_handler(commands=['start'])
def handle_start(message):
    res = storage.add_new_user(message)
    if res == 0:
        bot.send_message(message.chat.id, 'Привет, ты уже есть в базе')
    elif res == 1:
        bot.send_message(message.chat.id, 'Привет, добавил тебя в базу')

@bot.message_handler(commands=['version'])
def version(message):
    bot.send_message(message.chat.id, 'Текущая версия бота: ' + BOT_VERSION)

@bot.message_handler(commands=['help'])
def send_help(message):
    answer = """
/start - Старт бота \n\
/help - Список команд \n\
/backup - Создать бэкап \n\
/restore - Восстановиться из бэкапа \n\n\
pwd - Показать текущую директорию \n\
ls - Показать содержимое текущей директории \n\
cd dir - Перейти в директорию \n\
mkdir dir - Создать директорию \n\
rm file_or_dir- Удалить файл \n\
./file - Получить файл"""

    bot.send_message(message.chat.id, answer)

@bot.message_handler(commands=['stat'])
def stat(message):
    if not storage.check_user(message):
        answer = 'Вас нет в базе, пропишите /start'
        bot.send_message(message.chat.id, answer)
        return

    number_of_files = storage.stat(message)
    bot.reply_to(message, "Количество файлов: " + str(number_of_files))

@bot.message_handler(commands=['backup'])
def handle_backup(message):
    if not storage.check_user(message):
        answer = 'Вас нет в базе, пропишите /start'
        bot.send_message(message.chat.id, answer)
        return

    # Create folder for backups if it doesn't exist
    if not os.path.exists('backup'):
        os.mkdir('backup')
    else:
        # Delete old backups
        for file in os.listdir('backup'):
            os.remove(os.path.join('backup', file))

    backup_path = storage.create_backup()

    # Send backup file
    with open(backup_path, 'rb') as backup_file:
        bot.send_document(message.chat.id, backup_file, caption="Архив с бэкапом")

    # Remove backup file
    os.remove(backup_path)

    # Remove backups
    for file in os.listdir('backup'):
        os.remove(os.path.join('backup', file))

@bot.message_handler(commands=['restore'])
def handle_restore(message):
    if not storage.check_user(message):
        answer = 'Вас нет в базе, пропишите /start'
        bot.send_message(message.chat.id, answer)
        return

    bot.send_message(message.chat.id, 'Пришлите архив с бэкапом')
    bot.register_next_step_handler(message, restore)

def restore(message):
    if message.document:
        # Download backup file
        file_info = bot.get_file(message.document.file_id)
        backup_file = bot.download_file(file_info.file_path)

        # Save backup file to disk
        backup_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), message.document.file_name)
        with open(backup_path, 'wb') as f:
            f.write(backup_file)

        # Restore backup
        try:
            storage.restore_backup(backup_path, message.from_user.id)
            bot.reply_to(message, "Данные успешно восстановлены")
        except Exception as e:
            bot.reply_to(message, f"Ошибка восстановления данных: {e}")

        # Remove backup file
        os.remove(backup_path)
    else:
        bot.reply_to(message, "Это не файл, попробуйте еще раз /restore")



@bot.message_handler(content_types=['text'])
def handle_text(message):
    answer = 'Неизвестная команда'

    if not storage.check_user(message):
        answer = 'Вас нет в базе, пропишите /start'
        bot.send_message(message.chat.id, answer)
        return

    if message.text == 'pwd':
        answer = storage.pwd(message)

    elif 'mkdir ' in message.text and len(message.text.split(' ')) == 2:
        mkdir_res = storage.mkdir(message)
        if mkdir_res == -1:
            answer = 'Папка с таким именем уже есть'
        elif mkdir_res == -2:
            answer = 'В текущей директории есть файл с таким именем'
        else:
            answer = 'Создал папку'

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
            answer = storage.pwd(message) + '\n\n'

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

    elif 'mv ' in message.text and len(message.text.split(' ')) == 3:
        mv_res = storage.mv(message)
        
        if mv_res == -3:
            answer = 'Вы находитесь в корневой папке'
        if mv_res == -2:
            answer = 'Нет такой папки внутри текущей папки (пока перемещать можно только внутри текущей папки)'
        elif mv_res == -1:
            answer = 'Нет такого файла или папки'
        elif mv_res == 0:
            answer = 'Переместил файл {} в папку {}'.format(message.text.split(' ')[1], message.text.split(' ')[2])
        elif mv_res == 1:
            answer = 'Переместил папку {} в папку {}'.format(message.text.split(' ')[1], message.text.split(' ')[2])

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
    save_res = storage.save_file(message, file_id, file_name, file_url)
    if save_res == -1:
        bot.send_message(message.chat.id, 'Такой файл уже есть')
    elif save_res == -2:
        bot.send_message(message.chat.id, 'В текущей директории есть папка с таким именем')
    else:
        bot.send_message(message.chat.id, 'Файл успешно сохранен')


bot.polling(none_stop=True)
