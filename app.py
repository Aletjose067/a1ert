from flask import Flask, request, render_template_string
import sqlite3

app = Flask(__name__)

def init_db():
    con = sqlite3.connect("clips.db")
    cur = con.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS clips (
        key TEXT PRIMARY KEY,
        content TEXT
    )
    """)
    con.commit()
    con.close()

init_db()

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        key = request.form["key"]
        text = request.form["text"]

        con = sqlite3.connect("clips.db")
        cur = con.cursor()
        cur.execute("REPLACE INTO clips VALUES (?, ?)", (key, text))
        con.commit()
        con.close()

        return f"Saved! Share this secret code: {key}"

    return render_template_string("""
    <h2>Create a1ert clip</h2>
    <form method="post">
        Secret code: <input name="key"><br><br>
        <textarea name="text" rows="10" cols="50"></textarea><br>
        <button>Save</button>
    </form>
    <hr>
    <h2>Get clip</h2>
    <form action="/get">
        Secret code: <input name="key">
        <button>Get</button>
    </form>
    """)

@app.route("/get")
def get_clip():
    key = request.args.get("key")

    con = sqlite3.connect("clips.db")
    cur = con.cursor()
    cur.execute("SELECT content FROM clips WHERE key=?", (key,))
    row = cur.fetchone()
    con.close()

    if row:
        return row[0]
    else:
        return "No clip found"

import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)




