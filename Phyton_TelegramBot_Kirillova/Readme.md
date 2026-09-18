Проект: Телеграмм-бот с функцией календаря
Анна Кириллова
kad1982
kirilliza@yandex.ru

Для старта работы необходимо скопировать файл settings/.envs/.env.local.template в файл settings/.envs/.env и заполнить
его своими данными, выполнив команду
`cp settings/.envs/.env.local.template settings/.envs/.env`

CREATE DATABASE calendar;
CREATE USER new_user WITH PASSWORD 'new_user';
ALTER ROLE new_user SUPERUSER NOCREATEDB NOCREATEROLE INHERIT LOGIN NOREPLICATION NOBYPASSRLS;
GRANT CONNECT ON DATABASE calendar TO new_user;
GRANT ALL PRIVILEGES ON DATABASE calendar TO new_user;
GRANT ALL ON SCHEMA public TO new_user;
GRANT CREATE ON SCHEMA public TO new_user;

python -m app.tables
python -m app._test_repo


pip install "python-telegram-bot[callback-data]"