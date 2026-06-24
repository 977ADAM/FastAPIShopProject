# FastAPI Shop

Полнофункциональный интернет-магазин: **FastAPI** (backend) + **Vue 3** (frontend), упакованный в Docker с Nginx и автоматическим выпуском SSL-сертификатов через Let's Encrypt.

## Стек технологий

**Backend**
- FastAPI 0.124 + Uvicorn
- SQLAlchemy 2.0 (SQLite)
- Pydantic 2 / pydantic-settings
- Управление зависимостями — [uv](https://docs.astral.sh/uv/)
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
│   │   ├── database.py        # Engine, сессии, init_db
│   │   ├── models/            # SQLAlchemy модели (product, category)
│   │   ├── schemas/           # Pydantic-схемы запросов/ответов
│   │   ├── repositories/      # Доступ к данным
│   │   ├── services/          # Бизнес-логика (products, categories, cart)
│   │   └── routes/            # API-эндпоинты
│   ├── static/images/         # Изображения товаров
│   ├── seed_data.py           # Наполнение БД тестовыми данными
│   ├── run.py                 # Локальный запуск через uvicorn
│   ├── pyproject.toml         # Зависимости и метаданные проекта (uv)
│   ├── uv.lock                # Зафиксированные версии зависимостей
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
├── nginx/                     # Конфигурация reverse proxy
├── docker-compose.yml
└── deploy.sh                  # Автоматический деплой на VPS
```

## Локальная разработка

### Backend

Требуется [uv](https://docs.astral.sh/uv/) (`curl -LsSf https://astral.sh/uv/install.sh | sh`).

```bash
cd backend
uv sync                  # создаст .venv и установит зависимости из uv.lock

# (опционально) наполнить БД тестовыми данными
uv run python seed_data.py

# запуск
uv run python run.py
```

> Добавить зависимость: `uv add <пакет>` · обновить lock: `uv lock`

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

## API

Базовый префикс — `/api`.

### Products

| Метод | Путь | Описание |
|-------|------|----------|
| `GET` | `/api/products` | Список всех товаров |
| `GET` | `/api/products/{product_id}` | Товар по ID |
| `GET` | `/api/products/category/{category_id}` | Товары по категории |

### Categories

| Метод | Путь | Описание |
|-------|------|----------|
| `GET` | `/api/categories` | Список всех категорий |
| `GET` | `/api/categories/{category_id}` | Категория по ID |

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
| `DATABASE_URL` | `sqlite:///./shop.db` | Строка подключения к БД |
| `CORS_ORIGINS` | localhost:5173, 3000 | Разрешённые источники CORS |
| `STATIC_DIR` | `static` | Каталог статики |
| `IMAGES_DIR` | `static/images` | Каталог изображений |

Frontend использует переменную сборки `VITE_API_BASE_URL` (базовый URL API).

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
docker compose exec backend python seed_data.py   # пересоздать тестовые данные
```

Сертификаты Let's Encrypt обновляются автоматически контейнером `certbot`.

## Сервисы Docker Compose

| Сервис | Назначение | Порт |
|--------|------------|------|
| `backend` | FastAPI + SQLite | 8000 (internal) |
| `frontend` | Собранный Vue + Nginx | 80 (internal) |
| `nginx` | Reverse proxy + SSL | 80, 443 |
| `certbot` | Авто-обновление сертификатов | — |
