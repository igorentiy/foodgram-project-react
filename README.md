# FoodGram
![https://github.com/igorentiy91](https://img.shields.io/badge/Developed%20by-igorentiy91-blue)
![foodgram-project-react Workflow ](https://github.com/igorentiy/foodgram-project-react/actions/workflows/foodgram_workflow.yml/badge.svg?branch=master&event=push)

## Описание проекта Foodgram
«Продуктовый помощник»: приложение, в котором пользователи публикуют рецепты, могут подписываться на публикации других авторов и добавлять рецепты в избранное. Сервис «Список покупок» позволит пользователю создавать список продуктов, которые нужно купить для приготовления выбранных блюд.

Проект развернут по адресу [51.250.88.72](http://51.250.88.72)

Документацию к API можно посмотреть [тут](http://51.250.88.72/api/docs/)
## Запуск проекта в dev-режиме

- Установить и активировать виртуальное окружение

```
source /venv/bin/activated
```

- Установить зависимости из файла requirements.txt

```
python -m pip install --upgrade pip
pip install -r requirements.txt
```

- Выполнить миграции:

```
python manage.py migrate
```

- В папке с файлом manage.py выполнить команду:
```
python manage.py runserver
```

## Запуск с использованием CI/CD

Установить docker, docker-compose на сервере ВМ Yandex.Cloud:
```
ssh username@ip
```
```
sudo apt update && sudo apt upgrade -y && sudo apt install curl -y
```
```
sudo curl -fsSL https://get.docker.com -o get-docker.sh && sudo sh get-docker.sh && sudo rm get-docker.sh
```
```
sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
```
```
sudo chmod +x /usr/local/bin/docker-compose
```

Создайте папку infra:

```
mkdir infra
```
- Перенести файлы docker-compose.yml и default.conf на сервер.

```
scp docker-compose.yml username@server_ip:/home/<username>/infra
```
```
scp default.conf <username>@<server_ip>:/home/<username>/infra
```
- Создайте файл .env в дериктории infra:

```
touch .env
```
- Заполнить в настройках репозитория секреты .env

```python
DB_ENGINE="ваш тип модуля управления БД"
DB_NAME="имя БД"
POSTGRES_USER="имя пользователя БД"
POSTGRES_PASSWORD="пароль пользователя БД"
DB_HOST="хост БД, напимер localhost или db"
DB_PORT="5432"
```

Для доступа к контейнеру выполните следующие команды:

```
sudo docker-compose exec backend python manage.py makemigrations
```
```
sudo docker-compose exec backend python manage.py migrate --noinput
```
```
sudo docker-compose exec backend python manage.py createsuperuser
```
```
sudo docker-compose exec backend python manage.py collectstatic --no-input
```

Дополнительно можно наполнить базу данных ингредиентами и тэгами:

```
sudo docker-compose exec backend python manage.py load_tags
```
```
sudo docker-compose exec backend python manage.py load_ingredients
```

## Запуск проекта через Docker
- В папке infra выполнить команду, чтобы собрать контейнер:

```
sudo docker-compose up -d
```

Для доступа к контейнеру выполните следующие команды:

```
sudo docker-compose exec backend python manage.py makemigrations
```
```
sudo docker-compose exec backend python manage.py migrate --noinput
```
```
sudo docker-compose exec backend python manage.py createsuperuser
```
```
sudo docker-compose exec backend python manage.py collectstatic --no-input
```

Дополнительно можно наполнить базу данных ингредиентами и тэгами:
```
sudo docker-compose exec backend python manage.py load_ingr
```
