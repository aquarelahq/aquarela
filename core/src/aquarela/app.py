import uvicorn
from fastapi import FastAPI
from fastapi.responses import PlainTextResponse

app = FastAPI(title="Aquarela")


# PlainTextResponse responde "ok" tal cual, sin las comillas de JSON
@app.get("/api/health", response_class=PlainTextResponse)
def health() -> str:
    return "ok"


# El comando `aquarela` llama a esta función (ver [project.scripts])
def main() -> None:
    uvicorn.run(app, host="127.0.0.1", port=8080)
