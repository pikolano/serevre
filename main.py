from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
import uvicorn
from typing import Dict
import json

app = FastAPI()

# Хранилище реакций: {"oneevent1": {"like": 0, "thanks": 0, ...}}
reactions: Dict[str, Dict[str, int]] = {}

# WebSocket подключения
active_connections = []

@app.websocket("/ws/{channel}")
async def websocket_endpoint(websocket: WebSocket, channel: str):
    await websocket.accept()
    active_connections.append(websocket)
    
    # Инициализация реакций для канала
    if channel not in reactions:
        reactions[channel] = {"inter": 0, "barsa": 0}
    
    # Отправляем текущие реакции
    await websocket.send_text(json.dumps(reactions[channel]))
    
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            if message["type"] == "reaction":
                reaction_type = message["data"]
                if reaction_type in reactions[channel]:
                    reactions[channel][reaction_type] += 1
                    # Рассылаем обновление всем в канале
                    for conn in active_connections:
                        await conn.send_text(json.dumps(reactions[channel]))
    except WebSocketDisconnect:
        active_connections.remove(websocket)

@app.get("/")
async def root():
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
