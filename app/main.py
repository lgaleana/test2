from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.routes import app as routes_app

app = FastAPI()

# Mount the static files directory
app.mount("/static", StaticFiles(directory="app/templates/static"), name="static")

# Include the routes
app.include_router(routes_app)
