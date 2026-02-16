from flask import Flask, request, render_template_string
import sqlite3
import time
import os

app = Flask(__name__)

def init_db():
    con = sqlite3.connect("clips.db")
    cur = con.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS clips (
        key TEXT PRIMARY KEY,
        content TEXT,
        expiry INTEGER
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
        duration = int(request.form["duration"])

        expiry_time = int(time.time()) + duration

        con = sqlite3.connect("clips.db")
        cur = con.cursor()
        cur.execute("REPLACE INTO clips VALUES (?, ?, ?)", (key, text, expiry_time))
        con.commit()
        con.close()

        return f"Saved! Share this secret code: {key}"

    return render_template_string("""
<!DOCTYPE html>
<html>
<head>
<title>a1ert</title>
<style>
body {
    font-family: Arial;
    background: linear-gradient(to right, #1e3c72, #2a5298);
    color: white;
    text-align: center;
}
.box {
    background: rgba(0,0,0,0.5);
    padding: 20px;
    border-radius: 15px;
    width: 400px;
    margin: auto;
}
input, textarea, select, button {
    width: 90%;
    padding: 10px;
    margin: 5px;
    border-radius: 10px;
    border: none;
}
button {
    background: #00ffcc;
    font-weight: bold;
}
</style>
</head>
<body>
<h1>a1ert</h1>
<div class="box">
<form method="post">
<input name="key" placeholder="Secret code"><br>
<textarea name="text" placeholder="Paste your message"></textarea><br>

<select name="duration">
<option value="60">1 Minute</option>
<option value="300">5 Minutes</option>
<option value="3600">1 Hour</option>
<option value="86400">1 Day</option>
</select><br>

<button>Save</button>
</form>
<hr>
<form action="/get">
<input name="key" placeholder="Enter secret code">
<button>Get</button>
</form>
</div>
</body>
</html>
""")

@app.route("/get")
def get_clip():
    key = request.args.get("key")

    con = sqlite3.connect("clips.db")
    cur = con.cursor()
    cur.execute("SELECT content, expiry FROM clips WHERE key=?", (key,))
    row = cur.fetchone()

    if row:
        content, expiry = row
        if expiry < int(time.time()):
            cur.execute("DELETE FROM clips WHERE key=?", (key,))
            con.commit()
            con.close()
            return "This clip has expired"
        con.close()
        return content
    else:
        con.close()
        return "No clip found"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
