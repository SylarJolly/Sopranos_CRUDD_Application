# Sopranos CRUD App

A full-stack CRUD application for characters from *The Sopranos*.

- **Backend:** FastAPI + SQLAlchemy + SQLite (`app/`)
- **Frontend:** Flask + Jinja templates (`app/frontend/`). It talks to the API over HTTP only and never touches the database.
- **Tests:** pytest (`tests/`)

## File Structure

Sopranos_CRUDD_Application/
├── app/                        BACKEND (FastAPI API)
│   ├── main.py                 App setup, CORS, router registration
│   ├── database.py             SQLite engine, session, get_db dependency
│   ├── models.py               SQLAlchemy model (the characters table)
│   ├── schemas.py              Pydantic schemas (validation rules)
│   ├── routers/
│   │   └── characters.py       The five CRUD endpoints
│   ├── scripts/
│   │   └── populate_db.py      Seeds the database with 12 characters
│   └── frontend/               FRONTEND (Flask)
│       ├── app.py              Flask routes: list, details, add, edit, delete, undo
│       ├── api_client.py       All HTTP requests to the API
│       ├── templates/          Jinja pages (base, index, characters, character, form, 404, api_down)
│       └── static/             CSS and images (logo, guns, character photos)
├── tests/
│   ├── conftest.py             In-memory test database and fixtures
│   └── test_characters.py      33 pytest tests
├── sopranos.db                 SQLite database
├── requirements.txt            Dependencies
├── pyproject.toml              Project and pytest/Ruff settings
├── README.md                   How to set up and run
└── .github/workflows/ci.yaml   Runs Ruff and pytest on every push

## Setup

Run these once, from the project folder:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Run the app

Use two terminals, with the virtual environment activated in each.

**Terminal 1: start the backend** (API docs at http://localhost:8000/docs)

```bash
python -m uvicorn app.main:app --reload
```

**Terminal 2: start the frontend** (site at http://127.0.0.1:5000)

```bash
python app/frontend/app.py
```

Start the backend first. If it isn't running, the site shows a "data is unavailable" page.

## Run the tests

```bash
pytest
```

The tests use an in-memory database, so they don't change your real data.

## API endpoints

| Method | URL | Description |
|---|---|---|
| `GET` | `/characters/` | Read all (supports `skip`, `limit`, `name`) |
| `GET` | `/characters/{id}` | Read one |
| `POST` | `/characters/` | Create |
| `PUT` | `/characters/{id}` | Update |
| `DELETE` | `/characters/{id}` | Delete |

Each character has a `name`, `actor`, `role`, `status`, `first_season` and `last_season`. Two characters can't share the same name and actor (this returns `409`).

## Character photos

Photos go in `app/frontend/static/images/` and are named after the character in lowercase with hyphens, for example `tony-soprano.png`.

## Note
All code is greatly influenced by William Rochelle's Lab06 Starter Code (https://github.com/rochellew/csci_2910_labs/wiki/Lab-06:-Testing-Code-using-FastAPI) and his bluesky_flask_final code. 

