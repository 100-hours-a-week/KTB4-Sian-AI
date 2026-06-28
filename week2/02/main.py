# main.py
from fastapi import FastAPI

from board import board_router
from comment import comment_router

app = FastAPI()

app.include_router(board_router.router)
app.include_router(comment_router.router)