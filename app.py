from flask import Flask, render_template, request, redirect, flash
from werkzeug.utils import secure_filename
import os
import random
import sqlite3

os.makedirs("static/audio", exist_ok=True)
app = Flask(__name__)
app.secret_key = "Coptic_Hymns_2026_Project_@123"
@app.route("/")
def home():
    categories = [
        "رأس السنة",
        "الميلاد",
        "الصوم الكبير",
        "أسبوع الآلام",
        "القيامة",
        "العذراء",
        "النيروز",
        "التسليم",
        "التوبة",
        "أخرى"
    ]
    search = request.args.get("search", "")
    category = request.args.get("category", "")
    connection = sqlite3.connect("database.db")
    cursor = connection.cursor()
    if search and category:
        cursor.execute(
        "SELECT * FROM hymns WHERE title LIKE ? AND category = ?",
        ("%" + search + "%", category)
    )
    elif search:
        cursor.execute(
        "SELECT * FROM hymns WHERE title LIKE ?",
        ("%" + search + "%",)
    )
    elif category:
        cursor.execute(
        "SELECT * FROM hymns WHERE category = ?",
        (category,)
    )
    else:
        cursor.execute("SELECT * FROM hymns")
    hymns = cursor.fetchall()
    connection.close()
    return render_template("index.html", hymns=hymns, search=search, category=category, categories=categories)
@app.route("/add", methods=["GET", "POST"])
def add_hymn():
    if request.method == "POST":
        title = request.form["title"]
        category = request.form["category"]
        audio = request.files["audio"]
        lyrics = request.form.get("lyrics", "")
        audio_name = ""
        if audio and audio.filename != "":
            audio_name = secure_filename(audio.filename)
            audio.save(os.path.join("static", "audio", audio_name))
        connection = sqlite3.connect("database.db")
        cursor = connection.cursor()
        cursor.execute("""
                       INSERT INTO hymns (title, category, audio, lyrics) VALUES (?, ?, ?, ?)""", 
                       (title, category, audio_name, lyrics))
        connection.commit()
        connection.close()
        flash("تم اضافة الترنيمة بنجاح")
        return redirect("/")
    return render_template("add_hymn.html")
@app.route("/delete/<int:id>",
           methods=["POST"])
def delete_hymn(id):
        connection = sqlite3.connect("database.db")
        cursor = connection.cursor()
        cursor.execute("DELETE FROM hymns WHERE id = ?", (id,))
        connection.commit()
        connection.close()
        flash("تم حذف الترنيمة بنجاح")
        next_page = request.form.get("next", "/")
        return redirect(next_page)
@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit_hymn(id):
    connection = sqlite3.connect("database.db")
    cursor = connection.cursor()
    if request.method == "POST":
        title = request.form["title"]
        category = request.form["category"]
        audio = request.files["audio"]
        lyrics = request.form.get("lyrics", "")

        cursor.execute("SELECT * FROM hymns WHERE id = ?", (id,))
        current_hymn = cursor.fetchone()
        audio_name = current_hymn[3]

        if audio and audio.filename != "":
            audio_name = secure_filename(audio.filename)
            audio.save(os.path.join("static", "audio", audio_name))
        cursor.execute("""
                       UPDATE hymns SET title = ?, category = ?, audio = ?, lyrics = ? WHERE id = ?""",
                       (title, category, audio_name, lyrics, id)
                       )
        connection.commit()
        connection.close()
        flash("تم تعديل الترنيمة بنجاح")
        return redirect("/")
    cursor.execute("SELECT * FROM hymns WHERE id = ?", (id,))
    hymn = cursor.fetchone()

    connection.close()
    return render_template("edit_hymn.html", hymn=hymn)
@app.route("/favorite/<int:id>", methods=["POST"])
def favorite(id):
    connection = sqlite3.connect("database.db")
    cursor = connection.cursor()
    cursor.execute("SELECT favorite FROM hymns WHERE id = ?", (id,))
    current = cursor.fetchone()[0]

    if current == 1:
        new_value = 0
    else:
        new_value = 1
    cursor.execute(
        "UPDATE hymns SET favorite = ? WHERE id = ?",
        (new_value, id)
    )
    connection.commit()
    connection.close()
    next_page = request.form.get("next", "/")
    return redirect(next_page)
@app.route("/favorites")
def favorites():
    search = request.args.get("search", "")
    connection = sqlite3.connect("database.db")
    cursor = connection.cursor()
    if search:
        cursor.execute("SELECT * FROM hymns WHERE favorite = 1 AND title LIKE ?",
            ("%" + search + "%",)
        )
    else:
        cursor.execute("SELECT * FROM hymns WHERE favorite = 1")
    hymns = cursor.fetchall()

    connection.close()

    return render_template("favorites.html", hymns=hymns, search=search)
@app.route("/today")
def today():
    connection = sqlite3.connect("database.db")
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM hymns")
    hymns = cursor.fetchall()
    if not hymns:
        connection.close()
        flash("لا توجد ترانيم حاليا")
        return redirect("/")
    hymn = random.choice(hymns)
    connection.close()
    return render_template("listen.html", hymn=hymn)
@app.route("/listen/<int:id>")
def listen(id):
    connection = sqlite3.connect("database.db")
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM hymns WHERE id = ?", (id,))
    hymn = cursor.fetchone()
    connection.close()
    return render_template("listen.html", hymn=hymn)
@app.route("/contact")
def contact():
    return render_template("contact.html")

if __name__ == "__main__":
    app.run(debug=True)