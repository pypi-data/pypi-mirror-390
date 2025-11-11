import os
import pandas as pd
import requests
import datetime
from datetime import date
import yfinance as yf

class TickerDataFetch:

    def __init__(self):
        self.todays_date = str(date.today())
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.output_folder = os.path.join(self.script_dir, "Historical Data")

    def folder_scan(self):
        os.makedirs(self.output_folder, exist_ok=True)
        self.List = os.listdir(self.output_folder)
        self.namelist = {}
        for item in self.List:
            ticker_name = item.split('.')[0].split()[0]
            ticker_date = item.split('.')[0].split()[1]
            self.namelist[ticker_name] = ticker_date

    def fetch_historical_data(self, ticker):
        ticker_data = yf.download(ticker, period='max')
        os.makedirs(self.output_folder, exist_ok=True)
        csv_path = os.path.join(self.output_folder, f"{ticker} {self.todays_date}.csv")
        DataFrame = pd.DataFrame(ticker_data)
        DataFrame.columns = ['Close','High','Low','Open','Volume']
        DataFrame.to_csv(csv_path,index=True,header=True)
        print(f"Saved CSV to: {csv_path}")

    def update_tickers (self,tickers): 
        self.folder_scan()
        for ticker in tickers:
            if ticker in self.namelist:
                if self.namelist[ticker] == self.todays_date:
                    print(ticker,"data found for",self.todays_date)
                else:
                    os.remove(os.path.join(self.output_folder, f"{ticker} {self.namelist[ticker]}.csv"))
                    self.fetch_historical_data(ticker)
                    print(ticker,"data found for",self.namelist[ticker],". Updating data for",self.todays_date)
            else:
                self.fetch_historical_data(ticker)
                print(ticker,"data not found",{ticker},". Updating data for",self.todays_date)
        for ticker in self.namelist:
            if ticker in tickers:
                pass
            else:
                os.remove(os.path.join(self.output_folder, f"{ticker} {self.namelist[ticker]}.csv"))
                print("Removed",ticker,".")
        self.folder_scan()

    def import_tickers(self):
        ticker_data = {}
        self.folder_scan()
        for ticker in self.namelist:
            data = pd.read_csv(os.path.join(self.output_folder, f"{ticker} {self.namelist[ticker]}.csv"))
            data.set_index('Date',inplace=True)
            ticker_data[ticker] = data
        return ticker_data

class DataManipulation:
    def __init__(self):
        pass

    def shift_cells(self):
        pass
