"""
Flask app for Monopoly Deal game.
Handles user login, game play, and admin/database operations.
"""

import os
from os import path
from flask import Flask, render_template, request, redirect, url_for, session
from dotenv import load_dotenv
from game import start_game, draw_card, play_card, next_turn
from database import (
    initialize_database,
    get_usernames,
    user_exists,
    create_user,
    get_all_users,
)


def initialize():
    """
    Load environment variables and return the directory path
    of the current file.
    """
    load_dotenv(path.join(path.dirname(__file__), "./.envs/nihar.env"))
    return path.dirname(path.realpath(__file__))


app = Flask(__name__)
app.secret_key = "replace_this_with_a_random_secret"
game_state = None
users = set()
initialize()


# Initialize database with the new database module
# Note: This will be called when the app starts, not during import
def init_database():
    """Initialize the database when the app starts."""
    try:
        initialize_database()
        print("Database initialized successfully")
    except Exception as e:
        print(f"Warning: Could not initialize database: {e}")


# Call this when the app actually runs, not during import
if __name__ == "__main__":
    init_database()


@app.route("/", methods=["GET", "POST"])
def home():
    """Route for home page, redirects to login."""
    return login()


@app.route("/login", methods=["GET", "POST"])
def login():
    """Handle user login and start game if credentials are valid."""
    global game_state
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        db_user = os.getenv("POSTGRES_USER", "nihar")
        db_pass = os.getenv("POSTGRES_PASSWORD")
        if username == db_user and password == db_pass:
            session["username"] = username
            game_state = start_game([username])
            return redirect(url_for("play"))
        error_text = "Invalid username or password."
        return render_template("login.html", error=error_text)
    return render_template("login.html")


@app.route("/logout")
def logout():
    """Log out the current user."""
    session.pop("username", None)
    return redirect(url_for("login"))


@app.route("/play", methods=["GET", "POST"])
def play():
    """Main game play route."""
    if "username" not in session:
        return redirect(url_for("login"))
    if not game_state or not game_state.get("started", False):
        return redirect(url_for("login"))
    message = ""
    if request.method == "POST":
        action = request.form.get("action")
        if action == "draw":
            message = draw_card(game_state)
        elif action == "play":
            card_idx = int(request.form.get("card_idx"))
            message = play_card(game_state, card_idx)
        elif action == "end_turn":
            next_turn(game_state)
    current_player = game_state["players"][game_state["current_player_idx"]]
    return render_template(
        "play.html",
        game_state=game_state,
        current_player=current_player,
        message=message
    )


@app.route("/admin", methods=["GET", "POST"])
def admin():
    """Admin page for managing users."""
    message = ""

    # Get existing users using the database module
    db_users = set(get_usernames())

    if request.method == "POST":
        new_user = request.form.get("new_username")
        new_password = request.form.get("new_password")
        if new_user:
            if user_exists(new_user):
                message = "User already exists."
            else:
                try:
                    create_user(new_user, new_password or "")
                    message = f"User '{new_user}' created."
                    db_users.add(new_user)
                except Exception as e:
                    message = f"Error creating user: {str(e)}"

    return render_template("admin.html", users=db_users, message=message)


@app.route("/database")
def database():
    """Show all users in the database."""
    try:
        users_data = get_all_users()
        return render_template("database.html", users_data=users_data)
    except Exception as e:
        return render_template("database.html", users_data=[], error=str(e))
