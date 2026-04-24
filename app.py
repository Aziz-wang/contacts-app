from flask import Flask, render_template, request, redirect, jsonify
import sqlite3

app = Flask(__name__)

# 🔌 Connexion DB
def get_db():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn

# 🧱 INIT DB
def init_db():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT,
            phone TEXT,
            email TEXT,
            telegram TEXT
        )
    """)

    conn.commit()
    conn.close()

init_db()

# 🏠 HOME + SEARCH
@app.route("/")
def index():
    search = request.args.get("search")

    conn = get_db()
    cursor = conn.cursor()

    if search:
        cursor.execute("SELECT * FROM contacts WHERE full_name LIKE ?", ('%' + search + '%',))
    else:
        cursor.execute("SELECT * FROM contacts")

    contacts = cursor.fetchall()
    conn.close()

    return render_template("index.html", contacts=contacts)

# ➕ ADD CONTACT
@app.route("/add", methods=["POST"])
def add():
    data = request.form

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO contacts (full_name, phone, email, telegram)
        VALUES (?, ?, ?, ?)
    """, (
        data["full_name"],
        data["phone"],
        data["email"],
        data["telegram"]
    ))

    conn.commit()
    conn.close()

    return redirect("/")

# ✏️ UPDATE CONTACT
@app.route("/update/<int:id>", methods=["POST"])
def update(id):
    data = request.form

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE contacts
        SET full_name=?, phone=?, email=?, telegram=?
        WHERE id=?
    """, (
        data["full_name"],
        data["phone"],
        data["email"],
        data["telegram"],
        id
    ))

    conn.commit()
    conn.close()

    return redirect("/")

# ❌ DELETE CONTACT
@app.route("/delete/<int:id>")
def delete(id):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM contacts WHERE id=?", (id,))

    conn.commit()
    conn.close()

    return redirect("/")

# 📱 API JSON (mobile)
@app.route("/api/contacts")
def api_contacts():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM contacts")
    rows = cursor.fetchall()

    conn.close()

    result = []
    for r in rows:
        result.append({
            "id": r["id"],
            "full_name": r["full_name"],
            "phone": r["phone"],
            "email": r["email"],
            "telegram": r["telegram"]
        })

    return jsonify(result)

# ▶️ RUN SERVER
if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=10000,
        debug=True
    )
