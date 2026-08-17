# Sanic + SQLAlchemy 2.0 Authentication & Authorization System

Этот проект представляет собой **полностью кастомную систему аутентификации и авторизации**, построенную на асинхронном стеке **Sanic + SQLAlchemy 2.0** с использованием **JWT** (access + refresh токены). Реализовано **ролевое разграничение доступа (RBAC)** — каждое право задаётся парой `(ресурс, действие)`, привязывается к ролям, а пользователи могут иметь несколько ролей.

Проект разработан как **тестовое задание**, демонстрирующее понимание:
- отличий аутентификации от авторизации;
- механизмов работы JWT-токенов и их обновления;
- управления безопасностью веб-приложений;
- проектирования схемы БД для гибкого управления правами.

---

## Стек технологий

| Компонент       | Технология                                    |
|-----------------|-----------------------------------------------|
| **Фреймворк**   | Sanic (асинхронный)                           |
| **ORM**         | SQLAlchemy 2.0 (async)                        |
| **База данных** | PostgreSQL (asyncpg)                          |
| **Миграции**    | Alembic                                       |
| **Хэширование** | passlib[bcrypt]                               |
| **JWT**         | PyJWT                                         |
| **Управление**  | python-dotenv                                 |

---

## Требования

- Python 3.9+
- PostgreSQL (локальный или через Docker)
- Git

---

## Установка и запуск

1. **Клонировать репозиторий**
   ```bash
   git clone <url>
   cd sanic_auth_project
   ```

2. **Создать и активировать виртуальное окружение**
    ```bash
    python3 -m venv venv
    source venv/bin/activate      # Linux/macOS
    # venv\Scripts\activate       # Windows
    ```

3. **Установить зависимости**
    ```bash
    pip install -r requirements.txt
    ```

4. **Настроить переменные окружения**
    Создать файл `.env` в корне проекта со следующим содержимым (подставьте свои данные):
    ```env
    DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/authdb
    SECRET_KEY=your-super-secret-key
    ALGORITHM=HS256
    ACCESS_TOKEN_EXPIRE_MINUTES=30
    REFRESH_TOKEN_EXPIRE_DAYS=7
    ```

5. **Создать базу данных**
    Если база ещё не создана, выполните в psql:
    ```sql
    CREATE DATABASE authdb;
    ```

6. **Применить миграции (создать таблицы)**
    При первом запуске таблицы создадутся автоматически через `Base.metadata.create_all.`
    Если вы хотите использовать Alembic, выполните:
    ```bash
    alembic upgrade head
    ```

7. **Наполнить БД тестовыми данными**

    ```bash
    python seed.py
    ```

    Будут созданы:
    
    3 роли: admin, manager, viewer
    
    4 пользователя (см. раздел «Тестовые пользователи»)
    
    Ресурсы для project и report с действиями view, create, edit, delete
    
    Назначены права согласно ролям.

8. **Запустить приложение**

    ```bash
    python app.py
    ```
    Сервер будет доступен по адресу http://localhost:8000.

# Структура проекта 
```mermaid
flowchart LR
    %% Определение стилей
    classDef root fill:#6a5acd,stroke:#2E1A3B,color:#fff,font-weight:bold
    classDef level1 fill:#7b68ee,stroke:#5B2C8E,color:#fff,font-weight:bold
    classDef level2 fill:#a496f2,stroke:#7D3C98,color:#2E1A3B
    classDef file fill:#8e82d9,stroke:#A569BD,color:#2E1A3B
    classDef modelfile fill:#b0a8e3,stroke:#C39BD3,color:#2E1A3B

    %% Корень
    root["sanic_auth_project<br>Корень проекта"]:::root

    %% Файлы в корне
    app["app.py<br>Точка входа"]:::level2
    config["config.py<br>Настройки из .env"]:::level2
    req["requirements.txt<br>Зависимости"]:::level2
    seed["seed.py<br>Наполнение БД"]:::level2

    %% Папки первого уровня
    db["db<br>БД и модели"]:::level1
    services["services<br>Бизнес-логика"]:::level1
    middlewares["middlewares<br>Обработчики"]:::level1
    routes["routes<br>Эндпоинты API"]:::level1

    %% Связи от корня
    root --> app
    root --> config
    root --> req
    root --> seed
    root --> db
    root --> services
    root --> middlewares
    root --> routes

    %% Внутри db
    base["base.py<br>Базовый класс"]:::file
    session["session.py<br>Асинхронная сессия"]:::file
    models["models<br>Модели данных"]:::level2
    db --> base
    db --> session
    db --> models

    %% Внутри models
    user["user.py<br>Пользователи"]:::modelfile
    role["role.py<br>Роли"]:::modelfile
    resource["resource.py<br>Права (ресурс+действие)"]:::modelfile
    assoc["associations.py<br>Связи многие-ко-многим"]:::modelfile
    blacklist["blacklisted_token.py<br>Чёрный список refresh"]:::modelfile
    models --> user
    models --> role
    models --> resource
    models --> assoc
    models --> blacklist

    %% Внутри services
    auth_srv["auth.py<br>Хэширование, JWT"]:::file
    perm_srv["permissions.py<br>Декораторы прав"]:::file
    services --> auth_srv
    services --> perm_srv

    %% Внутри middlewares
    sess_mid["session.py<br>Открытие/закрытие сессии"]:::file
    auth_mid["auth.py<br>Проверка JWT"]:::file
    middlewares --> sess_mid
    middlewares --> auth_mid

    %% Внутри routes
    auth_route["auth.py<br>Регистрация, логин, профиль"]:::file
    protected_route["protected.py<br>Защищённые ресурсы"]:::file
    admin_route["admin.py<br>Админка (управление ролями)"]:::file
    routes --> auth_route
    routes --> protected_route
    routes --> admin_route
```

# API Эндпоинты

Примечание: Все публичные эндпоинты (/, /ping, /auth/login, /auth/register) не требуют токена.
Для всех остальных в заголовке необходимо передавать:

```text
Authorization: Bearer <access_token>
```

### Публичные

| Метод | URL                | Описание                                     | Тело запроса (JSON)                                                                 |
|-------|--------------------|----------------------------------------------|-------------------------------------------------------------------------------------|
| POST  | `/auth/register`   | Регистрация нового пользователя               | `{ "email", "password", "password_confirm", "first_name", "last_name", "patronymic?" }` |
| POST  | `/auth/login`      | Вход, возвращает `access_token` и `refresh_token` | `{ "email", "password" }`                                                       |
| GET   | `/`                | Приветственный ответ                          | –                                                                                   |
| GET   | `/ping`            | Проверка подключения к БД                     | –                                                                                   |

### Защищённые (требуют токен)


| Метод | URL | Описание | Тело запроса (JSON) |
|-------|-----|----------|---------------------|
| GET | /auth/me | Получить данные текущего пользователя | – |
| PUT | /auth/profile | Обновить имя, фамилию, отчество | `{ "first_name?", "last_name?", "patronymic?" }` |
| DELETE | /auth/profile | Мягкое удаление аккаунта (is_active=False) | – |
| POST | /auth/logout | Выход (добавляет refresh_token в blacklist) | `{ "refresh_token": "..." }` |
| GET | /api/projects | Пример защищённого ресурса (требует право project:view) | – |
