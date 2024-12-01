from fastapi import APIRouter
from starlette.responses import HTMLResponse

api_router = APIRouter()

@api_router.get("/", response_class=HTMLResponse)
async def root():
    return open('static/index.html').read()
