# docker/db/Dockerfile
FROM postgres:16-alpine

# копируем скрипт инициализации — он выполнится при первом запуске
COPY init.sql /docker-entrypoint-initdb.d/

# том для данных объявляется в docker-compose
EXPOSE 5432