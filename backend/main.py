from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes.todo import router as todo_router
from routes.auth import router as auth_router

from config.context_manager import lifespan

app = FastAPI(lifespan=lifespan)

origins = [
    "http://localhost",
    "http://localhost:5173"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,          # List of allowed origins
    allow_credentials=True,         # Allow cookies to be sent cross-origin
    allow_methods=["*"],            # Allow all HTTP methods (GET, POST, PUT, etc.)
    allow_headers=["*"],            # Allow all headers
)

app.include_router(todo_router)
app.include_router(auth_router)


