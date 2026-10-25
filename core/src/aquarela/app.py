import uvicorn
from fastapi import FastAPI
from fastapi.responses import PlainTextResponse

app = FastAPI(title="Aquarela")


@app.get("/api/health", response_class=PlainTextResponse)
def health() -> str:
    return "ok"


def main() -> None:
    uvicorn.run(app, host="127.0.0.1", port=8080)
