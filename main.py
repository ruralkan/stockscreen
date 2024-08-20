from fastapi import FastAPI, Request, Depends
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import models
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from models import Stock

app=FastAPI()

models.Base.metadata.create_all(bind=engine)

templates = Jinja2Templates(directory='templates')

class StockRequest(BaseModel):
    symbol:str


def get_db():
    try:
        db= SessionLocal()
        yield db
    finally:
        db.close()

@app.get("/")
def dashboard(request:Request):
    '''
    Display stock screener dashboard / homepage
    '''
    return templates.TemplateResponse("home.html", {
        "request":request,
        "somevar":2})

@app.post("/stock")
def create_stock(stock_request: StockRequest, db: Session=Depends(get_db)):
    '''
    Create a stock and stores it in the database
    '''
    stock=Stock()
    stock.symbol = stock_request.symbol
    db.add(stock)
    db.commit()
    
    
    return {
        "code":"succed",
        "message": "Stock created"
    }