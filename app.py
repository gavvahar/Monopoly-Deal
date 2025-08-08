from flask import Flask, render_template, request, redirect, url_for
from game import MonopolyGame

app = Flask(__name__)
game = MonopolyGame()

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/start', methods=['POST'])
def start():
    player_names = request.form.getlist('players')
    game.start_game(player_names)
    return redirect(url_for('play'))

@app.route('/play')
def play():
    return render_template('play.html', game=game)

if __name__ == '__main__':
    app.run(debug=True)
