from utils.db_connector import DB_Connector
from decouple import config

def check_user(message):
    db = DB_Connector(config("db_host"), config("db_port"), config("db_user"), config("db_pass"), config("db_name"))

    # Check if user is in database
    res = db.execute("SELECT * FROM users WHERE user_id = %s", (message.from_user.id,))

    if len(res) == 0:
        return False
    
    return True

def ls(message):
    db = DB_Connector(config("db_host"), config("db_port"), config("db_user"), config("db_pass"), config("db_name"))

    # Get current directory
    res = db.execute("SELECT current_directory FROM user_directories WHERE user_id = %s", (message.from_user.id,))
    current_directory = res[0]

    # Get all folders in current directory
    folders = db.execute("SELECT * FROM folders WHERE parent_folder_id = %s", (current_directory))

    folders_answer = ''

    # Add all folders to answer
    for folder in folders:
        folders_answer += folder[2] + ' '

    # Get all files in current directory
    files = db.execute("SELECT file_id FROM folder_files WHERE folder_id = %s", (current_directory))

    files_answer = ''

    # Add all files to answer
    for file in files:
        # Get file name by file id
        res = db.execute("SELECT file_name FROM files WHERE file_id = %s", (file[0],))
        file_name = res[0][0]
        files_answer += file_name + ' '

    return folders_answer, files_answer


def cd(message):
    db = DB_Connector(config("db_host"), config("db_port"), config("db_user"), config("db_pass"), config("db_name"))

    new_folder_name = message.text.split(' ')[1]

    # Check if user wants to go to parent folder
    if (new_folder_name == '..'):
        # Get current directory
        res = db.execute("SELECT current_directory FROM user_directories WHERE user_id = %s", (message.from_user.id,))
        current_directory = res[0]

        # Get parent folder
        res = db.execute("SELECT parent_folder_id FROM folders WHERE folder_id = %s", (current_directory))
        parent_folder = res[0]

        # Check if parent folder exists
        if parent_folder[0] == None:
            return -3

        # Update current directory
        db.execute("UPDATE user_directories SET current_directory = %s WHERE user_id = %s", (parent_folder, message.from_user.id))
        return 0

    # Get current directory
    res = db.execute("SELECT current_directory FROM user_directories WHERE user_id = %s", (message.from_user.id,))
    current_directory = res[0]

    # Check if folder with the same name exists
    res = db.execute("SELECT * FROM folders WHERE folder_name = %s and parent_folder_id = %s", (new_folder_name, current_directory))

    if len(res) == 0:
        # Folder with the same name doesn't exist
        return -1
    elif len(res) == 1:
        # Update current directory
        db.execute("UPDATE user_directories SET current_directory = %s WHERE user_id = %s", (res[0][0], message.from_user.id))
        return 0
    
def mkdir(message):
    db = DB_Connector(config("db_host"), config("db_port"), config("db_user"), config("db_pass"), config("db_name"))

    new_folder_name = message.text.split(' ')[1]

    # Get current directory
    res = db.execute("SELECT current_directory FROM user_directories WHERE user_id = %s", (message.from_user.id,))
    current_directory = res[0][0]

    # Check if folder with the same name already exists
    res = db.execute("SELECT * FROM folders WHERE folder_name = %s and parent_folder_id = %s", (new_folder_name, current_directory))
    if len(res) != 0:
        return -1

    # Create folder_id as hash of user_id + current_directory + new_folder_name
    folder_id_str = str(message.from_user.id) + '_' + current_directory + '/' + new_folder_name
    folder_id = (str) (hash(folder_id_str))

    # Add new folder to database
    db.execute("INSERT INTO folders (folder_id, user_id, folder_name, parent_folder_id) VALUES (%s, %s, %s, %s)", (folder_id, message.from_user.id, new_folder_name, current_directory))


def pwd(message):
    db = DB_Connector(config("db_host"), config("db_port"), config("db_user"), config("db_pass"), config("db_name"))

    # Get current directory
    res = db.execute("SELECT current_directory FROM user_directories WHERE user_id = %s", (message.from_user.id,))
    current_directory = res[0]

    # Get folder_name of current directory
    res = db.execute("SELECT * FROM folders WHERE folder_id = %s", (current_directory))
    res_tuple = res[0]
    current_directory_name = res_tuple[2]

    # Get full folder path (res_tuple[3] -- parent_folder_id)
    while res_tuple[3] != None:
        # Get folder_name of parent folder
        res = db.execute("SELECT * FROM folders WHERE folder_id = %s", (res_tuple[3],))
        res_tuple = res[0]

        # Add parent folder name to current directory name
        current_directory_name = res_tuple[2] + '/' + current_directory_name

    return "/" + current_directory_name

