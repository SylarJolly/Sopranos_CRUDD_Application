import os
import re

import api_client
import requests
from flask import Flask, abort, redirect, render_template, request, session, url_for

app = Flask(__name__)
app.secret_key = (
    "sopranos-dev-key"
)

FIELDS = ["name", "actor", "role", "status", "first_season", "last_season"]

PHOTO_FOLDER = os.path.join(app.static_folder, "images")

# saves uploade PNG as <character-name>.png

def save_photo(name):
    photo_file = request.files.get("photo")
    if photo_file and photo_file.filename.lower().endswith(".png"):
        photo_file.save(os.path.join(PHOTO_FOLDER, photo(name)))

@app.context_processor
def inject_undo():
    return {"undo": session.get("undo")}


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
        save_photo(created["name"])
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
            session["undo"] = {
                "action": "edit",
                "id": character_id,
                "label": f"Edited {found['name']}.",
                "character": {field: found[field] for field in FIELDS},
            }
        except requests.HTTPError as error:
            return render_template(
                "form.html",
                character={**data, "id": character_id},
                error=api_error_message(error),
            )
        save_photo(data["name"])                                  
        return redirect(url_for("character", character_id=character_id))
    return render_template("form.html", character=found)


@app.route("/delete/<int:character_id>", methods=["POST"])
def delete(character_id):
    found = api_client.get_character(character_id)
    if found is None:
        abort(404)
    api_client.delete_character(character_id)
    session["undo"] = {
        "action": "delete",
        "label": f"Deleted {found['name']}.",
        "character": {field: found[field] for field in FIELDS},
    }
    return redirect(url_for("characters"))


@app.route("/undo", methods=["POST"])
def undo():
    last = session.pop("undo", None)
    if last is None:
        return redirect(url_for("characters"))
    try:
        if last["action"] == "delete":
            api_client.add_character(last["character"])
            return redirect(url_for("characters"))
        api_client.update_character(last["id"], last["character"])
        return redirect(url_for("character", character_id=last["id"]))
    except requests.HTTPError:
        return redirect(url_for("characters"))


@app.errorhandler(404)
def page_not_found(error):
    return render_template("404.html"), 404


@app.errorhandler(requests.RequestException)
def api_unavailable(error):
    return render_template("api_down.html"), 503

#GEN AI used for this function, so that images don't disappear when undoing a delete
@app.template_filter("photo")
def photo(name):
    # "Dr. Jennifer Melfi" -> "dr-jennifer-melfi.png"
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-") + ".png"


if __name__ == "__main__":
    app.run(debug=True)
