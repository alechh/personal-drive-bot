from utils.db_connector import DB_Connector
from decouple import config

def check_user(message):
    db = DB_Connector(config("db_host"), config("db_port"), config("db_user"), config("db_pass"), config("db_name"))

    res = db.execute("SELECT * FROM users WHERE user_id = %s", (message.from_user.id,))

    if len(res) == 0:
        return False
    else:
        return True

def ls(message):
    db = DB_Connector(config("db_host"), config("db_port"), config("db_user"), config("db_pass"), config("db_name"))

    res = db.execute("SELECT current_directory FROM user_directories WHERE user_id = %s", (message.from_user.id,))

    current_directory = res[0]

    folders = db.execute("SELECT * FROM folders WHERE parent_folder_id = %s", (current_directory))

    folders_answer = ''

    for folder in folders:
        folders_answer += folder[2] + ' '

    files = db.execute("SELECT file_id FROM folder_files WHERE folder_id = %s", (current_directory))

    files_answer = ''

    for file in files:
        res = db.execute("SELECT file_name FROM files WHERE file_id = %s", (file[0],))
        file_name = res[0][0]
        files_answer += file_name + ' '

    return folders_answer, files_answer


def cd(message):
    db = DB_Connector(config("db_host"), config("db_port"), config("db_user"), config("db_pass"), config("db_name"))

    new_folder_name = message.text.split(' ')[1]

    if (new_folder_name == '..'):
        res = db.execute("SELECT current_directory FROM user_directories WHERE user_id = %s", (message.from_user.id,))
        current_directory = res[0]

        res = db.execute("SELECT parent_folder_id FROM folders WHERE folder_id = %s", (current_directory))
        parent_folder = res[0]

        if parent_folder[0] == None:
            return -3

        db.execute("UPDATE user_directories SET current_directory = %s WHERE user_id = %s", (parent_folder, message.from_user.id))
        return 0

    res = db.execute("SELECT current_directory FROM user_directories WHERE user_id = %s", (message.from_user.id,))

    current_directory = res[0]

    res = db.execute("SELECT * FROM folders WHERE folder_name = %s and parent_folder_id = %s", (new_folder_name, current_directory))

    if len(res) == 0:
        return -1
    elif len(res) == 1:
        db.execute("UPDATE user_directories SET current_directory = %s WHERE user_id = %s", (res[0][0], message.from_user.id))
        return 0
    else:
        return -2
    
def mkdir(message):
    db = DB_Connector(config("db_host"), config("db_port"), config("db_user"), config("db_pass"), config("db_name"))

    new_folder_name = message.text.split(' ')[1]

    res = db.execute("SELECT current_directory FROM user_directories WHERE user_id = %s", (message.from_user.id,))
    current_directory = res[0][0]

    folder_id = (str) (hash((str) (message.from_user.id) + new_folder_name + current_directory))

    db.execute("INSERT INTO folders (folder_id, user_id, folder_name, parent_folder_id) VALUES (%s, %s, %s, %s)", (folder_id, message.from_user.id, new_folder_name, current_directory))


def pwd(message):
    db = DB_Connector(config("db_host"), config("db_port"), config("db_user"), config("db_pass"), config("db_name"))

    res = db.execute("SELECT current_directory FROM user_directories WHERE user_id = %s", (message.from_user.id,))
    current_directory = res[0]

    res = db.execute("SELECT * FROM folders WHERE folder_id = %s", (current_directory))
    res_tuple = res[0]
    
    current_directory_name = res_tuple[2]

    while res_tuple[3] != None:
        res = db.execute("SELECT * FROM folders WHERE folder_id = %s", (res_tuple[3],))
        res_tuple = res[0]
        current_directory_name = res_tuple[2] + '/' + current_directory_name

    return "/" + current_directory_name

def add_new_user(message):
    db = DB_Connector(config("db_host"), config("db_port"), config("db_user"), config("db_pass"), config("db_name"))

    # check if the user exists in table users
    res = db.execute("SELECT * FROM users WHERE user_id = %s", (message.from_user.id,))

    # if not, add the user to the table
    if len(res) == 0:
        db.execute("INSERT INTO users (user_id, username) VALUES (%s, %s)", (message.from_user.id, message.from_user.username))
        return 1
    else:
        return 0
    
def save_file(message, file_id, file_name, file_url):
    db = DB_Connector(config("db_host"), config("db_port"), config("db_user"), config("db_pass"), config("db_name"))

    res = db.execute("SELECT current_directory FROM user_directories WHERE user_id = %s", (message.from_user.id,))
    current_directory = res[0]

    db.execute("INSERT INTO files (file_id, user_id, file_name, file_url) VALUES (%s, %s, %s, %s)", (file_id, message.from_user.id, file_name, file_url))

    db.execute("INSERT INTO folder_files (folder_id, file_id) VALUES (%s, %s)", (current_directory, file_id))

    return 0

def rm_file(message):
    db = DB_Connector(config("db_host"), config("db_port"), config("db_user"), config("db_pass"), config("db_name"))

    file_name = message.text.split(' ')[1]

    res = db.execute("SELECT current_directory FROM user_directories WHERE user_id = %s", (message.from_user.id,))
    current_directory = res[0]

    files_in_current_dir = db.execute ("SELECT file_id FROM folder_files WHERE folder_id = %s", (current_directory,))

    res = db.execute("SELECT file_id FROM files WHERE file_name = %s AND user_id = %s", (file_name, message.from_user.id))
    if len(res) == 0:
        return -1
    
    file_id = res[0]

    if file_id not in files_in_current_dir:
        return -1

    db.execute("DELETE FROM folder_files WHERE folder_id = %s and file_id = %s", (current_directory, file_id))
    db.execute("DELETE FROM files WHERE file_id = %s AND user_id = %s", (file_id, message.from_user.id))
    return 0

def rm_folder(message):
    db = DB_Connector(config("db_host"), config("db_port"), config("db_user"), config("db_pass"), config("db_name"))

    folder_name = message.text.split(' ')[1]

    res = db.execute("SELECT current_directory FROM user_directories WHERE user_id = %s", (message.from_user.id,))
    current_directory = res[0]

    res = db.execute("SELECT folder_id FROM folders WHERE folder_name = %s and parent_folder_id = %s", (folder_name, current_directory))
    folder_id = ''
    try:
        folder_id = res[0]
    except:
        return -1

    db.execute("DELETE FROM folders WHERE folder_id = %s", (folder_id))

    return 0