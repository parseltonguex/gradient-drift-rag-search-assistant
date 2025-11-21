# app.py
from mangum import Mangum
from backend.main import app  # import your FastAPI app

handler = Mangum(app)
