from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
import uvicorn
import json
import os

app = FastAPI()

reactions = {
    "like": {"emoji": "👍", "text": "Лайк", "count": 0},
    "thanks": {"emoji": "🙏", "text": "Спасибо!", "count": 0},
    "lag": {"emoji": "🐌", "text": "Лагает...", "count": 0},
    "scary": {"emoji": "👻", "text": "Страшно!", "count": 0}
}

active_connections = []

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_connections.append(websocket)
    try:
        await websocket.send_text(json.dumps({"type": "init", "data": reactions}))
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            if message["type"] == "reaction":
                reaction_type = message["data"]
                if reaction_type in reactions:
                    reactions[reaction_type]["count"] += 1
                    for connection in active_connections:
                        await connection.send_text(json.dumps({
                            "type": "update",
                            "data": reactions
                        }))
    except WebSocketDisconnect:
        active_connections.remove(websocket)

@app.get("/")
async def root():
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
