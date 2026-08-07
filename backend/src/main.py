from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from src.routes.auth import router as auth_router
from src.routes.chat import router as chat_router

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Trendly Agentic Support Assistant API is running (Python/FastAPI)."}

app.include_router(auth_router, prefix="/auth")
app.include_router(chat_router, prefix="/chat")

if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.getenv("PORT", 8081))
    uvicorn.run("src.main:app", host="0.0.0.0", port=port, reload=True)
