"""
QuantInsti'23 | Inter IIT 11.0
Blueshift Code 

"""
from blueshift.library.technicals.indicators import ema
import talib as ta
import numpy as np
from blueshift.finance import commission, slippage
from blueshift.api import(  symbol,
                            order,
                            set_commission,
                            set_slippage,
                            schedule_function,
                            date_rules,
                            time_rules,
                       )


def initialize(context):
    """
        A function to define things to do at the start of the strategy
    """
    # universe selection - add stocks here
    context.securities = [symbol('TATAMOTORS')]

    # define strategy parameters
    context.params = {'indicator_lookback':375,
                      'indicator_freq':'1m',
                      'buy_signal_threshold':0.5,
                      'sell_signal_threshold':-0.5,
                      'ROC_period_short':30,
                      'ROC_period_long':120,
                      'BBands_period':300,
                      'trade_freq':1,
                      'leverage':2,
                      'max_holding_period':5, # edit holding period here
                      'SMA_period':10} 

    # variable for keeping track of positions - dictionary with key value pairs as share: days being held
    context.open_positions = {key:[] for key in context.securities} 

    # variable to control trading frequency
    context.bar_count = 0

    # variables to track signals and target portfolio
    context.signals = dict((security,0) for security in context.securities)
    context.target_position = dict((security,0) for security in context.securities)

    # set trading cost and slippage to zero
    set_commission(commission.PerShare(cost=0.0, min_trade_cost=0.0))
    set_slippage(slippage.FixedSlippage(0.00))
    
    freq = int(context.params['trade_freq'])
    schedule_function(run_strategy, date_rules.every_day(),
                      time_rules.every_nth_minute(freq))
    
    schedule_function(stop_trading, date_rules.every_day(),
                      time_rules.market_close(minutes=30))


def before_trading_start(context, data):
    context.trade = True
    
def stop_trading(context, data):
    context.trade = False


def increase_day_of_holdings(context, data):
    for security in context.securities:
        context.open_positions[security] = [1+i for i in context.open_positions[security]]


def check_for_exit(context, data):

    for security in context.securities:
        if len(context.open_positions[security]) == 0: # no open positions
            pass
        elif context.open_positions[security][0] == context.params["max_holding_period"]: # time to exit 
            oid = order(security, quantity=-25)
            print("sold", security, oid)
            context.open_positions[security] = context.open_positions[security][1:]
        else: # holdings exist, they just arent at that max day yet
            pass

def check_for_entry(context, data):
    '''
        Checking when we are entering the market
    '''
    for security in context.securities:
        if context.signals[security] > context.params['buy_signal_threshold']: # entry into market
            oid = order(security, quantity=25)
            print("ordered", security, oid)
            context.open_positions[security] += [0]




def run_strategy(context, data):
    """
        A function to define core strategy steps
    """
    if not context.trade:
        return        
    
    # add one day to all holdings
    increase_day_of_holdings(context, data)

    # sell all the ones whose holdings > max_holding_period
    check_for_exit(context, data)

    # generate required signals
    generate_signals(context, data)

    # generate_target_position(context, data)
    check_for_entry(context, data) # enter into market, if needed
        

def generate_signals(context, data):
    """
        A function to define define the signal generation
    """
    try:
        price_data = data.history(context.securities, ['open','high','low','close'],
            context.params['indicator_lookback'], context.params['indicator_freq'])
    except:
        return

    for security in context.securities:
        px = price_data.xs(security)
        context.signals[security] = signal_function(px, context.params,
            context.signals[security])
        #print(security, context.signals[security])

def signal_function(px, params, last_signal):
    """
        The main trading logic goes here, called by generate_signals above
    """
    op = np.array(px['open'], dtype=float)
    hi = np.array(px['high'], dtype=float)
    lo = np.array(px['low'], dtype=float)
    cl = np.array(px['close'], dtype=float)

    #identify candlestick pattern - change pattern here [CDLHARAMI, CDLPIERCING, CDLENGULFING]
    ind1 = ta.CDLENGULFING(op,hi,lo,cl) 

    ind2 = ema(px, params['SMA_period'])
    
    if ind1[-1] > 0 and cl[-1] < ind2:
        return 1
    else:
        return 0
