FROM python:3.11-slim

# Устанавливаем uv из официального образа
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# venv живёт вне /app, чтобы bind-mount ./backend:/app не затирал его
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PROJECT_ENVIRONMENT=/opt/venv \
    PATH="/opt/venv/bin:$PATH"

# Устанавливаем зависимости отдельным слоем (кэшируется при неизменных pyproject/lock)
COPY backend/pyproject.toml backend/uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

COPY backend/ .

# Создаем директорию static в правильном месте
RUN mkdir -p static/images

RUN chmod -R 755 static

EXPOSE 8000

CMD ["uv", "run", "--frozen", "--no-dev", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
