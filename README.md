# Fulfillment Management System (FMS)

Система управления фулфилментом с CRM, WMS и финансовой аналитикой.

## Быстрый старт

### Требования
- Docker 20.10+
- Docker Compose 2.0+

### Запуск

```bash
cd fms
cp .env.example .env
make up
```

Система будет доступна:
- Frontend: http://localhost
- API: http://localhost:8000
- Swagger: http://localhost:8000/docs

### Вход
- Email: admin@fms.local
- Password: admin123

## Команды

| Команда | Описание |
|---------|----------|
| `make up` | Запуск всех сервисов |
| `make down` | Остановка всех сервисов |
| `make logs` | Просмотр логов |
| `make migrate` | Применить миграции |
| `make test` | Запуск тестов |
| `make seed` | Загрузить начальные данные |

## Архитектура

- **Backend**: FastAPI + SQLAlchemy
- **Frontend**: React + Ant Design
- **БД**: PostgreSQL + Redis
- **Очереди**: Celery
- **Прокси**: Nginx

## Структура проекта

```
fms/
├── backend/          # FastAPI backend
│   ├── app/
│   │   ├── modules/  # Модули приложения
│   │   │   ├── dashboard/    # Дашборд
│   │   │   ├── finance/      # Финансы и PnL
│   │   │   ├── integrations/ # Интеграции с маркетплейсами
│   │   │   ├── orders/       # Заказы (CRM)
│   │   │   ├── products/     # Товары
│   │   │   ├── warehouse/    # Склад (WMS)
│   │   │   └── ...
│   │   └── models/   # SQLAlchemy модели
│   └── alembic/      # Миграции БД
├── frontend/         # React + TypeScript + Ant Design
│   └── src/
│       ├── pages/    # Страницы приложения
│       └── components/ # Компоненты
├── nginx/           # Nginx reverse proxy
├── docker-compose.yml
├── Makefile
└── .env.example
```

## API Документация

Swagger UI: http://localhost:8000/docs

## Основные возможности

### CRM (Заказы)
- Создание и управление заказами
- Отслеживание статусов заказов
- История изменений

### WMS (Склад)
- Управление складами, зонами, стеллажами, ячейками
- Приёмка товаров
- Резервирование товаров под заказы
- Перемещения товаров

### Финансы
- Расчёт PnL (прибыль/убыток) по заказам
- Тарифы на услуги
- Отчёты по периодам

### Интеграции
- Интеграция с маркетплейсами (Ozon, Wildberries)
- Синхронизация заказов
- Логи синхронизации

### Дашборд
- Статистика заказов за сегодня
- Финансовые показатели (выручка, маржа)
- Алерты о низких остатках

## Разработка

### Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## Сервисы

- **Backend**: http://localhost:8000
- **Frontend**: http://localhost:3000 (через Docker) или http://localhost:80 (через Nginx)
- **PostgreSQL**: localhost:5432
- **Redis**: localhost:6379
- **Nginx**: http://localhost:80

## Health Checks

- Backend: `GET /health` - возвращает `{"status": "healthy"}`
- API: `GET /api/v1/health` - возвращает `{"status": "healthy", "version": "0.1.0"}`