def add_new_user(message):
    db = DB_Connector(config("db_host"), config("db_port"), config("db_user"), config("db_pass"), config("db_name"))

    # Check if the user exists in table users
    res = db.execute("SELECT * FROM users WHERE user_id = %s", (message.from_user.id,))

    # If not, add the user to the table
    if len(res) == 0:
        db.execute("INSERT INTO users (user_id, username) VALUES (%s, %s)", (message.from_user.id, message.from_user.username))
        return 1
    else:
        return 0
    
def save_file(message, file_id, file_name, file_url):
    db = DB_Connector(config("db_host"), config("db_port"), config("db_user"), config("db_pass"), config("db_name"))

    # Get current directory
    res = db.execute("SELECT current_directory FROM user_directories WHERE user_id = %s", (message.from_user.id,))
    current_directory = res[0]

    # Check if file with the same name already exists in the current directory
    res = db.execute("SELECT * FROM folder_files WHERE folder_id = %s", (current_directory,))
    for file in res:
        res2 = db.execute("SELECT * FROM files WHERE file_id = %s", (file[1],))
        if res2[0][2] == file_name:
            return -1
    
    # Add file to table files
    db.execute("INSERT INTO files (file_id, user_id, file_name, file_url) VALUES (%s, %s, %s, %s)", (file_id, message.from_user.id, file_name, file_url))

    # Add file to table folder_files
    db.execute("INSERT INTO folder_files (folder_id, file_id) VALUES (%s, %s)", (current_directory, file_id))

    return 0

def rm_file(message):
    db = DB_Connector(config("db_host"), config("db_port"), config("db_user"), config("db_pass"), config("db_name"))

    file_name = message.text.split(' ')[1]

    # Get current directory
    res = db.execute("SELECT current_directory FROM user_directories WHERE user_id = %s", (message.from_user.id,))
    current_directory = res[0]

    # Get all files in current directory
    files_in_current_dir = db.execute("SELECT file_id FROM folder_files WHERE folder_id = %s", (current_directory,))

    res = db.execute("SELECT file_id FROM files WHERE file_name = %s AND user_id = %s", (file_name, message.from_user.id))
    if len(res) == 0:
        return -1
    
    found = False
    curr_index = 0
    
    file_id = res[curr_index]

    # Try to find file_id in files_in_current_dir
    while file_id not in files_in_current_dir and curr_index < len(res):
        curr_index += 1
        file_id = res[curr_index]
    else:
        if curr_index < len(res):
            found = True
    
    # If found, delete file from table files and table folder_files
    if found:
        db.execute("DELETE FROM folder_files WHERE folder_id = %s and file_id = %s", (current_directory, file_id))
        db.execute("DELETE FROM files WHERE file_id = %s AND user_id = %s", (file_id, message.from_user.id))
    return 0

def rm_folder(message):
    db = DB_Connector(config("db_host"), config("db_port"), config("db_user"), config("db_pass"), config("db_name"))

    folder_name = message.text.split(' ')[1]

    # Get current directory
    res = db.execute("SELECT current_directory FROM user_directories WHERE user_id = %s", (message.from_user.id,))
    current_directory = res[0]

    # Get folder_id of folder to delete
    res = db.execute("SELECT folder_id FROM folders WHERE folder_name = %s and parent_folder_id = %s", (folder_name, current_directory))
    if len(res) == 0:
        return -1
    
    folder_id = res[0]

    # Check if folder contains files
    res = db.execute("SELECT * FROM folder_files WHERE folder_id = %s", (folder_id,))
    if len(res) != 0:
        return -2
    
    # Check if folder contains other folders
    res = db.execute("SELECT * FROM folders WHERE parent_folder_id = %s", (folder_id,))
    if len(res) != 0:
        return -2

    # Delete folder from table folders
    db.execute("DELETE FROM folders WHERE folder_id = %s", (folder_id))

    return 0

def get_file_id(message):
    db = DB_Connector(config("db_host"), config("db_port"), config("db_user"), config("db_pass"), config("db_name"))

    file_name = message.text.split('/')[1]

    # Get current directory
    res = db.execute("SELECT current_directory FROM user_directories WHERE user_id = %s", (message.from_user.id,))
    current_directory = res[0]

    # Get all files in current directory
    files_in_current_dir = db.execute("SELECT file_id FROM folder_files WHERE folder_id = %s", (current_directory,))

    res = db.execute("SELECT file_id FROM files WHERE file_name = %s AND user_id = %s", (file_name, message.from_user.id))
    if len(res) == 0:
        return -1
    
    found = False
    curr_index = 0

    file_id = res[curr_index]

    # Try to find file_id in files_in_current_dir
    while file_id not in files_in_current_dir and curr_index < len(res):
        curr_index += 1
        file_id = res[curr_index]
    else:
        if curr_index < len(res):
            found = True
    
    # If found, return file_url
    if found:
        return file_id[0]
    
    return 0

