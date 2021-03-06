import math
import pandas as pd
import statsmodels.api as sm
import requests

import fred
import trading_calendar

from scipy import stats

API_DOMAIN_ROOT = 'https://www.alphavantage.co/query?function='

class Equity:

  def __init__(self, symbol, benchmark=False):
    self.symbol = symbol
    self.benchmark = benchmark

    # preload raw historical performance
    self.daily_activity = self._fetch_data('TIME_SERIES_DAILY_ADJUSTED', 'Time Series (Daily)')
    self.monthly_activity = self._fetch_data('TIME_SERIES_MONTHLY_ADJUSTED', 'Monthly Adjusted Time Series')

  def price(self):
    """
    Return the latest closing price
    """
    return pd.to_numeric( self.daily_activity['5. adjusted close'][-1] )

  def beta(self):
    """
    Return equity beta to benchmark
    Computed by comparing slope of asset to slope of benchmark (percent change)
    """
    # get daily percent changes
    benchmark_daily_pct_change = self.benchmark.daily_percent_change()
    daily_pct_change = self.daily_percent_change()

    # calculate beta
    r = sm.regression.linear_model.OLS( daily_pct_change[1:].tolist(), benchmark_daily_pct_change[1:].tolist() ).fit()
    beta = r.params[0]
    return beta


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
    
  def daily_volatility(self):
    """
    Standard deviation of daily percent change of closing price
    """
    # get daily percent change
    daily_pct_change = self.daily_percent_change()
    
    # calculate daily volatility
    daily_volatility = stats.tstd( daily_pct_change[1:] )
    return daily_volatility
  
  def annualized_volatility(self):
    """
    Daily price standard deviation extrapolated based on the number of trading days
    """
    # annualized volatility based on annual trading days
    daily_volatility = self.daily_volatility()
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

  def dividend_yield(self):
    """
    Found by annualizing the dividend payout and dividing by the current stock price
    """
    # parse for monthly dividend amount
    monthly_dividend_amount = pd.to_numeric(self.monthly_activity['7. dividend amount'])

    # dividend pay periods
    dividend_pay_periods = monthly_dividend_amount[monthly_dividend_amount > 0]
    
    # group by year
    dividend_pay_periods_by_year = dividend_pay_periods.rename(index=lambda s: s[0:4])
    no_pay_periods_per_year = dividend_pay_periods_by_year.groupby(level=0).count()

    # number of payouts per year
    payouts_per_year = no_pay_periods_per_year[1]

    # most recent payout
    dividend_payout = dividend_pay_periods[-1]

    # annual dividend yield
    annual_payout = dividend_payout * payouts_per_year

    # current stock price
    price = self.price()

    # dividend yield
    return annual_payout / price

  def _fetch_data(self, fn, key):
    # make request
    response = requests.get(API_DOMAIN_ROOT + fn + '&symbol=' + self.symbol + '&apikey=GQ383NOJKHTC4129&datatype=json')

    # filter and normalize response
    data = response.json()[key]
    series = pd.DataFrame.from_dict(data, orient='index')
    series = series.iloc[::-1]
    return series