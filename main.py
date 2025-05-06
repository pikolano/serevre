from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
import uvicorn
from typing import Dict, Set
import json

app = FastAPI()

# Хранилище: {"inter": 5, "barsa": 3}
reactions: Dict[str, int] = {"inter": 0, "barsa": 0}

# ID пользователей, которые уже голосовали
voted_users: Set[str] = set()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    
    try:
        # Отправляем текущие реакции
        await websocket.send_text(json.dumps(reactions))
        
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Проверяем, что пользователь еще не голосовал
            user_id = message.get("user_id")
            if not user_id or user_id in voted_users:
                continue
                
            if message["type"] == "reaction" and message["team"] in reactions:
                reactions[message["team"]] += 1
                voted_users.add(user_id)
                
                # Отправляем обновление всем
                await websocket.send_text(json.dumps(reactions))
    except WebSocketDisconnect:
        pass

@app.get("/")
async def root():
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
