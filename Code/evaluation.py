"""
QuantInsti'23 | Inter IIT 11.0
Evaluation Metrics - Python

This script takes the transactions.csv file generated of BlueShift Logs as input, generates t-stats, returns, winning probability and Z. It also saves the returns data generated from means as ".txt" file for input for R code to calculate bootstrapped skewness adjusted t test values and the confidence intervals.

"""

import pandas as pd
import math
import statistics

# Importing data - edit file name here
tranData=pd.read_csv("transactions_B5.csv")


# Sorting data on basis of stocks
enter = [] 
exit = []
symbol_dict = {}

for i in range(tranData.shape[0]):
    temp=tranData['amount'].iloc[i]
    symbol = tranData['symbol'].iloc[i]
    if(symbol not in symbol_dict):
        enter = [] 
        exit = []
        if(temp >0):
            enter.append(tranData['price'].iloc[i])
        else:
            exit.append(tranData['price'].iloc[i])
        symbol_dict[symbol] = [enter,exit]
    else:
        if(temp >0):
            symbol_dict[symbol][0].append(tranData['price'].iloc[i])
        else:
            symbol_dict[symbol][1].append(tranData['price'].iloc[i])

# Calculating returns and log or returns
returns=0
indiReturns=[]
meanReturns=0
pcnt=0
for lst in symbol_dict:
    entry = symbol_dict[lst][0]
    exit = symbol_dict[lst][1]
    for i in range(len(exit)):
        if((exit[i]-entry[i])>0):
            pcnt+=1
        tempReturns = (math.log(exit[i],math.e) - math.log(entry[i],math.e))
        indiReturns.append(tempReturns)
        returns+=tempReturns

print("the return in MYR is {}".format(returns))

# Saving to txt file for R script
with open("rtrn.txt",'w') as file1:
    for i in indiReturns:
        print(i,file=file1)
file1.close()


stdDev= statistics.stdev(indiReturns)
gamma=0

n=len(indiReturns)
print("number of samples:",n)

# Calculating returns
rBar = returns/n
for i in range(n):
    tempG = (((indiReturns[i]- rBar)**3)/(n*(stdDev**3)))
    gamma+=tempG
print("rMean", rBar*100)


s = rBar/stdDev
Tsa = (n**0.5)*(s+((gamma*(s**2))/3)+(gamma/(6*n)))
print("tsa of stocks is ",Tsa)
print("standardized mean of returns", s)
print("estimated skewness of returns", gamma)
print("winning Prob:", pcnt/n)

# Calculating z statistics
p=pcnt/n
p0=0.5
sigma= (n* p0 * (1-p0))**0.5
Z=(n*(p-p0))/sigma
print("Z:",Z)

