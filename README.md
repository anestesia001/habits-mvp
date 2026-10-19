# Habit Tracker API

Простое REST API для учёта привычек на Python.

Проект использует:

- **FastAPI** — HTTP API и автоматическая OpenAPI-документация.
- **PostgreSQL** — хранение привычек и ежедневных отметок.
- **SQLAlchemy 2.0 + Psycopg 3** — ORM и драйвер PostgreSQL.
- **Boto3** — выгрузка CSV-отчётов в AWS S3.

FastAPI поддерживает работу с PostgreSQL через SQLAlchemy, а Boto3 предоставляет метод `upload_file` для загрузки файлов в S3.

## Возможности

- Создание, получение, изменение и удаление привычек.
- Отметка выполнения привычки за конкретную дату.
- Повторная отметка за ту же дату обновляет существующую запись.
- Фильтрация отметок по периоду.
- Генерация CSV-отчёта.
- Загрузка отчёта в AWS S3 или S3-совместимое хранилище, например MinIO или LocalStack.

## Быстрый старт

### 1. Клонировать проект

```bash
git clone <repository-url>
cd habit-tracker-api
```

### 2. Создать файл окружения

```bash
cp .env.example .env
```

Заполните значения:

```env
DATABASE_URL=postgresql+psycopg://habit_user:habit_password@localhost:5432/habit_tracker

AWS_REGION=eu-central-1
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_S3_BUCKET=your-bucket-name
AWS_S3_PREFIX=habit-reports
```

Для локальной разработки можно использовать MinIO или LocalStack и указать:

```env
AWS_ENDPOINT_URL=http://localhost:4566
```

API будет доступно по адресу:

```text
http://localhost:8000
```

Swagger UI:

```text
http://localhost:8000/docs
```

## Модель данных

### `habits`

| Поле | Тип | Описание |
|---|---|---|
| `id` | integer | Первичный ключ |
| `name` | string | Название привычки |
| `description` | string, nullable | Описание |
| `target_per_week` | integer | Целевое количество выполнений в неделю |
| `created_at` | timestamp | Дата создания |

### `habit_entries`

| Поле | Тип | Описание |
|---|---|---|
| `id` | integer | Первичный ключ |
| `habit_id` | integer | FK на `habits.id` |
| `entry_date` | date | Дата отметки |
| `completed` | boolean | Выполнена ли привычка |
| `note` | string, nullable | Комментарий |
| `created_at` | timestamp | Дата создания записи |

На пару `(habit_id, entry_date)` наложен уникальный индекс: одна привычка может иметь только одну отметку за день.

## API

### Проверка сервиса

```http
GET /health
```

Ответ:

```json
{"status": "ok"}
```

### Создать привычку

```http
POST /habits
Content-Type: application/json
```

```json
{
  "name": "Утренняя зарядка",
  "description": "15 минут упражнений",
  "target_per_week": 5
}
```

### Получить список привычек

```http
GET /habits
```

### Получить привычку

```http
GET /habits/1
```

### Обновить привычку

```http
PATCH /habits/1
Content-Type: application/json
```

```json
{
  "target_per_week": 7
}
```

### Удалить привычку

```http
DELETE /habits/1
```

### Отметить выполнение

```http
POST /habits/1/entries
Content-Type: application/json
```

```json
{
  "entry_date": "2026-10-19",
  "completed": true,
  "note": "Сделал зарядку после прогулки"
}
```

### Получить отметки

```http
GET /habits/1/entries?date_from=2026-10-01&date_to=2026-10-19
```

### Выгрузить отчёт в S3

```http
POST /reports/export?date_from=2026-10-01&date_to=2026-10-19
```

Ответ:

```json
{
  "bucket": "configured-in-settings",
  "key": "habit-reports/2026-10-19-habits-report.csv",
  "location": "[https://your-bucket-name.s3.eu-central-1.amazonaws.com/habit-reports/2026-10-19-habits-report.csv](https://your-bucket-name.s3.eu-central-1.amazonaws.com/habit-reports/2026-10-19-habits-report.csv)"
}
```

## Формат CSV-отчёта

```csv
habit_id,habit_name,target_per_week,entry_date,completed,note
1,Утренняя зарядка,5,2026-10-19,true,Сделал зарядку
```

## Настройка AWS S3

У пользователя или роли AWS должны быть разрешения как минимум на:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:PutObject"
      ],
      "Resource": "arn:aws:s3:::your-bucket-name/habit-reports/*"
    }
  ]
}
```

В продакшене предпочтительно использовать IAM Role вместо статических `AWS_ACCESS_KEY_ID` и `AWS_SECRET_ACCESS_KEY`.
