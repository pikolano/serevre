# server.py
from flask import Flask, render_template
from flask_socketio import SocketIO, emit

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# Хранение количества реакций
reactions = {
    "Лайк!": 0,
    "Страшно...": 0,
    "Лагает": 0,
    "Вперед!": 0
}

@app.route('/')
def index():
    return 'Сервер реакций работает!'

@socketio.on('send_reaction')
def handle_reaction(data):
    reaction = data.get("reaction")
    if reaction in reactions:
        reactions[reaction] += 1
        emit('update_reactions', reactions, broadcast=True)

@socketio.on('get_reactions')
def send_initial_data():
    emit('update_reactions', reactions)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)

