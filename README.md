# Лабораторна робота 1. CRUD

![tests](https://github.com/Callibri/lab1/actions/workflows/tests.yml/badge.svg)

REST API для обліку фільмів і їхніх касових зборів. Стек: Python, FastAPI, SQLAlchemy, SQLite, JWT.

Предметна область: фільми, касові звіти (збори й кількість проданих квитків за дату та регіон), аналітика (підсумки по фільму, топ фільмів, збори за регіонами).

## Встановлення

Потрібен Python 3.11 або новіший.

Windows (PowerShell):

```
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Linux / macOS:

```
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Запуск

```
uvicorn app.main:app --reload
```

Документація та перевірка запитів у браузері: http://127.0.0.1:8000/docs.
Для захищених ендпоінтів спочатку виконайте `POST /auth/register` і `POST /auth/login`, потім натисніть Authorize і вставте `access_token`.

База даних за замовчуванням: файл `boxoffice.db` у поточній папці. Інший шлях задається змінною `DATABASE_URL`, ключ підпису токенів змінною `SECRET_KEY`.

## Тести

```
pytest -v
```

- `tests/unit` перевіряють правила валідації без бази даних;
- `tests/integration` перевіряють ендпоінти (HTTP-запит і відповідь) разом з базою даних (SQLite у пам'яті).

## Ендпоінти

| Метод | Шлях | Призначення |
|---|---|---|
| POST | `/auth/register` | реєстрація |
| POST | `/auth/login` | вхід, повертає JWT |
| POST, GET | `/movies` | створення, список (`genre`, `year`, `limit`, `offset`) |
| GET, PUT, DELETE | `/movies/{id}` | перегляд, оновлення, видалення фільму |
| POST, GET | `/movies/{id}/reports` | додавання звіту, список (`date_from`, `date_to`, `region`) |
| PUT, DELETE | `/reports/{id}` | зміна, видалення звіту |
| GET | `/movies/{id}/summary` | збори, квитки, середня ціна квитка, ROI, збори за регіонами |
| GET | `/analytics/top` | топ фільмів за зборами |
| GET | `/analytics/regions` | збори за регіонами |

Усі ендпоінти, крім `/auth/*`, без токена повертають 401. Помилки: 400 невалідні дані, 404 не знайдено, 409 конфлікт.

## Правила (інваріанти)

- email має коректний формат, пароль не коротший за 8 символів;
- назва і жанр фільму не порожні, бюджет більший за нуль;
- пара «назва + дата виходу» унікальна;
- дата звіту не в майбутньому і не раніша за дату виходу фільму;
- регіон це код із двох літер, збори й кількість квитків не від'ємні;
- пара «фільм + дата + регіон» унікальна.

## Документи

- `docs/use-cases.md` юзкейси;
- `docs/self-analysis.md` відповіді на питання для самоаналізу.
