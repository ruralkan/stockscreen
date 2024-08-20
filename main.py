from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
import models
from sqlalchemy.orm import Session
from database import SessionLocal, engine


app=FastAPI()

models.Base.metadata.create_all(bind=engine)

templates = Jinja2Templates(directory='templates')

@app.get("/")
def dashboard(request:Request):
    '''
    Display stock screener dashboard / homepage
    '''
    return templates.TemplateResponse("home.html", {
        "request":request,
        "somevar":2})

@app.post("/stock")
def create_stock():
    '''
    Create a stock and stores it in the database
    '''
    return {
        "code":"succed",
        "message": "Stock created"
    }