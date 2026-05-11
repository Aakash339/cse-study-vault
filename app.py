from flask import Flask, render_template, request, redirect
import os
import sqlite3
from werkzeug.utils import secure_filename

#this is a testing line

app = Flask(__name__)

UPLOAD_FOLDER = "static/uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def init_db():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS materials (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            semester TEXT,
            subject TEXT,
            resource_type TEXT,
            filename TEXT
        )
    """)

    conn.commit()
    conn.close()


init_db()


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")


@app.route("/admin-login")
def admin_login():
    return render_template("admin-login.html")


@app.route("/admin-panel")
def admin_panel():
    return render_template("admin-panel.html")


@app.route("/upload", methods=["GET", "POST"])
def upload():
    if request.method == "POST":
        title = request.form["title"]
        semester = request.form["semester"]
        subject = request.form["subject"]
        resource_type = request.form["resource_type"]
        file = request.files["file"]

        if file:
            filename = secure_filename(file.filename)
            save_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            file.save(save_path)

            conn = sqlite3.connect("database.db")
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO materials (title, semester, subject, resource_type, filename)
                VALUES (?, ?, ?, ?, ?)
            """, (title, semester, subject, resource_type, filename))

            conn.commit()
            conn.close()

            return redirect("/admin-panel")

    return render_template("upload.html")


@app.route("/semester3")
def semester3():
    return render_template("semester3.html")


@app.route("/semester4")
def semester4():
    return render_template("semester4.html")


@app.route("/semester5")
def semester5():
    return render_template("semester5.html")


@app.route("/semester6")
def semester6():
    return render_template("semester6.html")


@app.route("/semester7")
def semester7():
    return render_template("semester7.html")


@app.route("/semester8")
def semester8():
    return render_template("semester8.html")

@app.route("/resources")
def resources_redirect():
    return redirect("/dashboard")

@app.route("/resources/<semester>/<subject>")
def resources(semester, subject):
    return render_template("resources.html", semester=semester, subject=subject)


def get_materials(semester, subject, resource_type):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT title, semester, subject, filename
        FROM materials
        WHERE semester = ? AND subject = ? AND resource_type = ?
    """, (semester, subject, resource_type))

    materials = cursor.fetchall()
    conn.close()

    return materials


@app.route("/materials/<semester>/<subject>/<resource_type>")
def materials_page(semester, subject, resource_type):
    materials = get_materials(semester, subject, resource_type)

    if resource_type == "Notes":
        return render_template("notes.html", materials=materials, semester=semester, subject=subject)

    elif resource_type == "PYQs":
        return render_template("pyqs.html", materials=materials, semester=semester, subject=subject)

    elif resource_type == "Lab Programs":
        return render_template("lab.html", materials=materials, semester=semester, subject=subject)

    elif resource_type == "Important Questions":
        return render_template("important.html", materials=materials, semester=semester, subject=subject)

    return "Invalid resource type"


if __name__ == "__main__":
    app.run(debug=True)