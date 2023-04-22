from utils.db_connector import DB_Connector
from decouple import config
import tempfile
import shutil
import zipfile
import os

def check_user(message):
    db = DB_Connector(config("db_host"), config("db_port"), config("db_user"), config("db_pass"), config("db_name"))

    # Check if user is in database
    res = db.execute("SELECT * FROM users WHERE user_id = %s", (message.from_user.id,))

    if len(res) == 0:
        return False
    
    return True

def get_current_directory(db, user_id):
    res = db.execute("SELECT current_directory FROM user_directories WHERE user_id = %s", (user_id,))
    return res[0]

def get_folders_in_directory(db, directory_id):
    return db.execute("SELECT * FROM folders WHERE parent_folder_id = %s", (directory_id,))

def get_files_in_directory(db, directory_id):
    return db.execute("SELECT file_id FROM folder_files WHERE folder_id = %s", (directory_id,))

def get_file_name_by_id(db, file_id):
    return db.execute("SELECT file_name FROM files WHERE file_id = %s", (file_id,))

def get_parent_folder_id(db, folder_id):
    return db.execute("SELECT parent_folder_id FROM folders WHERE folder_id = %s", (folder_id,))

def update_current_directory(db, directory_id, user_id):
    db.execute("UPDATE user_directories SET current_directory = %s WHERE user_id = %s", (directory_id, user_id))

def get_folders_by_name_and_parent(db, folder_name, parent_directory):
    return db.execute("SELECT * FROM folders WHERE folder_name = %s and parent_folder_id = %s", (folder_name, parent_directory))

def get_folder_name_by_id(db, folder_id):
    res = db.execute("SELECT * FROM folders WHERE folder_id = %s", (folder_id,))
    return res[0]

def get_folder_id_by_name_and_parent(db, folder_name, parent_directory):
    return db.execute("SELECT folder_id FROM folders WHERE folder_name = %s and parent_folder_id = %s", (folder_name, parent_directory))

def get_folder_files_by_folder_id(db, folder_id):
    return db.execute("SELECT * FROM folder_files WHERE folder_id = %s", (folder_id,))

def get_file_id_by_name(db, file_name, user_id):
    return db.execute("SELECT file_id FROM files WHERE file_name = %s AND user_id = %s", (file_name, user_id))

def ls(message):
    db = DB_Connector(config("db_host"), config("db_port"), config("db_user"), config("db_pass"), config("db_name"))

    # Get current directory
    current_directory = get_current_directory(db, message.from_user.id)

    # Get all folders in current directory
    folders = get_folders_in_directory(db, current_directory)

    folders_answer = ''

    # Add all folders to answer
    for folder in folders:
        folders_answer += folder[2] + ' '

    # Get all files in current directory
    files = get_files_in_directory(db, current_directory)

    files_answer = ''

    # Add all files to answer
    for file in files:
        # Get file name by file id
        res = get_file_name_by_id(db, file[0])
        file_name = res[0][0]
        files_answer += file_name + ' '

    return folders_answer, files_answer


def cd(message):
    db = DB_Connector(config("db_host"), config("db_port"), config("db_user"), config("db_pass"), config("db_name"))

    new_folder_name = message.text.split(' ')[1]

    # Check if user wants to go to parent folder
    if (new_folder_name == '..'):
        # Get current directory
        current_directory = get_current_directory(db, message.from_user.id)

        # Get parent folder
        res = get_parent_folder_id(db, current_directory)
        parent_folder = res[0]

        # Check if parent folder exists
        if parent_folder[0] == None:
            return -3

        # Update current directory
        update_current_directory(db, parent_folder, message.from_user.id)
        return 0

    # Get current directory
    current_directory = get_current_directory(db, message.from_user.id)

    # Check if folder with the same name exists
    res = get_folders_by_name_and_parent(db, new_folder_name, current_directory)

    if len(res) == 0:
        # Folder with the same name doesn't exist
        return -1
    elif len(res) == 1:
        # Update current directory
        update_current_directory(db, res[0][0], message.from_user.id)
        return 0
    
