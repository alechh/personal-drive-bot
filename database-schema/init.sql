-- Создание схемы для базы данных телеграм бота файлового хранилища

CREATE TABLE users (
  user_id INTEGER PRIMARY KEY,
  username VARCHAR(255)
);

CREATE TABLE files (
  file_id TEXT PRIMARY KEY,
  user_id INTEGER REFERENCES users(user_id) ON DELETE CASCADE,
  file_name VARCHAR(255),
  file_url VARCHAR(255)
);

CREATE TABLE folders (
  folder_id TEXT PRIMARY KEY,
  user_id INTEGER REFERENCES users(user_id) ON DELETE CASCADE,
  folder_name VARCHAR(255),
  parent_folder_id TEXT REFERENCES folders(folder_id) ON DELETE CASCADE
);

CREATE TABLE folder_files (
  folder_id TEXT REFERENCES folders(folder_id) ON DELETE CASCADE,
  file_id TEXT REFERENCES files(file_id) ON DELETE CASCADE
);

CREATE TABLE user_directories (
    user_id INTEGER REFERENCES users(user_id) ON DELETE CASCADE,
    current_directory TEXT REFERENCES folders(folder_id) ON DELETE CASCADE
);

CREATE OR REPLACE FUNCTION create_user_folder()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO folders (folder_id, user_id, folder_name, parent_folder_id)
  VALUES (NEW.user_id || '_home', NEW.user_id, 'home', NULL);

  INSERT INTO user_directories (user_id, current_directory)
  VALUES (NEW.user_id, (SELECT folder_id FROM folders WHERE user_id = NEW.user_id AND folder_name = 'home'));
  RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER insert_user_folder
AFTER INSERT ON users
FOR EACH ROW
WHEN (NEW.user_id IS NOT NULL)
EXECUTE FUNCTION create_user_folder();


