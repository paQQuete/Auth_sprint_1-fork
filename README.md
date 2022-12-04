Ссылка на проект https://github.com/alexbravada/Auth_sprint_1
Участники @npocbet, @paQQuete, @alexbravada
# Проектная работа 6 спринта

## Взаимодействие с другими сервисами

Сервис аутентификации выдает клиентскому приложению JWT токены. Эти токены используются для аутетификации в других
сервисах, например сервис [API](https://github.com/alexbravada/Async_API_sprint_2). Для аутентификации в этом
сервисе API необходимо указать Bearer токен в заголовке Authorization, токен будет провалидирован самим сервисом.
Второй токен часто передаётся в теле запроса например: {"access_token": "jwt"}


## Запуск проекта:

1. Создаем файл .env на основе .env_example (копируем и редактируем)
2. Запускаем создание докер-образа:

```
docker-compose -f docker-compose.dev.yml up --build  
```

3. Проводим миграции БД. Для этого следует зайти в контейнер с API и запустить миграции через командную строку Flask:

```
docker exec -it auth_sprint_1 bash
python3 -m flask db upgrade
```

В Postgre базе создадутся все нужные миграции и партиции.

4. ОПЦИОНАЛЬНО: Создаем суперпользователя. Нужно зайти в контейнер с Flask и запустить консольную команду (не забудьте
   указать свой емэйл и пароль)

```
docker exec -it auth_sprint_1 bash
python3 -m flask create-superuser your@email.com yourpassword123
```

## Особенности проекта
```
- В проекте {"is_admin": True/False} прописывается в JWT payload, по умолчанию в БД проставляется False

```

## Структура базы данных

После проведения миграций в базе данных Postgres появятся таблицы:

- alembic_version - хранит идентификатор миграции базы данных
- user_info - таблица для добавленных юзеров
- login_history - пустая таблица. В ней хранится история входов пользователя.
- role - таблица для добавленных ролей
- user__role - связка uuid user_id и role_id

# Список endpoints

Для тестирования ручек через [OpenAPI] необходимо перейти по адресу:

```
http://localhost/
```

Представленные enpoints:

Управление ролями:

- Получение списка ролей: **GET /api/v1/auth/role**
- Создание роли: **POST /api/v1/auth/role/add**
- Удаление роли: **DELETE /api/v1/user/auth/role/delete**
- Получение роли по идентификатору: **GET /api/v1/auth/role/<int:role_id>**
- Изменение роли по ее идентификатору в теле зарпоса: **PATCH /api/v1/auth/role/update**

Управление авторизацией:

- Авторизация пользователя: **POST /api/v1/auth/user/signin**
- Создание пользователя: **POST /api/v1/auth/user/signup**
- Подтверждение валидности access tokena: - **POST /api/v1/auth/user/access**
- Выход пользователя (помещает переданные токены в блоклист): **POST /api/v1/auth/user/logout**
- Для валидного refresh-токена возвращает пару токенов access+refresh: **POST /api/v1/auth/refresh**

Управление пользователями:

- Обновление логина и пароля пользователя: **PATCH /api/v1/auth/user/**
- История авторизаций пользователя: **GET /api/v1/auth/user/auth_history**
- Удаление роли у пользователя: **DELETE /api/v1/auth/user/role/user_role_delete**
- Получение списка ролей одного пользователя **GET /api/v1/auth/user/role/user_role_show/<int:user_id>**
- Добавление роли пользователя **POST /api/v1/auth/user/role/user_role_add**




С этого модуля вы больше не будете получать чётко расписанное ТЗ, а задания для каждого спринта вы найдёте внутри уроков. Перед тем как начать программировать, вам предстоит продумать архитектуру решения, декомпозировать задачи и распределить их между командой.

В первом спринте модуля вы напишете основу вашего сервиса и реализуете все базовые требования к нему. Старайтесь избегать ситуаций, в которых один из ваших коллег сидит без дела. Для этого вам придётся составлять задачи, которые можно выполнить параллельно и выбрать единый стиль написания кода.

К концу спринта у вас должен получиться сервис авторизации с системой ролей, написанный на Flask с использованием gevent. Первый шаг к этому — проработать и описать архитектуру вашего сервиса. Это значит, что перед тем, как приступить к разработке, нужно составить план действий: из чего будет состоять сервис, каким будет его API, какие хранилища он будет использовать и какой будет его схема данных. Описание нужно сдать на проверку. Вам предстоит выбрать, какой метод организации доступов использовать для онлайн-кинотеатра, и систему прав, которая позволит ограничить доступ к ресурсам. 

Для описания API рекомендуем использовать [OpenAPI](https://editor.swagger.io){target="_blank"}, если вы выберете путь REST. Или используйте текстовое описание, если вы планируете использовать gRPC. С этими инструментами вы познакомились в предыдущих модулях. Обязательно продумайте и опишите обработку ошибок. Например, как отреагирует ваш API, если обратиться к нему с истёкшим токеном? Будет ли отличаться ответ API, если передать ему токен с неверной подписью? А если имя пользователя уже занято? Документация вашего API должна включать не только ответы сервера при успешном завершении запроса, но и понятное описание возможных ответов с ошибкой.

После прохождения ревью вы можете приступать к программированию. 

Для успешного завершения первой части модуля в вашем сервисе должны быть реализованы API для аутентификации и система управления ролями. Роли понадобятся, чтобы ограничить доступ к некоторым категориям фильмов. Например, «Фильмы, выпущенные менее 3 лет назад» могут просматривать только пользователи из группы 'subscribers'.  

## API для сайта и личного кабинета

- регистрация пользователя;
- вход пользователя в аккаунт (обмен логина и пароля на пару токенов: JWT-access токен и refresh токен); 
- обновление access-токена;
- выход пользователя из аккаунта;
- изменение логина или пароля (с отправкой email вы познакомитесь в следующих модулях, поэтому пока ваш сервис должен позволять изменять личные данные без дополнительных подтверждений);
- получение пользователем своей истории входов в аккаунт;

## API для управления доступами

- CRUD для управления ролями:
  - создание роли,
  - удаление роли,
  - изменение роли,
  - просмотр всех ролей.
- назначить пользователю роль;
- отобрать у пользователя роль;
- метод для проверки наличия прав у пользователя. 

## Подсказки

1. Продумайте, что делать с анонимными пользователями, которым доступно всё, что не запрещено отдельными правами.
2. Метод проверки авторизации будет всегда нужен пользователям. Ходить каждый раз в БД — не очень хорошая идея. Подумайте, как улучшить производительность системы.
3. Добавьте консольную команду для создания суперпользователя, которому всегда разрешено делать все действия в системе.
4. Чтобы упростить себе жизнь с настройкой суперпользователя, продумайте, как сделать так, чтобы при авторизации ему всегда отдавался успех при всех запросах.
5. Для реализации ограничения по фильмам подумайте о присвоении им какой-либо метки. Это потребует небольшой доработки ETL-процесса.


## Дополнительное задание

Реализуйте кнопку «Выйти из остальных аккаунтов», не прибегая к хранению в БД активных access-токенов.

## Напоминаем о требованиях к качеству

Перед тем как сдать ваш код на проверку, убедитесь, что 

- Код написан по правилам pep8: при запуске [линтера](https://semakin.dev/2020/05/python_linters/){target="_blank"} в консоли не появляется предупреждений и возмущений;
- Все ключевые методы покрыты тестами: каждый ответ каждой ручки API и важная бизнес-логика тщательно проверены;
- У тестов есть понятное описание, что именно проверяется внутри. Используйте [pep257](https://www.python.org/dev/peps/pep-0257/){target="_blank"}; 
- Заполните README.md так, чтобы по нему можно было легко познакомиться с вашим проектом. Добавьте короткое, но ёмкое описание проекта. По пунктам опишите как запустить приложения с нуля, перечислив полезные команды. Упомяните людей, которые занимаются проектом и их роли. Ведите changelog: описывайте, что именно из задания модуля уже реализовано в вашем сервисе и пополняйте список по мере развития.
- Вы воспользовались лучшими практиками описания конфигурации приложений из урока. 
