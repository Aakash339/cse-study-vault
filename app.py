from flask import Flask, render_template, request, redirect, send_from_directory, flash, session
import os
import sqlite3
from werkzeug.utils import secure_filename

#this is a testing line

app = Flask(__name__)

app.secret_key = "cse-study-vault-secret-key"

def admin_required():
    if "admin" not in session:
        return redirect("/admin-login")
    return None

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

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS subjects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            semester TEXT,
            subject_name TEXT,
            has_notes INTEGER,
            has_pyqs INTEGER,
            has_lab INTEGER,
            has_important INTEGER
        )
    """)


    cursor.execute("""
        CREATE TABLE IF NOT EXISTS semesters (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            semester_name TEXT,
            is_active INTEGER
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
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT semester_name
        FROM semesters
        WHERE is_active = 1
        ORDER BY CAST(REPLACE(semester_name, 'Semester ', '') AS INTEGER)
    """)

    semesters = cursor.fetchall()
    conn.close()

    return render_template("dashboard.html", semesters=semesters)

@app.route("/admin-login", methods=["GET", "POST"])
def admin_login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        if email == "aakash.cse24@cmrit.ac.in" and password == "@@k@sh18":

            session["admin"] = True

            flash("Login successful!")

            return redirect("/admin-panel")

        else:

            flash("Invalid email or password!")

            return redirect("/admin-login")

    return render_template("admin-login.html")

@app.route("/admin-panel")
def admin_panel():

    if "admin" not in session:
        return redirect("/admin-login")

    return render_template("admin-panel.html")

@app.route("/upload", methods=["GET", "POST"])
def upload():

    auth = admin_required()
    if auth:
        return auth
    
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

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

            cursor.execute("""
                INSERT INTO materials
                (title, semester, subject, resource_type, filename)
                VALUES (?, ?, ?, ?, ?)
            """, (
                title,
                semester,
                subject,
                resource_type,
                filename
            ))

            conn.commit()

            conn.close()

            flash("Material uploaded successfully!")
            return redirect("/admin-panel")

    cursor.execute("""
        SELECT semester_name
        FROM semesters
        WHERE is_active = 1
        ORDER BY CAST(REPLACE(semester_name, 'Semester ', '') AS INTEGER)
    """)

    semesters = cursor.fetchall()

    conn.close()

    return render_template("upload.html", semesters=semesters)

def get_subjects(semester):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT subject_name
        FROM subjects
        WHERE semester = ?
    """, (semester,))

    subjects = cursor.fetchall()
    conn.close()

    return subjects


@app.route("/semester3")
def semester3():
    subjects = get_subjects("Semester 3")
    return render_template("semester.html", semester="Semester 3", subjects=subjects)


@app.route("/semester4")
def semester4():
    subjects = get_subjects("Semester 4")
    return render_template("semester.html", semester="Semester 4", subjects=subjects)


@app.route("/semester5")
def semester5():
    subjects = get_subjects("Semester 5")
    return render_template("semester.html", semester="Semester 5", subjects=subjects)


@app.route("/semester6")
def semester6():
    subjects = get_subjects("Semester 6")
    return render_template("semester.html", semester="Semester 6", subjects=subjects)


@app.route("/semester7")
def semester7():
    subjects = get_subjects("Semester 7")
    return render_template("semester.html", semester="Semester 7", subjects=subjects)


@app.route("/semester8")
def semester8():
    subjects = get_subjects("Semester 8")
    return render_template("semester.html", semester="Semester 8", subjects=subjects)

@app.route("/resources")
def resources_redirect():
    return redirect("/dashboard")

@app.route("/resources/<semester>/<subject>")
def resources(semester, subject):

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT has_notes, has_pyqs, has_lab, has_important
        FROM subjects
        WHERE semester = ? AND subject_name = ?
    """, (semester, subject))

    subject_data = cursor.fetchone()

    conn.close()

    return render_template(
        "resources.html",
        semester=semester,
        subject=subject,
        subject_data=subject_data
    )

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

@app.route("/admin-resources")
def admin_resources():
    auth = admin_required()
    if auth:
        return auth

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, title, semester, subject, resource_type, filename
        FROM materials
        ORDER BY 
        CAST(REPLACE(semester, 'Semester ', '') AS INTEGER),
        subject,
        resource_type
    """)

    materials = cursor.fetchall()
    conn.close()

    return render_template("admin-resources.html", materials=materials)


@app.route("/delete-material/<int:id>")
def delete_material(id):
    auth = admin_required()
    if auth:
        return auth
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("SELECT filename FROM materials WHERE id = ?", (id,))
    file = cursor.fetchone()

    if file:
        file_path = os.path.join(app.config["UPLOAD_FOLDER"], file[0])

        if os.path.exists(file_path):
            os.remove(file_path)

        cursor.execute("DELETE FROM materials WHERE id = ?", (id,))
        conn.commit()

    conn.close()
    flash("Material deleted successfully!")
    return redirect("/admin-resources")

