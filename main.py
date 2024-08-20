from fastapi import FastAPI, Request, Depends, BackgroundTasks
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import models
from models import Stock
from sqlalchemy.orm import Session
from database import SessionLocal, engine
import yfinance

app=FastAPI()
#Create all the database table extended the base model for all the models that we will create it
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

def fetch_stock_data(id:int):
    db=SessionLocal()
    stock=db.query(Stock).filter(Stock.id==id).first()
    
    yahoo_data= yfinance.Ticker(stock.symbol)
    print(yahoo_data.info)
    
    stock.ma200= yahoo_data.info['twoHundredDayAverage']
    stock.ma50= yahoo_data.info['fiftyDayAverage']
    stock.price = yahoo_data.info['previousClose']
    stock.forward_pe = yahoo_data.info['forwardPE']
    stock.forward_eps = yahoo_data.info['forwardEps']
    stock.dividend_yield = yahoo_data.info['returnOnEquity']

    
    
    db.add(stock)
    db.commit()


@app.get("/")
def dashboard(request:Request,forward_pe =None, dividend_yield=None, ma50 = None, ma200=None, db: Session = Depends(get_db)):
    '''
    Display stock screener dashboard / homepage
    '''

    stocks = db.query(Stock)

    if forward_pe:
        stocks = stocks.filter(Stock.forward_pe < forward_pe)

    if dividend_yield:
        stocks = stocks.filter(Stock.dividend_yield > dividend_yield)
    
    if ma50:
        stocks = stocks.filter(Stock.price > Stock.ma50)
    
    if ma200:
        stocks = stocks.filter(Stock.price > Stock.ma200)
    
    

    return templates.TemplateResponse("home.html", {
        "request": request, 
        "stocks": stocks, 
        "dividend_yield": dividend_yield,
        "forward_pe": forward_pe,
        "ma200": ma200,
        "ma50": ma50
    })


#We should use async to execute the functions into background_task
@app.post("/stock")
async def create_stock(stock_request: StockRequest, background_task: BackgroundTasks, db: Session=Depends(get_db)):
    '''
    Create a stock and stores it in the database
    '''
    stock=Stock()
    stock.symbol = stock_request.symbol
    db.add(stock)
    db.commit()
    background_task.add_task(fetch_stock_data,stock.id)
    
    return {
        "code":"succed",
        "message": "Stock created"
    }