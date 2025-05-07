from flask import Flask
from flask_socketio import SocketIO, emit

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# Хранение реакций
reactions = {
    "Лайк!": 0,
    "Страшно...": 0,
    "Лагает": 0,
    "Вперед!": 0
}

@app.route('/')
def index():
    return "Сервер работает"

# Событие для получения реакций
@socketio.on('get_reactions')
def handle_get_reactions():
    print("Получен запрос на реакцию")
    emit('update_reactions', reactions, broadcast=False)

# Событие для отправки реакции
@socketio.on('send_reaction')
def handle_send_reaction(data):
    reaction = data.get('reaction')
    if reaction in reactions:
        reactions[reaction] += 1
        print(f"Реакция {reaction} обновлена")
        emit('update_reactions', reactions, broadcast=True)
    else:
        print(f"Неизвестная реакция: {reaction}")

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, allow_unsafe_werkzeug=True)

