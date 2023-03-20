import psycopg2

def ls(message):
    conn = psycopg2.connect(host="localhost", port=5432, database="postgres", user="alechh", password="123")
    cur = conn.cursor()

    cur.execute("SELECT current_directory FROM user_directories WHERE user_id = %s", (message.from_user.id,))
    current_directory = cur.fetchall()[0]

    cur.execute("SELECT * FROM folders WHERE parent_folder_id = %s", (current_directory))
    folders = cur.fetchall()

    folders_answer = ''

    for folder in folders:
        folders_answer += folder[2] + ' '

    cur.execute("SELECT file_id FROM folder_files WHERE folder_id = %s", (current_directory))
    files = cur.fetchall()

    files_answer = ''

    for file in files:
        files_answer += file[2] + ' '

    conn.close()

    return folders_answer, files_answer


def cd(message):
    conn = psycopg2.connect(host="localhost", port=5432, database="postgres", user="alechh", password="123")
    cur = conn.cursor()

    new_folder_name = message.text.split(' ')[1]

    if (new_folder_name == '..'):
        cur.execute("SELECT current_directory FROM user_directories WHERE user_id = %s", (message.from_user.id,))
        current_directory = cur.fetchall()[0]

        cur.execute("SELECT parent_folder_id FROM folders WHERE folder_id = %s", (current_directory))
        parent_folder = cur.fetchall()[0]

        if parent_folder[0] == None:
            conn.close()
            return -3

        cur.execute("UPDATE user_directories SET current_directory = %s WHERE user_id = %s", (parent_folder, message.from_user.id))
        conn.commit()
        conn.close()
        return 0

    cur.execute("SELECT current_directory FROM user_directories WHERE user_id = %s", (message.from_user.id,))

    current_directory = cur.fetchall()[0]

    cur.execute("SELECT * FROM folders WHERE folder_name = %s and parent_folder_id = %s", (new_folder_name, current_directory))

    res = cur.fetchall()

    if len(res) == 0:
        conn.close()
        return -1
    elif len(res) == 1:
        cur.execute("UPDATE user_directories SET current_directory = %s WHERE user_id = %s", (res[0][0], message.from_user.id))
        conn.commit()
        conn.close()
        return 0
    else:
        conn.close()
        return -2
    
def mkdir(message):
    conn = psycopg2.connect(host="localhost", port=5432, database="postgres", user="alechh", password="123")
    cur = conn.cursor()

    new_folder_name = message.text.split(' ')[1]

    cur.execute("SELECT current_directory FROM user_directories WHERE user_id = %s", (message.from_user.id,))
    current_directory = cur.fetchall()[0]

    cur.execute("INSERT INTO folders (user_id, folder_name, parent_folder_id) VALUES (%s, %s, %s)", (message.from_user.id, new_folder_name, current_directory))

    conn.commit()
    conn.close()


def pwd(message):
    conn = psycopg2.connect(host="localhost", port=5432, database="postgres", user="alechh", password="123")
    cur = conn.cursor()

    cur.execute("SELECT current_directory FROM user_directories WHERE user_id = %s", (message.from_user.id,))
    current_directory = cur.fetchall()[0]

    cur.execute("SELECT * FROM folders WHERE folder_id = %s", (current_directory))
    res = cur.fetchall()
    res_tuple = res[0]
    
    current_directory_name = res_tuple[2]

    while res_tuple[3] != None:
        cur.execute("SELECT * FROM folders WHERE folder_id = %s", (res_tuple[3],))
        res = cur.fetchall()
        res_tuple = res[0]
        current_directory_name = res_tuple[2] + '/' + current_directory_name

    conn.close()

    return "/" + current_directory_name

def add_new_user(message):
    conn = psycopg2.connect(host="localhost", port=5432, database="postgres", user="alechh", password="123")
    cur = conn.cursor()

    # check if the user exists in table users
    cur.execute("SELECT * FROM users WHERE user_id = %s", (message.from_user.id,))

    # if not, add the user to the table
    if not cur.fetchone():
        cur.execute("INSERT INTO users (user_id, username) VALUES (%s, %s)", (message.from_user.id, message.from_user.username))
        conn.commit()
        conn.close()
        return 1
    else:
        conn.close()
        return 0
