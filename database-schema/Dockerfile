# используем официальный образ PostgreSQL в качестве базового образа
FROM postgres:latest

# определяем переменные окружения для базы данных
ENV POSTGRES_USER alechh
ENV POSTGRES_PASSWORD 123
ENV POSTGRES_DB postgres

# копируем файл инициализации базы данных в образ
COPY ./init.sql /docker-entrypoint-initdb.d/

# открываем порт 5432 для подключений к базе данных
EXPOSE 5432