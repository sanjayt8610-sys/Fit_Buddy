import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from dotenv import load_dotenv

from app.database import init_db
from app.routes import router

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler to ensure DB tables are created on start."""
    init_db()
    yield


app = FastAPI(
    title="FitBuddy – AI Fitness Plan Generator",
    description="A full-stack, AI-powered fitness planning application that generates 7-day personalized workout routines and nutrition guidance with Gemini AI.",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Ensure static directories exist
os.makedirs("static/css", exist_ok=True)
os.makedirs("static/js", exist_ok=True)
os.makedirs("static/images", exist_ok=True)
os.makedirs("templates", exist_ok=True)

# Mount Static Files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include Application Routes
app.include_router(router)

templates = Jinja2Templates(directory="templates")


# Global HTTP 404 Error Handler
@app.exception_handler(404)
async def custom_404_handler(request: Request, exc):
    return templates.TemplateResponse(
        request=request,
        name="error.html",
        context={
            "error_title": "404 - Page Not Found",
            "error_message": "The page or fitness plan you are looking for does not exist or has been moved."
        },
        status_code=404
    )


# Global HTTP 500 Error Handler
@app.exception_handler(500)
async def custom_500_handler(request: Request, exc):
    return templates.TemplateResponse(
        request=request,
        name="error.html",
        context={
            "error_title": "500 - Server Error",
            "error_message": "An internal error occurred. Please try again or check back shortly."
        },
        status_code=500
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
