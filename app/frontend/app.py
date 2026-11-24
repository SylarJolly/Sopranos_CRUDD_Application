import api_client
import requests
from flask import Flask, abort, redirect, render_template, request, url_for

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/characters")
def characters():
    name = request.args.get("name")
    shown = api_client.get_characters(name)
    return render_template("characters.html", characters=shown, name=name)


@app.route("/character/<int:character_id>")
def character(character_id):
    found = api_client.get_character(character_id)
    if found is None:
        abort(404)
    return render_template("character.html", character=found)


def read_form():
    return {
        "name": request.form.get("name", "").strip(),
        "actor": request.form.get("actor", "").strip(),
        "role": request.form.get("role", "").strip(),
        "status": request.form.get("status", "").strip(),
        "first_season": request.form.get("first_season", type=int),
        "last_season": request.form.get("last_season", type=int),
    }


def api_error_message(error):
    # 409 sends a text message; 422 sends a list of problems
    detail = error.response.json().get("detail")
    if isinstance(detail, str):
        return detail
    return "Please check every field. Seasons must be between 1 and 6."


@app.route("/add", methods=["GET", "POST"])
def add():
    if request.method == "POST":
        data = read_form()
        try:
            created = api_client.add_character(data)
        except requests.HTTPError as error:
            return render_template(
                "form.html", character=data, error=api_error_message(error)
            )
        return redirect(url_for("character", character_id=created["id"]))
    return render_template("form.html", character={})


@app.route("/edit/<int:character_id>", methods=["GET", "POST"])
def edit(character_id):
    found = api_client.get_character(character_id)
    if found is None:
        abort(404)
    if request.method == "POST":
        data = read_form()
        try:
            api_client.update_character(character_id, data)
        except requests.HTTPError as error:
            return render_template(
                "form.html",
                character={**data, "id": character_id},
                error=api_error_message(error),
            )
        return redirect(url_for("character", character_id=character_id))
    return render_template("form.html", character=found)


@app.route("/delete/<int:character_id>", methods=["POST"])
def delete(character_id):
    api_client.delete_character(character_id)
    return redirect(url_for("characters"))


# Error handler for custom 404 page
@app.errorhandler(404)
def page_not_found(error):
    return render_template("404.html"), 404


# If the API is down, too slow, or sends an error
@app.errorhandler(requests.RequestException)
def api_unavailable(error):
    return render_template("api_down.html"), 503
