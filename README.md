# FastAPI Shop

Полнофункциональный интернет-магазин: **FastAPI** (backend) + **Vue 3** (frontend), упакованный в Docker с Nginx и автоматическим выпуском SSL-сертификатов через Let's Encrypt.

## Стек технологий

**Backend**
- FastAPI + Uvicorn
- SQLAlchemy 2.0 + **PostgreSQL** (SQLite — для локальной разработки)
- **Alembic** — миграции БД
- Pydantic 2 / pydantic-settings
- JWT-аутентификация (PyJWT + bcrypt) для админских операций
- Rate-limiting логина (slowapi), загрузка изображений (multipart)
- Управление зависимостями — [uv](https://docs.astral.sh/uv/); ruff + mypy
- Слоистая архитектура: `models → repositories → services → routes`

**Frontend**
- Vue 3.5 (Composition API)
- Vite 7
- Pinia (state management)
- Vue Router 4
- Axios

**Инфраструктура**
- Docker / Docker Compose
- Nginx (reverse proxy + раздача статики)
- Certbot (Let's Encrypt, авто-renew)

## Структура проекта

```
FastAPIShopProject/
├── backend/
│   ├── app/
│   │   ├── main.py            # Точка входа FastAPI, CORS, роутеры
│   │   ├── config.py          # Настройки (pydantic-settings)
│   │   ├── database.py        # Engine, сессии
│   │   ├── security.py        # JWT + bcrypt, зависимость require_admin
│   │   ├── limiter.py         # slowapi rate limiter
│   │   ├── models/            # SQLAlchemy модели (Mapped-стиль)
│   │   ├── schemas/           # Pydantic-схемы (+ auth)
│   │   ├── repositories/      # Доступ к данным
│   │   ├── services/          # Бизнес-логика (products, categories, cart)
│   │   └── routes/            # API (auth, products, categories, cart, uploads)
│   ├── alembic/               # Миграции БД (alembic/versions)
│   ├── alembic.ini            # Конфигурация Alembic
│   ├── tests/                 # Pytest-тесты (изолированная in-memory БД)
│   ├── static/images/         # Изображения товаров
│   ├── seed_data.py           # Наполнение БД тестовыми данными
│   ├── run.py                 # Локальный запуск через uvicorn
│   ├── pyproject.toml         # Зависимости и метаданные проекта (uv)
│   ├── uv.lock                # Зафиксированные версии зависимостей
│   ├── .env.example           # Пример конфигурации backend
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── views/             # Страницы (Home, ProductDetail, Cart)
│   │   ├── components/        # UI-компоненты
│   │   ├── stores/            # Pinia-сторы (cart, products)
│   │   ├── services/api.js    # HTTP-клиент к backend
│   │   └── router/            # Vue Router
│   ├── nginx.conf
│   └── Dockerfile
│   └── src/
│       ├── views/admin/       # Админ-UI (AdminLogin, AdminProducts)
│       └── stores/auth.js     # JWT-аутентификация на фронте
├── nginx/nginx.conf.template  # Reverse proxy (envsubst по ${DOMAIN})
├── scripts/                   # backup.sh / restore.sh (PostgreSQL)
├── .github/workflows/ci.yml   # CI: ruff+mypy+alembic+pytest, фронт, docker
├── .github/dependabot.yml     # Авто-обновления зависимостей
├── .pre-commit-config.yaml    # Хуки pre-commit (ruff)
├── .env.example               # Пример корневого .env для деплоя
├── docker-compose.yml
└── deploy.sh                  # Автоматический деплой на VPS
```

## Локальная разработка

### Backend

Требуется [uv](https://docs.astral.sh/uv/) (`curl -LsSf https://astral.sh/uv/install.sh | sh`).

```bash
cd backend
uv sync                  # создаст .venv и установит зависимости из uv.lock

# применить миграции (схемой управляет Alembic)
uv run alembic upgrade head

# (опционально) наполнить БД тестовыми данными
uv run python seed_data.py

# запуск
uv run python run.py
```

По умолчанию локально используется SQLite (`sqlite:///./shop.db`). Для PostgreSQL
задайте `DATABASE_URL`, например:
`postgresql+psycopg://fashop:fashop@localhost:5432/fashop`.

> Добавить зависимость: `uv add <пакет>` · обновить lock: `uv lock`
> Миграция при изменении моделей: `uv run alembic revision --autogenerate -m "..."`
> Линтер: `uv run ruff check .`

API будет доступен на `http://localhost:8000`.

- Swagger UI: `http://localhost:8000/api/docs`
- ReDoc: `http://localhost:8000/api/redoc`
- Health check: `http://localhost:8000/health`

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Dev-сервер поднимется на `http://localhost:5173`. По умолчанию обращается к API
по адресу `http://localhost:8000/api` (переопределяется переменной
`VITE_API_BASE_URL`).

Дополнительные команды:

```bash
npm run build     # production-сборка
npm run preview   # предпросмотр сборки
npm run lint      # ESLint с авто-фиксом
npm run format    # Prettier
```

## Тесты

Backend — pytest (изолированная in-memory SQLite-БД, без обращения к реальной БД):

```bash
cd backend
uv run pytest
```

Frontend — Vitest (jsdom):

```bash
cd frontend
npm run test
```

## CI

GitHub Actions (`.github/workflows/ci.yml`) на каждый push/PR в `main`:

- **backend** — `ruff` + `mypy` + `alembic upgrade head` + `pytest`
- **frontend** — `npm ci` + `lint` + `test` + `build`
- **docker** — сборка backend- и frontend-образов

Зависимости обновляются автоматически через Dependabot. Локальные хуки —
`pre-commit install` (запускает ruff перед коммитом).

## API

Базовый префикс — `/api`. Эндпоинты на чтение публичны; операции записи
(`POST`/`PUT`/`DELETE` для products и categories) требуют JWT админа.

### Auth

| Метод | Путь | Тело | Описание |
|-------|------|------|----------|
| `POST` | `/api/auth/login` | `{ username, password }` | Вернёт `{ access_token }` (лимит 5/мин) |

Защищённые запросы передают токен в заголовке: `Authorization: Bearer <token>`.

### Products

| Метод | Путь | Доступ | Описание |
|-------|------|--------|----------|
| `GET` | `/api/products` | публично | Список товаров (`?limit=&offset=&search=`) |
| `GET` | `/api/products/{product_id}` | публично | Товар по ID |
| `GET` | `/api/products/category/{category_id}` | публично | Товары по категории |
| `POST` | `/api/products` | админ | Создать товар |
| `PUT` | `/api/products/{product_id}` | админ | Обновить товар |
| `DELETE` | `/api/products/{product_id}` | админ | Удалить товар |

### Categories

| Метод | Путь | Доступ | Описание |
|-------|------|--------|----------|
| `GET` | `/api/categories` | публично | Список всех категорий |
| `GET` | `/api/categories/{category_id}` | публично | Категория по ID |
| `POST` | `/api/categories` | админ | Создать категорию |
| `PUT` | `/api/categories/{category_id}` | админ | Обновить категорию |
| `DELETE` | `/api/categories/{category_id}` | админ | Удалить категорию (если без товаров) |

### Uploads

| Метод | Путь | Доступ | Описание |
|-------|------|--------|----------|
| `POST` | `/api/uploads/image` | админ | Загрузить изображение (multipart `file`), вернёт `{ image_url }` |

## Админка (frontend)

- `/admin/login` — вход (логин/пароль администратора)
- `/admin` — управление товарами и категориями (создание/редактирование/удаление,
  загрузка изображений). Доступ защищён router-guard; JWT хранится в localStorage
  и подставляется в запросы интерсептором axios.

### Cart

Корзина — без хранения состояния на сервере: клиент передаёт текущее содержимое
корзины (`{ product_id: quantity }`) в каждом запросе, сервер возвращает
обновлённую корзину.

| Метод | Путь | Тело запроса | Описание |
|-------|------|--------------|----------|
| `POST` | `/api/cart` | `{ "1": 2, "3": 1 }` | Детали корзины (товары + суммы) |
| `POST` | `/api/cart/add` | `{ product_id, quantity, cart }` | Добавить товар |
| `PUT` | `/api/cart/update` | `{ product_id, quantity, cart }` | Изменить количество |
| `DELETE` | `/api/cart/remove/{product_id}` | `{ cart }` | Удалить товар |

## Конфигурация

Настройки backend задаются через переменные окружения или файл `backend/.env`
(см. `backend/app/config.py`):

| Переменная | По умолчанию | Описание |
|------------|--------------|----------|
| `APP_NAME` | `FastAPI Shop` | Название приложения |
| `DEBUG` | `True` | Режим отладки / авто-reload |
| `DATABASE_URL` | `sqlite:///./shop.db` | Строка подключения к БД (в Docker — PostgreSQL) |
| `CORS_ORIGINS` | localhost:5173, 3000 | Источники CORS (через запятую или JSON) |
| `STATIC_DIR` | `static` | Каталог статики |
| `IMAGES_DIR` | `static/images` | Каталог изображений |
| `ADMIN_USERNAME` | `admin` | Логин администратора |
| `ADMIN_PASSWORD_HASH` | (хеш «admin») | bcrypt-хеш пароля админа |
| `JWT_SECRET` | (заглушка) | Секрет для подписи JWT — **обязательно сменить в проде** |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `60` | Время жизни токена |

В Docker значения БД и админа приходят из корневого `.env` через docker-compose
(`POSTGRES_*`, `ADMIN_*`, `JWT_SECRET`). Frontend использует переменную сборки
`VITE_API_BASE_URL`.

> Сгенерировать bcrypt-хеш пароля:
> `docker compose run --rm backend uv run python -c "import bcrypt;print(bcrypt.hashpw(b'PASS', bcrypt.gensalt()).decode())"`
> При ручной вставке в `.env` экранируйте `$` как `$$`.

## Деплой на VPS (Ubuntu)

Скрипт `deploy.sh` выполняет полную автоматическую установку: запрашивает домен
и email, ставит Docker/Certbot, выпускает SSL-сертификаты, генерирует
конфигурацию Nginx и `.env`, собирает и запускает контейнеры, наполняет БД.

```bash
sudo ./deploy.sh
```

После деплоя:

- Магазин: `https://<домен>`
- API Docs: `https://<домен>/api/docs`
- Health: `https://<домен>/health`

### Полезные команды

```bash
docker compose ps              # статус контейнеров
docker compose logs -f         # логи всех сервисов
docker compose logs -f backend # логи backend
docker compose restart         # перезапуск
docker compose down            # остановка
docker compose exec backend uv run python seed_data.py   # пересоздать тестовые данные
```

Миграции применяются автоматически при старте backend (`alembic upgrade head`).
Сертификаты Let's Encrypt обновляются автоматически контейнером `certbot`.

### Бэкапы PostgreSQL

```bash
./scripts/backup.sh                       # дамп в ./backups/<db>_<timestamp>.sql.gz
./scripts/restore.sh backups/<файл>.sql.gz  # восстановление
```

`backup.sh` хранит дампы 14 дней; удобно повесить на cron.

## Сервисы Docker Compose

| Сервис | Назначение | Порт |
|--------|------------|------|
| `db` | PostgreSQL 16 (volume `postgres_data`) | 5432 (internal) |
| `backend` | FastAPI + Alembic + PostgreSQL | 8000 (internal) |
| `frontend` | Собранный Vue + Nginx | 80 (internal) |
| `nginx` | Reverse proxy + SSL | 80, 443 |
| `certbot` | Авто-обновление сертификатов | — |