def mkdir(message):
    db = DB_Connector(config("db_host"), config("db_port"), config("db_user"), config("db_pass"), config("db_name"))

    new_folder_name = message.text.split(' ')[1]

    # Get current directory
    current_directory = get_current_directory(db, message.from_user.id)[0]

    # Check if folder with the same name already exists
    res = get_folders_by_name_and_parent(db, new_folder_name, current_directory)
    if len(res) != 0:
        return -1
    
    # Check if file with the same name already exists
    res = get_files_in_directory(db, current_directory)
    for file in res:
        # Get file name by file id
        res = get_file_name_by_id(db, file[0])
        file_name = res[0][0]
        if file_name == new_folder_name:
            return -2

    # Create folder_id as hash of user_id + current_directory + new_folder_name
    folder_id_str = str(message.from_user.id) + '_' + current_directory + '/' + new_folder_name
    folder_id = (str) (hash(folder_id_str))

    # Add new folder to database
    db.execute("INSERT INTO folders (folder_id, user_id, folder_name, parent_folder_id) VALUES (%s, %s, %s, %s)", (folder_id, message.from_user.id, new_folder_name, current_directory))


def pwd(message):
    db = DB_Connector(config("db_host"), config("db_port"), config("db_user"), config("db_pass"), config("db_name"))

    # Get current directory
    current_directory = get_current_directory(db, message.from_user.id)

    # Get folder_name of current directory
    res_tuple = get_folder_name_by_id(db, current_directory)
    current_directory_name = res_tuple[2]

    # Get full folder path (res_tuple[3] -- parent_folder_id)
    while res_tuple[3] != None:
        # Get folder_name of parent folder
        res_tuple = get_folder_name_by_id(db, res_tuple[3])

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
    current_directory = get_current_directory(db, message.from_user.id)

    # Check if file with the same name already exists in the current directory
    res = get_folder_files_by_folder_id(db, current_directory)
    for file in res:
        res2 = db.execute("SELECT * FROM files WHERE file_id = %s", (file[1],))
        if res2[0][2] == file_name:
            return -1
        
    # Check if folder with the same name already exists in the current directory
    folders = get_folders_in_directory(db, current_directory)
    for folder in folders:
        if folder[2] == file_name:
            return -2
    
    # Add file to table files
    db.execute("INSERT INTO files (file_id, user_id, file_name, file_url) VALUES (%s, %s, %s, %s)", (file_id, message.from_user.id, file_name, file_url))

    # Add file to table folder_files
    db.execute("INSERT INTO folder_files (folder_id, file_id) VALUES (%s, %s)", (current_directory, file_id))

    return 0

def rm_file(message):
    db = DB_Connector(config("db_host"), config("db_port"), config("db_user"), config("db_pass"), config("db_name"))

    file_name = message.text.split(' ')[1]

    # Get current directory
    current_directory = get_current_directory(db, message.from_user.id)

    # Get all files in current directory
    files_in_current_dir = get_files_in_directory(db, current_directory)

    res = get_file_id_by_name(db, file_name, message.from_user.id)
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
    current_directory = get_current_directory(db, message.from_user.id)

    # Get folder_id of folder to delete
    res = get_folder_id_by_name_and_parent(db, folder_name, current_directory)
    if len(res) == 0:
        return -1
    
    folder_id = res[0]

    # Check if folder contains files
    res = get_folder_files_by_folder_id(db, folder_id)
    if len(res) != 0:
        return -2
    
    # Check if folder contains other folders
    res = get_folders_in_directory(db, folder_id)
    if len(res) != 0:
        return -2

    # Delete folder from table folders
    db.execute("DELETE FROM folders WHERE folder_id = %s", (folder_id))

    return 0

