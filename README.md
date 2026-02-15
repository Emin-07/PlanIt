![Python](https://img.shields.io/badge/python-s?style=for-the-badge&logo=python&logoColor=%233776AB&color=white)
![FastAPI](https://img.shields.io/badge/fastapi-s?style=for-the-badge&logo=FastAPI&logoColor=%23009688&color=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-s?style=for-the-badge&logo=PostgreSQL&logoColor=%234169E1&color=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-s?style=for-the-badge&logo=SQLAlchemy&logoColor=%23D71F00&color=white)
![Docker](https://img.shields.io/badge/docker-s?style=for-the-badge&logo=Docker&logoColor=%232496ED&color=white)
![UV](https://img.shields.io/badge/uv-s?style=for-the-badge&logo=uv&logoColor=%23DE5FE9&color=white)
![Tests](https://img.shields.io/badge/pytest-test?style=for-the-badge&logo=pytest&logoColor=%230A9EDC&color=white)
![Redis](https://img.shields.io/badge/redis-server?style=for-the-badge&logo=redis&logoColor=%23FF4438&color=white)
![CI/CD](https://img.shields.io/badge/CI%2FCD-sd?style=for-the-badge&logo=githubactions&logoColor=%232088FF&color=white)

Here's the updated README with your actual Makefile commands:

# PlanIt API / ПланИт API

A robust, production-ready task management API built with FastAPI. / Надежное, готовое к продакшену API для управления задачами, созданное с использованием FastAPI.

---

## 🌐 Language / Язык

- [English](#english)
- [Русский](#russian)

---

## English

### 🚀 Features

- **User Authentication**: Secure JWT-based authentication with RSA256 encryption
- **Task Management**: Create, read, update, and delete tasks
- **Rate Limiting**: Redis-based rate limiting to prevent abuse
- **Email Notifications**: Password reset functionality with email support
- **Database**: SQLAlchemy ORM with SQLite (development/test) and PostgreSQL (production)
- **Docker Support**: Containerized application with docker-compose
- **CI/CD**: Automated testingcd
- **Comprehensive Testing**: Pytest suite with high coverage
- **Database Migrations**: Alembic for version control of database schema

### 🛠 Tech Stack

- **Framework**: FastAPI
- **Database**: SQLAlchemy ORM, SQLite (tests), PostgreSQL (production)
- **Authentication**: JWT tokens with RSA256 encryption
- **Caching/Rate Limiting**: Redis
- **Testing**: Pytest
- **Containerization**: Docker, Docker Compose
- **CI/CD**: GitHub Actions
- **Email**: SMTP integration
- **Migrations**: Alembic
- **Package Management**: UV (fast Python package installer)

### 📋 Prerequisites

- Python 3.9+
- Docker and Docker Compose
- Redis
- SMTP server credentials (for email functionality)
- OpenSSL (for generating JWT keys)
- UV package installer (`pip install uv`)

### 🚦 Getting Started

#### Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/planit-api.git
   cd planit-api
   ```

2. **Generate JWT certificates**
   ```bash
   make certs
   ```
   This creates RSA256 public/private keys in the `certs/` directory.

3. **Generate requirements files**
   ```bash
   make requirements
   ```
   Or individually:
   ```bash
   make requirements-prod    # Generate production requirements
   make requirements-dev     # Generate development requirements
   ```

4. **Create and activate virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

5. **Install dependencies**
   ```bash
   # Using UV (recommended - faster)
   pip install uv
   uv pip install -r requirements.txt
   uv pip install -r requirements-dev.txt
   ```

6. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

7. **Run database migrations**
   ```bash
   alembic upgrade head
   ```

8. **Start Redis server**
   ```bash
   redis-server
   ```

9. **Run the application**
   ```bash
   make run
   ```

10. **Access the API documentation**
    - Swagger UI: http://localhost:8000/docs
    - ReDoc: http://localhost:8000/redoc

#### Docker Deployment

1. **Build and run with Docker Compose**
   ```bash
   make run
   ```

2. **Stop containers**
   ```bash
   make down
   ```

3. **Run demo environment**
   ```bash
   make demo
   ```

4. **Clean up everything**
   ```bash
   make clean
   ```

### 📁 Project Structure

```
PlanIt/
├── main.py                    # Application entry point
├── core/                      # Core functionality
│   ├── config.py              # Configuration settings
│   ├── redis.py               # Redis client setup
│   └── setup.py               # App initialization
├── routes/                    # API routes
│   ├── auth_routes.py         # Authentication endpoints
│   ├── task_routes.py         # Task management endpoints
│   └── user_routers.py        # User management endpoints
├── services/                  # Business logic layer
│   ├── auth_validation.py     # JWT validation
│   ├── service.py             # Base service
│   ├── task_services.py       # Task operations
│   └── user_services.py       # User operations
├── models/                    # SQLAlchemy models
│   ├── user_model.py
│   └── task_model.py
├── schemas/                   # Pydantic schemas
│   ├── auth_schema.py
│   ├── user_schemas.py
│   ├── task_schemas.py
│   └── relation_schemas.py
├── utils/                     # Utility functions
│   ├── auth_helper.py         # Auth utilities
│   ├── auth_utils.py          # JWT handling
│   ├── data_helper.py         # Data processing
│   └── rate_limit.py          # Rate limiting
├── migrations/                 # Alembic migrations
│   └── versions/              # Migration versions
├── tests/                     # Test suite
│   ├── api/                   # API tests
│   │   ├── test_tasks.py
│   │   └── test_users.py
│   ├── helpers/               # Test helpers
│   │   └── auth.py
│   └── conftest.py            # Pytest fixtures
├── certs/                     # SSL/JWT certificates
│   ├── jwt-private.pem
│   └── jwt-public.pem
├── dockerfile                  # Docker configuration
├── docker-compose.yaml        # Main Docker Compose config
├── docker-compose.demo.yml    # Demo Docker Compose config
├── Makefile                    # Make commands
├── pyproject.toml             # Project metadata with dependencies
├── pytest.ini                 # Pytest configuration
├── requirements.txt           # Generated production dependencies
├── requirements-dev.txt       # Generated development dependencies
├── prestart.sh                # Pre-startup script
├── data_hash.py               # Test data loader
├── test_data.json             # Test data
├── test_send.py               # Test email sender
└── uv.lock                    # UV lock file
```


### 🧪 Testing

```bash
# Run all tests
make test
# or
pytest

# Run with coverage
pytest --cov=core --cov=routes --cov=services tests/

# Run specific test file
pytest tests/api/test_tasks.py -v

# Load test data
python data_hash.py
```

### 🔒 Environment Variables

```env
# Application
SECRET_KEY=your-secret-key-here
ALGORITHM=RS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# JWT Keys
JWT_PRIVATE_KEY_PATH=certs/jwt-private.pem
JWT_PUBLIC_KEY_PATH=certs/jwt-public.pem

# Database
DATABASE_URL=sqlite:///./planit.db
# For production: DATABASE_URL=postgresql://user:pass@localhost/dbname

# Redis
REDIS_URL=redis://localhost:6379

# Email
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# Rate Limiting
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_PERIOD=60  # seconds
```

### 📝 Makefile Commands

| Command | Description |
|---------|-------------|
| `make certs` | Generate JWT RSA256 public/private keys in certs/ directory |
| `make requirements` | Generate both production and development requirements |
| `make requirements-prod` | Generate production requirements.txt from pyproject.toml |
| `make requirements-dev` | Generate development requirements-dev.txt from pyproject.toml |
| `make run` | Build and run the application with docker-compose |
| `make test` | Run pytest test suite |
| `make demo` | Start demo environment using docker-compose.demo.yml |
| `make down` | Stop and remove docker-compose containers |
| `make clean` | Full cleanup: remove containers, volumes, and cache files |

### 📊 Rate Limiting

- Default: 100 requests per minute per IP
- Authentication endpoints: 5 requests per minute per IP
- Configurable via environment variables

### 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### 📄 License

MIT License - see the [LICENSE](LICENSE) file for details

### 📧 Contact

Project Link: [https://github.com/yourusername/planit-api](https://github.com/yourusername/planit-api)

---

## Russian

### 🚀 Возможности

- **Аутентификация пользователей**: Безопасная JWT-аутентификация с RSA256 шифрованием
- **Управление задачами**: Создание, чтение, обновление и удаление задач
- **Ограничение запросов**: Redis-базированное ограничение для предотвращения злоупотреблений
- **Email-уведомления**: Функционал сброса пароля с поддержкой email
- **База данных**: SQLAlchemy ORM с SQLite (разработка/тесты) и PostgreSQL (продакшен)
- **Docker поддержка**: Контейнеризованное приложение с docker-compose
- **CI/CD**: Автоматизированный конвейер тестирования и развертывания
- **Комплексное тестирование**: Pytest с высоким покрытием
- **Миграции БД**: Alembic для версионирования схемы базы данных

### 🛠 Технологический стек

- **Фреймворк**: FastAPI
- **База данных**: SQLAlchemy ORM, SQLite (тесты), PostgreSQL (продакшен)
- **Аутентификация**: JWT токены с RSA256 шифрованием
- **Кэширование/Ограничение запросов**: Redis
- **Тестирование**: Pytest
- **Контейнеризация**: Docker, Docker Compose
- **CI/CD**: GitHub Actions
- **Email**: SMTP интеграция
- **Миграции**: Alembic
- **Управление пакетами**: UV (быстрый установщик пакетов Python)

### 📋 Предварительные требования

- Python 3.9+
- Docker и Docker Compose
- Redis
- Учетные данные SMTP сервера (для email функционала)
- OpenSSL (для генерации JWT ключей)
- UV установщик пакетов (`pip install uv`)

### 🚦 Начало работы

#### Локальная разработка

1. **Клонируйте репозиторий**
   ```bash
   git clone https://github.com/yourusername/planit-api.git
   cd planit-api
   ```

2. **Сгенерируйте JWT сертификаты**
   ```bash
   make certs
   ```
   Эта команда создаст RSA256 публичные/приватные ключи в директории `certs/`.

3. **Сгенерируйте файлы зависимостей**
   ```bash
   make requirements
   ```
   Или по отдельности:
   ```bash
   make requirements-prod    # Сгенерировать продакшен зависимости
   make requirements-dev     # Сгенерировать зависимости для разработки
   ```

4. **Создайте и активируйте виртуальное окружение**
   ```bash
   python -m venv venv
   source venv/bin/activate  # На Windows: venv\Scripts\activate
   ```

5. **Установите зависимости**
   ```bash
   # Используя UV (рекомендуется - быстрее)
   pip install uv
   uv pip install -r requirements.txt
   uv pip install -r requirements-dev.txt
   ```

6. **Настройте переменные окружения**
   ```bash
   cp .env.example .env
   # Отредактируйте .env с вашими настройками
   ```

7. **Запустите миграции базы данных**
   ```bash
   alembic upgrade head
   ```

8. **Запустите Redis сервер**
   ```bash
   redis-server
   ```

9. **Запустите приложение**
   ```bash
   make run
   ```

10. **Доступ к документации API**
    - Swagger UI: http://localhost:8000/docs
    - ReDoc: http://localhost:8000/redoc

#### Docker развертывание

1. **Соберите и запустите с Docker Compose**
   ```bash
   make run
   ```

2. **Остановите контейнеры**
   ```bash
   make down
   ```

3. **Запустите демо-среду**
   ```bash
   make demo
   ```

4. **Полная очистка**
   ```bash
   make clean
   ```

### 📁 Структура проекта

```
PlanIt/
├── main.py                    # Точка входа приложения
├── core/                      # Базовая функциональность
│   ├── config.py              # Настройки конфигурации
│   ├── redis.py               # Настройка Redis клиента
│   └── setup.py               # Инициализация приложения
├── routes/                    # API маршруты
│   ├── auth_routes.py         # Эндпоинты аутентификации
│   ├── task_routes.py         # Эндпоинты задач
│   └── user_routers.py        # Эндпоинты пользователей
├── services/                  # Слой бизнес-логики
│   ├── auth_validation.py     # Валидация JWT
│   ├── service.py             # Базовый сервис
│   ├── task_services.py       # Операции с задачами
│   └── user_services.py       # Операции с пользователями
├── models/                    # SQLAlchemy модели
│   ├── user_model.py
│   └── task_model.py
├── schemas/                   # Pydantic схемы
│   ├── auth_schema.py
│   ├── user_schemas.py
│   ├── task_schemas.py
│   └── relation_schemas.py
├── utils/                     # Вспомогательные функции
│   ├── auth_helper.py         # Утилиты аутентификации
│   ├── auth_utils.py          # Обработка JWT
│   ├── data_helper.py         # Обработка данных
│   └── rate_limit.py          # Ограничение запросов
├── migrations/                 # Миграции Alembic
│   └── versions/              # Версии миграций
├── tests/                     # Тесты
│   ├── api/                   # Тесты API
│   │   ├── test_tasks.py
│   │   └── test_users.py
│   ├── helpers/               # Вспомогательные функции для тестов
│   │   └── auth.py
│   └── conftest.py            # Pytest фикстуры
├── certs/                     # SSL/JWT сертификаты
│   ├── jwt-private.pem
│   └── jwt-public.pem
├── dockerfile                  # Docker конфигурация
├── docker-compose.yaml        # Основная Docker Compose конфигурация
├── docker-compose.demo.yml    # Демо Docker Compose конфигурация
├── Makefile                    # Make команды
├── pyproject.toml             # Метаданные проекта с зависимостями
├── pytest.ini                 # Pytest конфигурация
├── requirements.txt           # Сгенерированные продакшен зависимости
├── requirements-dev.txt       # Сгенерированные зависимости для разработки
├── prestart.sh                # Скрипт предзапуска
├── data_hash.py               # Загрузчик тестовых данных
├── test_data.json             # Тестовые данные
├── test_send.py               # Тестовый отправитель email
└── uv.lock                    # UV lock файл
```

### 🧪 Тестирование

```bash
# Запустить все тесты
make test
# или
pytest

# Запустить с оценкой покрытия
pytest --cov=core --cov=routes --cov=services tests/

# Запустить конкретный файл тестов
pytest tests/api/test_tasks.py -v

# Загрузить тестовые данные
python data_hash.py
```

### 🔒 Переменные окружения

```env
# Приложение
SECRET_KEY=ваш-секретный-ключ
ALGORITHM=RS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# JWT ключи
JWT_PRIVATE_KEY_PATH=certs/jwt-private.pem
JWT_PUBLIC_KEY_PATH=certs/jwt-public.pem

# База данных
DATABASE_URL=sqlite:///./planit.db
# Для продакшена: DATABASE_URL=postgresql://пользователь:пароль@localhost/имябд

# Redis
REDIS_URL=redis://localhost:6379

# Email
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=ваш-email@gmail.com
SMTP_PASSWORD=ваш-пароль-приложения

# Ограничение запросов
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_PERIOD=60  # секунд
```

### 📝 Makefile Команды

| Команда | Описание |
|---------|----------|
| `make certs` | Сгенерировать JWT RSA256 публичные/приватные ключи в директории certs/ |
| `make requirements` | Сгенерировать продакшен и разработческие зависимости |
| `make requirements-prod` | Сгенерировать requirements.txt из pyproject.toml |
| `make requirements-dev` | Сгенерировать requirements-dev.txt из pyproject.toml |
| `make run` | Собрать и запустить приложение с docker-compose |
| `make test` | Запустить pytest тесты |
| `make demo` | Запустить демо-среду используя docker-compose.demo.yml |
| `make down` | Остановить и удалить docker-compose контейнеры |
| `make clean` | Полная очистка: удалить контейнеры, тома и кэш файлы |

### 📊 Ограничение запросов

- По умолчанию: 100 запросов в минуту на IP
- Эндпоинты аутентификации: 5 запросов в минуту на IP
- Настраивается через переменные окружения

### 🤝 Вклад в проект

1. Сделайте форк репозитория
2. Создайте ветку для функции (`git checkout -b feature/amazing-feature`)
3. Зафиксируйте изменения (`git commit -m 'Add amazing feature'`)
4. Отправьте изменения в ветку (`git push origin feature/amazing-feature`)
5. Откройте Pull Request

### 📄 Лицензия

MIT Лицензия - подробности в файле [LICENSE](LICENSE)

---
