import math
import pandas as pd
import requests

import fred
import trading_calendar

from scipy import stats

API_DOMAIN_ROOT = 'https://www.alphavantage.co/query?function='

class Equity:

  def __init__(self, symbol):
    self.symbol = symbol

    # preload raw historical performance
    self.daily_activity = self._fetch_data('TIME_SERIES_DAILY_ADJUSTED', 'Time Series (Daily)')
    self.monthly_activity = self._fetch_data('TIME_SERIES_MONTHLY_ADJUSTED', 'Monthly Adjusted Time Series')

  def daily_percent_change(self):
    """
    Calculate the daily percent change of closing price over the last 100 days.
    """
    try:
      # parse for adjusted daily close
      daily_adj_close = pd.to_numeric(self.daily_activity['5. adjusted close'])

      # calculate percent change
      daily_pct_change = pd.DataFrame.pct_change( daily_adj_close )
      return daily_pct_change
    except:
      print(response)
      
  
  def annualized_volatility(self):
    """
    Daily price standard deviation extrapolated based on the number of trading days
    """
    # get daily percent change
    daily_pct_change = self.daily_percent_change()
    
    # calculate daily volatility
    daily_volatility = stats.tstd( daily_pct_change[1:] )

    # annualized volatility based on annual trading days
    annualized_volatility = daily_volatility * math.sqrt( trading_calendar.get_no_trading_days() )
    
    return annualized_volatility

  def recent_daily_excess_return(self):
    """
    Geometric mean of the closing price for the last 100 days after risk free rate
    """
    # get daily percent change
    daily_pct_change = self.daily_percent_change()

    # daily return (geometric mean)
    daily_percent_change_plus_one = daily_pct_change + 1
    daily_return = stats.mstats.gmean( daily_percent_change_plus_one[1:] )
    daily_return = daily_return - 1

    # excess return
    excess_return = daily_return - fred.curr_one_yr_treas_const_maturity_rate()

    return excess_return

  def _fetch_data(self, fn, key):
    # make request
    response = requests.get(API_DOMAIN_ROOT + fn + '&symbol=' + self.symbol + '&apikey=GQ383NOJKHTC4129&datatype=json')

    # filter and normalize response
    data = response.json()[key]
    series = pd.DataFrame.from_dict(data, orient='index')
    series = series.iloc[::-1]
    return series