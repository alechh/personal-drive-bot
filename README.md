[![CI/CD Pipeline](https://github.com/alechh/personal-drive-bot/actions/workflows/tests.yml/badge.svg?branch=ci%2Fcd)](https://github.com/alechh/personal-drive-bot/actions/workflows/tests.yml)

[![Codacy Badge](https://app.codacy.com/project/badge/Grade/1ab0987675a2409b9f4b8cdd7ae175fa)](https://app.codacy.com/gh/alechh/personal-drive-bot/dashboard?utm_source=gh&utm_medium=referral&utm_content=&utm_campaign=Badge_grade)

# personal-drive-bot
Телеграм бот для организации файлового хранилища внутри мессенджера Телеграм.

## Описание
-   Так как Телеграм предоставляет неограниченный объём хранилища для файлов, то его можно использовать в качестве файлового хранилища. 
-   Но делать это посредством приватных телеграм-каналов неудобно по ряду причин. Данный бот позволяет организовать файловое хранилище внутри мессенджера. 
-   Бот позволяет посредством Unix-like команда (ls, cd, mkdir, rm) создавать папки, загружать файлы, просматривать содержимое папок, скачивать файлы, удалять файлы и папки.

## Как развернуть бота
1.  Склонировать репозиторий
2.  В директории проекта создать файл `.env` и заполнить его переменными окружения:
```
token = 'YOUR_BOT_TOKEN'
db_name = 'postgres'
db_user = 'user'
db_pass = 'password'
```
3.  Поднять docker-compose
```
docker-compose up --build -d
```

## Список поддерживаемых команд
-   `/start` - запуск бота
-   `/help` - список команд
-   `/backup` - бэкап данных
-   `/restore` - восстановление данных из бэкапа
-   `/stat` - Количество сохраненных файлов
-   `ls` - просмотр содержимого текущей директории
-   `cd <folder_name>` - переход в другую директорию (назад - `cd ..`)
-   `mkdir <folder_name>` - создание новой директории
-   `rm <folder_or_file_name>` - удаление файла или директории (удаление папки вместо с содержимым `rm -r <folder_name>`)
-   `mv <file_name> <folder_name>` - перемещение файла в другую директорию
-   `pwd` - показать текущую директорию
-   `./ <file_name>` - получить файл из текущей директории

Файлы загружаются в текущую директорию посредством отправки в чат с ботом.
