from flask import Flask, render_template, request, redirect, url_for, session
from game import MonopolyGame

app = Flask(__name__)
app.secret_key = "replace_this_with_a_random_secret"
game = MonopolyGame()
users = set()


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        if username:
            session["username"] = username
            # Start game with this user as the only player
            game.start_game([username])
            return redirect(url_for("play"))
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
    if request.method == "POST":
        new_user = request.form.get("new_username")
        if new_user:
            if new_user in users:
                message = "User already exists."
            else:
                users.add(new_user)
                message = f"User '{new_user}' created."
    return render_template("admin.html", users=users, message=message)


if __name__ == "__main__":
    app.run(debug=True)
