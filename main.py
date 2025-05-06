from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import uvicorn
import json

app = FastAPI()

# Хранилище реакций
reactions = {
    "like": {"emoji": "👍", "text": "Лайк", "count": 0},
    "thanks": {"emoji": "🙏", "text": "Спасибо!", "count": 0},
    "lag": {"emoji": "🐌", "text": "Лагает...", "count": 0},
    "scary": {"emoji": "👻", "text": "Страшно!", "count": 0}
}

# WebSocket подключения
active_connections = []

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_connections.append(websocket)
    try:
        # Отправляем текущие реакции новому клиенту
        await websocket.send_text(json.dumps({"type": "init", "data": reactions}))
        
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            if message["type"] == "reaction":
                reaction_type = message["data"]
                if reaction_type in reactions:
                    reactions[reaction_type]["count"] += 1
                    # Рассылаем обновление всем подключенным
                    for connection in active_connections:
                        await connection.send_text(json.dumps({
                            "type": "update",
                            "data": reactions
                        }))
    except WebSocketDisconnect:
        active_connections.remove(websocket)

# Статическая страница для теста
@app.get("/", response_class=HTMLResponse)
async def test_page():
    return """
    <!DOCTYPE html>
    <html>
    <body>
        <h1>Сервер реакций работает!</h1>
        <p>WebSocket: <code id="status">Отключен</code></p>
        <script>
            const ws = new WebSocket(`ws://${window.location.host}/ws`);
            ws.onopen = () => document.getElementById("status").textContent = "Подключен";
            ws.onmessage = (e) => console.log(JSON.parse(e.data));
        </script>
    </body>
    </html>
    """

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
