from flask import Flask, render_template, request, redirect, url_for, session
from game import MonopolyGame
import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env

app = Flask(__name__)
app.secret_key = "replace_this_with_a_random_secret"
game = MonopolyGame()
users = set()


@app.route("/", methods=["GET", "POST"])
def home():
    return login()


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        # Use the same credentials as the db container
        db_user = os.getenv("POSTGRES_USER", "nihar")
        db_pass = os.getenv("POSTGRES_PASSWORD")
        if username == db_user and password == db_pass:
            session["username"] = username
            game.start_game([username])
            return redirect(url_for("play"))
        else:
            return render_template("login.html", error="Invalid username or password.")
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect(url_for("login"))


@app.route("/play", methods=["GET", "POST"])
def play():
    if "username" not in session:
        return redirect(url_for("login"))
    if not game.started:
        return redirect(url_for("login"))
    message = ""
    if request.method == "POST":
        action = request.form.get("action")
        if action == "draw":
            message = game.draw_card()
        elif action == "play":
            card_idx = int(request.form.get("card_idx"))
            message = game.play_card(card_idx)
        elif action == "end_turn":
            game.next_turn()
    current_player = game.players[game.current_player_idx]
    return render_template(
        "play.html", game=game, current_player=current_player, message=message
    )


@app.route("/admin", methods=["GET", "POST"])
def admin():
    message = ""
    # Connect to DB to fetch users
    conn = psycopg2.connect(
        dbname="monopoly",
        user="nihar",
        password=os.getenv("POSTGRES_PASSWORD"),
        host="db",
        port=5432,
    )
    cur = conn.cursor()
    cur.execute("SELECT username FROM users;")
    db_users = set(row[0] for row in cur.fetchall())
    if request.method == "POST":
        new_user = request.form.get("new_username")
        new_password = request.form.get("new_password")
        if new_user:
            if new_user in db_users:
                message = "User already exists."
            else:
                cur.execute(
                    "INSERT INTO users (username, password) VALUES (%s, %s);",
                    (new_user, new_password or ""),
                )
                conn.commit()
                message = f"User '{new_user}' created."
                db_users.add(new_user)
    cur.close()
    conn.close()
    return render_template("admin.html", users=db_users, message=message)


@app.route("/database")
def database():
    conn = psycopg2.connect(
        dbname="monopoly",
        user="nihar",
        password=os.getenv("POSTGRES_PASSWORD"),
        host="db",
        port=5432,
    )
    cur = conn.cursor()
    cur.execute("SELECT * FROM users;")
    users_data = cur.fetchall()
    cur.close()
    conn.close()
    return render_template("database.html", users_data=users_data)


def init_db():
    conn = psycopg2.connect(
        dbname="monopoly",
        user="nihar",
        password=os.getenv("POSTGRES_PASSWORD"),
        host="db",
        port=5432,
    )
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(255) UNIQUE NOT NULL,
            password VARCHAR(255)
        );
    """
    )
    conn.commit()
    cur.close()
    conn.close()


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