def rm_folder_minus_r(message):
    db = DB_Connector(config("db_host"), config("db_port"), config("db_user"), config("db_pass"), config("db_name"))

    folder_name = message.text.split(' ')[2]

    # Get current directory
    res = db.execute("SELECT current_directory FROM user_directories WHERE user_id = %s", (message.from_user.id,))
    current_directory = res[0]

    # Get folder_id of folder to delete
    res = db.execute("SELECT folder_id FROM folders WHERE folder_name = %s and parent_folder_id = %s", (folder_name, current_directory))
    if len(res) == 0:
        return -1
    
    target_folder_id = res[0]

    # Delete all subfolders from table folders
    subfolders = db.execute("SELECT folder_id FROM folders WHERE parent_folder_id = %s", (target_folder_id,))

    # Check if subfolder contains files, if so, return -2
    for subfolder in subfolders:
        res_files = db.execute("SELECT * FROM folder_files WHERE folder_id = %s", (subfolder[0],))
        if len(res_files) != 0:
            return -2
    
    # Subfolders do not contain files, delete them
    for subfolder in subfolders:
        db.execute("DELETE FROM folders WHERE folder_id = %s", (subfolder[0],))

    # Delete all files in target folder
    files = db.execute("SELECT file_id FROM folder_files WHERE folder_id = %s", (target_folder_id,))
    for file in files:
        db.execute("DELETE FROM files WHERE file_id = %s", (file[0],))

    # Delete target folder from table folders
    db.execute("DELETE FROM folders WHERE folder_id = %s", target_folder_id)

    return 0

def mv(message):
    db = DB_Connector(config("db_host"), config("db_port"), config("db_user"), config("db_pass"), config("db_name"))

    file_name = message.text.split(' ')[1]
    target_folder_name = message.text.split(' ')[2]

    # Get current directory
    res = db.execute("SELECT current_directory FROM user_directories WHERE user_id = %s", (message.from_user.id,))
    current_directory = res[0]

    # Get all files in current directory
    files_in_current_dir = db.execute("SELECT file_id FROM folder_files WHERE folder_id = %s", (current_directory,))
    files_in_current_dir = [file[0] for file in files_in_current_dir]

    res = db.execute("SELECT file_id FROM files WHERE file_name = %s AND user_id = %s", (file_name, message.from_user.id))
    if len(res) == 0:
        # File does not exist, lets check if it is a folder
        res = db.execute("SELECT folder_id FROM folders WHERE folder_name = %s AND parent_folder_id = %s", (file_name, current_directory))
        if len(res) == 0:
            return -1
        else:
            target_folder_id = res[0]
            # It is a folder, lets check if target folder exists
            if target_folder_name == '..':
                res = db.execute("SELECT parent_folder_id FROM folders WHERE folder_id = %s", (current_directory,))
                if res[0][0] == None:
                    return -3
            else:
                res = db.execute("SELECT folder_id FROM folders WHERE folder_name = %s AND parent_folder_id = %s", (target_folder_name, current_directory))
                if len(res) == 0:
                    return -2
            # Target folder exists, lets move folder

            db.execute("UPDATE folders SET parent_folder_id = %s WHERE folder_id = %s", (res[0], target_folder_id))
            return 1
    
    # File exists, lets check if it is in current directory
    found = False
    curr_index = 0

    file_id = res[curr_index]

    # Try to find file_id in files_in_current_dir
    while file_id[0] not in files_in_current_dir and curr_index < len(res):
        curr_index += 1
        file_id = res[curr_index]
    else:
        if curr_index < len(res):
            found = True
    
    if not found:
        return -1

    # If found, check if target folder exists
    if target_folder_name == '..':
        res = db.execute("SELECT parent_folder_id FROM folders WHERE folder_id = %s", (current_directory,))
        if res[0][0] == None:
            return -3
    else:
        res = db.execute("SELECT folder_id FROM folders WHERE folder_name = %s AND parent_folder_id = %s", (target_folder_name, current_directory))
        if len(res) == 0:
            return -2
        
    target_folder_id = res[0]
    db.execute("INSERT INTO folder_files (folder_id, file_id) VALUES (%s, %s)", (target_folder_id, file_id))
    db.execute("DELETE FROM folder_files WHERE folder_id = %s AND file_id = %s", (current_directory, file_id))
    return 0
