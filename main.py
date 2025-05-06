from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
import uvicorn
from typing import Dict, Set
import json

app = FastAPI()

# Хранилище: {channel: {"like": 5, "thanks": 3}}
reactions: Dict[str, Dict[str, int]] = {}

# ID пользователей, которые уже отреагировали: {channel: {"user1", "user2"}}
voted_users: Dict[str, Set[str]] = {}

@app.websocket("/ws/{channel}")
async def websocket_endpoint(websocket: WebSocket, channel: str):
    await websocket.accept()
    
    # Инициализация канала
    if channel not in reactions:
        reactions[channel] = {"like": 0, "thanks": 0, "lag": 0, "scary": 0}
        voted_users[channel] = set()
    
    # Отправляем текущие реакции
    await websocket.send_text(json.dumps({
        "type": "init",
        "reactions": reactions[channel],
        "can_vote": True  # По умолчанию можно голосовать
    }))

    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Проверяем, что пользователь еще не голосовал
            user_id = message.get("user_id")  # Передаем из клиента
            if not user_id:
                continue
                
            if message["type"] == "reaction" and user_id not in voted_users[channel]:
                reaction_type = message["data"]
                if reaction_type in reactions[channel]:
                    reactions[channel][reaction_type] += 1
                    voted_users[channel].add(user_id)
                    
                    # Отправляем обновление всем
                    for conn in active_connections:
                        await conn.send_text(json.dumps({
                            "type": "update",
                            "reactions": reactions[channel],
                            "user_id": user_id,
                            "can_vote": False  # Блокируем кнопки
                        }))
    except WebSocketDisconnect:
        if user_id in voted_users[channel]:
            voted_users[channel].remove(user_id)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
