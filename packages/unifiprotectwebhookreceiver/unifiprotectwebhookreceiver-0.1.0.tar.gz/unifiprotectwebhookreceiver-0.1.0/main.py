from fastapi import FastAPI

from model.unifialert import UnifiAlert

app = FastAPI()


@app.post("/webhook")
async def create_alert(alert: UnifiAlert):
    return alert