def get_file_id(message):
    db = DB_Connector(config("db_host"), config("db_port"), config("db_user"), config("db_pass"), config("db_name"))

    file_name = message.text.split('/')[1]

    # Get current directory
    current_directory = get_current_directory(db, message.from_user.id)

    # Get all files in current directory
    files_in_current_dir = get_files_in_directory(db, current_directory)

    res = get_file_id_by_name(db, file_name, message.from_user.id)
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
    current_directory = get_current_directory(db, message.from_user.id)

    # Get folder_id of folder to delete
    res = get_folder_id_by_name_and_parent(db, folder_name, current_directory)
    if len(res) == 0:
        return -1
    
    target_folder_id = res[0]

    # Delete all subfolders from table folders
    subfolders = db.execute("SELECT folder_id FROM folders WHERE parent_folder_id = %s", (target_folder_id,))

    # Check if subfolder contains files, if so, return -2
    for subfolder in subfolders:
        res_files = get_folder_files_by_folder_id(db, subfolder[0])
        if len(res_files) != 0:
            return -2
    
    # Subfolders do not contain files, delete them
    for subfolder in subfolders:
        db.execute("DELETE FROM folders WHERE folder_id = %s", (subfolder[0],))

    # Delete all files in target folder
    files = get_files_in_directory(db, target_folder_id)
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
    current_directory = get_current_directory(db, message.from_user.id)

    # Get all files in current directory
    files_in_current_dir = get_files_in_directory(db, current_directory)
    files_in_current_dir = [file[0] for file in files_in_current_dir]

    res = get_file_id_by_name(db, file_name, message.from_user.id)
    if len(res) == 0:
        # File does not exist, lets check if it is a folder
        res = get_folder_id_by_name_and_parent(db, file_name, current_directory)
        if len(res) == 0:
            return -1
        else:
            target_folder_id = res[0]
            # It is a folder, lets check if target folder exists
            if target_folder_name == '..':
                res = get_parent_folder_id(db, current_directory)
                if res[0][0] == None:
                    return -3
            else:
                res = get_folder_id_by_name_and_parent(db, target_folder_name, current_directory)
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
        res = get_parent_folder_id(db, current_directory)
        if res[0][0] == None:
            return -3
    else:
        res = get_folder_id_by_name_and_parent(db, target_folder_name, current_directory)
        if len(res) == 0:
            return -2
        
    target_folder_id = res[0]
    db.execute("INSERT INTO folder_files (folder_id, file_id) VALUES (%s, %s)", (target_folder_id, file_id))
    db.execute("DELETE FROM folder_files WHERE folder_id = %s AND file_id = %s", (current_directory, file_id))
    return 0

def create_backup():
    db = DB_Connector(config("db_host"), config("db_port"), config("db_user"), config("db_pass"), config("db_name"))
    backup_dir = './backup'

    tables_to_backup = ['files', 'folders', 'folder_files']
    
    for table in tables_to_backup:
        with tempfile.NamedTemporaryFile(mode='wb', delete=False, dir=backup_dir, prefix=f'{table}_', suffix='.csv') as backup_file:
            db.make_backup(f"COPY {table} TO STDOUT WITH (FORMAT csv, HEADER true, DELIMITER ',', QUOTE '\"', ESCAPE '\\', NULL 'null')", backup_file)

        backup_archive = shutil.make_archive(backup_dir, 'zip', root_dir=backup_dir)
    return backup_archive

def restore_backup(backup_path, user_id):
    db = DB_Connector(config("db_host"), config("db_port"), config("db_user"), config("db_pass"), config("db_name"))

    # Extract backup to temporary directory
    with tempfile.TemporaryDirectory(dir='./backup') as temp_dir:
        with zipfile.ZipFile(backup_path, 'r') as backup_zip:
            backup_zip.extractall(temp_dir)

        # temp_dir += '/backup'

        # Retrieve all backup files
        backup_files = [f for f in os.listdir(temp_dir) if f.endswith('.csv')]

        # Make folder_files last (because it depends on folders and files)
        backup_files = sorted(backup_files, key=lambda x: x.split('_')[0] == 'folder')

        # Restore data from backup files
        for backup_file in backup_files:
            table_name = os.path.splitext(backup_file)[0].split('_')[0]

            # Dirty hack to fix folder_files table name
            if table_name == 'folder':
                table_name = 'folder_files'

            backup_file_path = os.path.join(temp_dir, backup_file)

            # Clean table before restoring data
            db.execute(f"TRUNCATE {table_name} RESTART IDENTITY CASCADE")

            # Restore data from backup file
            with open(backup_file_path, 'r') as f:
                db.restore_backup(f"COPY {table_name} FROM STDIN WITH (FORMAT csv, HEADER true, DELIMITER ',', QUOTE '\"', NULL 'null')", f)

        # Set current directory to root
        db.execute("INSERT INTO user_directories (user_id, current_directory) VALUES (%s, %s)", (user_id, str(user_id) + '_home'))

def stat(message):
    db = DB_Connector(config("db_host"), config("db_port"), config("db_user"), config("db_pass"), config("db_name"))

    res = db.execute("SELECT count(*) FROM files WHERE user_id = %s", (message.from_user.id,))
    return res[0][0]
