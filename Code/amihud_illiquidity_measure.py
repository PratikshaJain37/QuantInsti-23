"""
QuantInsti'23 | Inter IIT 11.0
Illiquidity Measure - AMIHUD

This script take a ".txt" file of stocks as input, gets daily data (volume and returns), prints an output of the least illiquid stocks and saves this information to a CSV
"""

import numpy as np 
import yfinance as yf
import csv

illiq_dict = []

# Opening file of stocks to read stocks symbols from
with open("Nifty-50-LargeCap.txt", "r") as file:
    tickers = file.readlines()[1:]
    tickers = [ticker[:-1] for ticker in tickers]


for ticker in tickers:

    # Downloading daily data
    data = yf.download(ticker+".NS", start="2018-07-01", end="2018-12-31")
    data = data[["Volume", "Adj Close"]]

    # Calculating the amihud measure
    p = np.array(data["Adj Close"]) 
    dollar_vol = np.array(data["Volume"]*p) 
    ret = np.array((p[1:] - p[:-1])/p[1:]) 
    illiq = np.mean(np.divide(abs(ret),dollar_vol[1:])) 

    # Saving the results in a list of dictionaries
    illiq_dict += [{'ticker_name':ticker, 'illiq_adj':illiq*100000000000}]

    print("Aminud illiq for =",ticker,illiq)


# Sorting the list as per the least illiquidity
illiq_dict = sorted(illiq_dict, key=lambda d: d['illiq_adj'])

# For convenience of adding to blueshift code
toPrint = "["
for key in illiq_dict:
    toPrint += "symbol(\'" + key["ticker_name"] + "\'), "
print(toPrint+"]")

# Saving the results in a csv
with open("Nifty-50-LargeCap.csv", "w") as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=["ticker_name", "illiq_adj"])
    writer.writeheader() 
    writer.writerows(illiq_dict) 

