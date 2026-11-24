"""Flask frontend for the Sopranos API (full CRUD through HTTP requests)."""

import os

from flask import Flask, flash, redirect, render_template, request, url_for

from app.frontend import api_client as api
from app.frontend.api_client import ApiError, ApiUnavailable

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-only-change-me")

STATUSES = ["Alive", "Dead", "Imprisoned", "Unknown"]
FIELDS = ["name", "actor", "role", "status", "first_season"]


def _form_data() -> dict:
    """Read the form into the JSON shape the API expects."""
    data = {f: request.form.get(f, "").strip() for f in FIELDS}
    try:
        data["first_season"] = int(data["first_season"])
    except ValueError:
        pass  # leave the raw text; the API will reject it with a 422 we can show
    return data


@app.errorhandler(ApiUnavailable)
def api_down(_):
    return render_template(
        "error.html",
        title="API unreachable",
        message=f"Couldn't reach the API at {api.API_URL}. Is it running?",
    ), 503


@app.errorhandler(ApiError)
def api_error(exc):
    code = 404 if exc.status_code == 404 else 502
    return render_template(
        "error.html",
        title="Not found" if code == 404 else "API error",
        message="; ".join(exc.messages),
    ), code


@app.get("/")
def index():
    q = request.args.get("q", "").strip()
    return render_template("index.html", characters=api.list_characters(q or None), q=q)


@app.get("/characters/<int:character_id>")
def detail(character_id):
    return render_template("detail.html", c=api.get_character(character_id))


@app.route("/characters/new", methods=["GET", "POST"])
def create():
    if request.method == "POST":
        data = _form_data()
        try:
            created = api.create_character(data)
        except ApiError as exc:
            if exc.status_code in (409, 422):
                return render_template(
                    "form.html",
                    c=data,
                    errors=exc.messages,
                    statuses=STATUSES,
                    mode="create",
                ), 400
            raise
        flash(f"Added {created['name']}.", "ok")
        return redirect(url_for("detail", character_id=created["id"]))
    return render_template(
        "form.html",
        c={"status": "Alive", "first_season": 1},
        errors=[],
        statuses=STATUSES,
        mode="create",
    )


@app.route("/characters/<int:character_id>/edit", methods=["GET", "POST"])
def edit(character_id):
    if request.method == "POST":
        data = _form_data()
        try:
            updated = api.update_character(character_id, data)
        except ApiError as exc:
            if exc.status_code in (409, 422):
                return render_template(
                    "form.html",
                    c={**data, "id": character_id},
                    errors=exc.messages,
                    statuses=STATUSES,
                    mode="edit",
                ), 400
            raise
        flash(f"Saved changes to {updated['name']}.", "ok")
        return redirect(url_for("detail", character_id=character_id))
    return render_template(
        "form.html",
        c=api.get_character(character_id),
        errors=[],
        statuses=STATUSES,
        mode="edit",
    )


@app.post("/characters/<int:character_id>/delete")
def delete(character_id):
    name = api.get_character(character_id)["name"]
    api.delete_character(character_id)
    flash(f"Deleted {name}.", "ok")
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(port=5000, debug=True)
