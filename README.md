# Sopranos CRUD App

A full-stack CRUD application for characters from *The Sopranos*.

- **Backend:** FastAPI + SQLAlchemy + SQLite (`app/`)
- **Frontend:** Flask + Jinja templates (`app/frontend/`). It talks to the API over HTTP only and never touches the database.
- **Tests:** pytest (`tests/`)

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
