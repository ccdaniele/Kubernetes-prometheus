import os

from fastapi import FastAPI
import uvicorn

app: FastAPI = FastAPI()

@app.get("/")
async def index():
    environment: str = os.environ.get("APP_ENV")
    location: str = "From "

    if environment is None:
        location += "Host"
    else:
        location += environment
        
    return {"Hello": location}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=5050,reload=True)
    