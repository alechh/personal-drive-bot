# используем официальный образ PostgreSQL в качестве базового образа
FROM postgres:latest

# копируем файл инициализации базы данных в образ
COPY ./init.sql /docker-entrypoint-initdb.d/