@app.route("/manage-subjects", methods=["GET", "POST"])
def manage_subjects():
    auth = admin_required()
    if auth:
        return auth
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    if request.method == "POST":

        semester = request.form["semester"]
        subject_name = request.form["subject_name"]

        has_notes = 1 if "has_notes" in request.form else 0
        has_pyqs = 1 if "has_pyqs" in request.form else 0
        has_lab = 1 if "has_lab" in request.form else 0
        has_important = 1 if "has_important" in request.form else 0

        cursor.execute("""
            INSERT INTO subjects
            (semester, subject_name, has_notes, has_pyqs, has_lab, has_important)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            semester,
            subject_name,
            has_notes,
            has_pyqs,
            has_lab,
            has_important
        ))

        conn.commit()
        flash("Subject added successfully!")

    cursor.execute("""
        SELECT * FROM subjects
    """)
    subjects = cursor.fetchall()

    cursor.execute("""
        SELECT semester_name
        FROM semesters
        WHERE is_active = 1
        ORDER BY CAST(REPLACE(semester_name, 'Semester ', '') AS INTEGER)
    """)
    semesters = cursor.fetchall()

    conn.close()

    return render_template(
        "manage-subjects.html",
        subjects=subjects,
        semesters=semesters
    )

@app.route("/delete-subject/<int:id>")
def delete_subject(id):
    auth = admin_required()
    if auth:
        return auth
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("DELETE FROM subjects WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    flash("Subject deleted successfully!")
    return redirect("/manage-subjects")


@app.route("/edit-subject/<int:id>", methods=["GET", "POST"])
def edit_subject(id):
    auth = admin_required()
    if auth:
        return auth
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    if request.method == "POST":
        semester = request.form["semester"]
        subject_name = request.form["subject_name"]

        has_notes = 1 if "has_notes" in request.form else 0
        has_pyqs = 1 if "has_pyqs" in request.form else 0
        has_lab = 1 if "has_lab" in request.form else 0
        has_important = 1 if "has_important" in request.form else 0

        cursor.execute("""
            UPDATE subjects
            SET semester = ?, subject_name = ?, has_notes = ?, has_pyqs = ?, has_lab = ?, has_important = ?
            WHERE id = ?
        """, (semester, subject_name, has_notes, has_pyqs, has_lab, has_important, id))

        conn.commit()
        conn.close()
        flash("Subject updated successfully!")
        return redirect("/manage-subjects")

    cursor.execute("SELECT * FROM subjects WHERE id = ?", (id,))
    subject = cursor.fetchone()

    conn.close()

    return render_template("edit-subject.html", subject=subject)

@app.route("/get-subjects/<semester>")
def get_subjects_api(semester):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT subject_name
        FROM subjects
        WHERE semester = ?
    """, (semester,))

    subjects = cursor.fetchall()
    conn.close()

    subject_list = [subject[0] for subject in subjects]

    return {"subjects": subject_list}


@app.route("/edit-material/<int:id>", methods=["GET", "POST"])
def edit_material(id):
    auth = admin_required()
    if auth:
        return auth
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    if request.method == "POST":
        title = request.form["title"]
        semester = request.form["semester"]
        subject = request.form["subject"]
        resource_type = request.form["resource_type"]
        file = request.files["file"]

        if file and file.filename != "":
            filename = secure_filename(file.filename)
            save_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            file.save(save_path)

            cursor.execute("""
                UPDATE materials
                SET title = ?, semester = ?, subject = ?, resource_type = ?, filename = ?
                WHERE id = ?
            """, (title, semester, subject, resource_type, filename, id))
        else:
            cursor.execute("""
                UPDATE materials
                SET title = ?, semester = ?, subject = ?, resource_type = ?
                WHERE id = ?
            """, (title, semester, subject, resource_type, id))

        conn.commit()
        conn.close()
        flash("Material updated successfully!")
        return redirect("/admin-resources")

    cursor.execute("SELECT * FROM materials WHERE id = ?", (id,))
    material = cursor.fetchone()

    conn.close()

    return render_template("edit-material.html", material=material)


@app.route("/manage-semesters", methods=["GET", "POST"])
def manage_semesters():
    auth = admin_required()
    if auth:
        return auth
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    if request.method == "POST":
        semester_name = request.form["semester_name"]
        is_active = 1 if "is_active" in request.form else 0

        cursor.execute("""
            INSERT INTO semesters (semester_name, is_active)
            VALUES (?, ?)
        """, (semester_name, is_active))

        conn.commit()
        flash("Semester added successfully!")

    cursor.execute("""
        SELECT * FROM semesters
        ORDER BY CAST(REPLACE(semester_name, 'Semester ', '') AS INTEGER)
    """)
    semesters = cursor.fetchall()

    conn.close()

    return render_template("manage-semesters.html", semesters=semesters)

@app.route("/delete-semester/<int:id>")
def delete_semester(id):
    auth = admin_required()
    if auth:
        return auth
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("DELETE FROM semesters WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    flash("Semester deleted successfully!")
    return redirect("/manage-semesters")


@app.route("/edit-semester/<int:id>", methods=["GET", "POST"])
def edit_semester(id):
    auth = admin_required()
    if auth:
        return auth
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    if request.method == "POST":
        semester_name = request.form["semester_name"]
        is_active = 1 if "is_active" in request.form else 0

        cursor.execute("""
            UPDATE semesters
            SET semester_name = ?, is_active = ?
            WHERE id = ?
        """, (semester_name, is_active, id))

        conn.commit()
        conn.close()
        flash("Semester updated successfully!")
        return redirect("/manage-semesters")

    cursor.execute("SELECT * FROM semesters WHERE id = ?", (id,))
    semester = cursor.fetchone()

    conn.close()

    return render_template("edit-semester.html", semester=semester)



@app.route("/semester/<semester>")
def semester_dynamic(semester):
    subjects = get_subjects(semester)
    return render_template("semester.html", semester=semester, subjects=subjects)

@app.route("/view-file/<filename>")
def view_file(filename):
    return send_from_directory(
        app.config["UPLOAD_FOLDER"],
        filename,
        as_attachment=False
    )

@app.route("/logout")
def logout():
    session.pop("admin", None)
    flash("Logged out successfully!")
    return redirect("/admin-login")

if __name__ == "__main__":
    app.run(debug=True)