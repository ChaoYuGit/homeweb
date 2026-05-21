import json
import os

from flask import (
    Flask,
    flash,
    redirect,
    render_template,
    request,
    send_from_directory,
    url_for,
)

from utils.auth import authenticate, create_user_session, load_config, login_required, logout_user
from utils.db import init_db, get_notes, create_note, update_note, delete_note
from utils.stock import get_stock_files
from utils.system import get_system_info

app = Flask(__name__)
app.config.from_mapping(
    SECRET_KEY=load_config()["secret_key"],
)

ALLOWED_EXTENSIONS = set()
FILE_ROOT = os.path.join(os.path.dirname(__file__), load_config().get("file_root", "served_files"))


def format_size(size):
    for unit in ("B", "KB", "MB", "GB"):
        if size < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} TB"


def list_files(dir_path):
    items = []
    for name in sorted(os.listdir(dir_path), key=str.lower):
        full = os.path.join(dir_path, name)
        rel = os.path.relpath(full, FILE_ROOT)
        stat = os.stat(full)
        items.append({
            "name": name,
            "rel_path": rel,
            "is_dir": os.path.isdir(full),
            "size": format_size(stat.st_size) if os.path.isfile(full) else "-",
            "modified": stat.st_mtime,
        })
    return items


# ── Auth Routes ──

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if authenticate(username, password):
            create_user_session()
            return redirect(url_for("dashboard"))
        flash("Invalid username or password", "error")
    return render_template("login.html")


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("login"))


# ── Dashboard ──

@app.route("/")
@app.route("/dashboard")
@login_required
def dashboard():
    info = get_system_info()
    return render_template("dashboard.html", info=info)


# ── File Browser ──

@app.route("/files")
@app.route("/files/")
@app.route("/files/<path:path>")
@login_required
def files(path=""):
    safe_path = os.path.normpath(os.path.join(FILE_ROOT, path))
    if not safe_path.startswith(os.path.realpath(FILE_ROOT)):
        flash("Access denied", "error")
        return redirect(url_for("files"))
    if not os.path.exists(safe_path):
        flash("Path not found", "error")
        return redirect(url_for("files"))
    if os.path.isfile(safe_path):
        return send_from_directory(os.path.dirname(safe_path), os.path.basename(safe_path))

    items = list_files(safe_path)
    current_path = safe_path
    relative_path = os.path.relpath(safe_path, FILE_ROOT) if safe_path != FILE_ROOT else ""

    parent_rel = None
    if relative_path:
        parent_rel = os.path.dirname(relative_path)

    return render_template(
        "files.html",
        items=items,
        current_path=current_path,
        relative_path=relative_path,
        parent_path=parent_rel if parent_rel != "" else None,
        file_root=FILE_ROOT,
    )


@app.route("/files/upload", methods=["POST"])
@login_required
def upload_file():
    path = request.form.get("path", "")
    safe_dir = os.path.normpath(os.path.join(FILE_ROOT, path))
    if not safe_dir.startswith(os.path.realpath(FILE_ROOT)):
        flash("Access denied", "error")
        return redirect(url_for("files"))
    os.makedirs(safe_dir, exist_ok=True)
    f = request.files.get("file")
    if f and f.filename:
        f.save(os.path.join(safe_dir, f.filename))
        flash("File uploaded", "success")
    return redirect(url_for("files", path=path))


@app.route("/files/delete", methods=["POST"])
@login_required
def delete_file():
    path = request.form.get("path", "")
    full = os.path.normpath(os.path.join(FILE_ROOT, path))
    if full.startswith(os.path.realpath(FILE_ROOT)) and os.path.exists(full):
        if os.path.isfile(full):
            os.remove(full)
            flash("File deleted", "success")
        elif os.path.isdir(full):
            os.rmdir(full)
            flash("Directory deleted", "success")
    else:
        flash("Access denied", "error")
    parent = os.path.dirname(path)
    return redirect(url_for("files", path=parent))


@app.route("/files/download/<path:path>")
@login_required
def download_file(path):
    safe_path = os.path.normpath(os.path.join(FILE_ROOT, path))
    if not safe_path.startswith(os.path.realpath(FILE_ROOT)) or not os.path.isfile(safe_path):
        flash("Access denied", "error")
        return redirect(url_for("files"))
    return send_from_directory(os.path.dirname(safe_path), os.path.basename(safe_path))


# ── Stock Reports ──

@app.route("/stock")
@login_required
def stock():
    reports = get_stock_files()
    return render_template("stock.html", reports=reports)


@app.route("/daily")
@login_required
def daily():
    reports = get_stock_files()
    return render_template("daily.html", reports=reports)


# ── Notes ──

@app.route("/notes")
@login_required
def notes():
    all_notes = get_notes()
    return render_template("notes.html", notes=all_notes)


@app.route("/notes/create", methods=["POST"])
@login_required
def notes_create():
    title = request.form["title"]
    content = request.form["content"]
    create_note(title, content)
    flash("Note created", "success")
    return redirect(url_for("notes"))


@app.route("/notes/<int:note_id>/edit", methods=["POST"])
@login_required
def notes_edit(note_id):
    title = request.form["title"]
    content = request.form["content"]
    update_note(note_id, title, content)
    flash("Note updated", "success")
    return redirect(url_for("notes"))


@app.route("/notes/<int:note_id>/delete", methods=["POST"])
@login_required
def notes_delete(note_id):
    delete_note(note_id)
    flash("Note deleted", "success")
    return redirect(url_for("notes"))


if __name__ == "__main__":
    os.makedirs(FILE_ROOT, exist_ok=True)
    init_db()
    config = load_config()
    app.run(host=config["host"], port=config["port"], debug=False)
