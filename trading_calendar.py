import numpy as np
import datetime as dt

# NYSE Trading calendar
# https://www.nyse.com/markets/hours-calendars
NO_HOLIDAYS = { 2020: 9, 2021: 9, 2022: 8 }

def get_no_trading_days():
  """
  Returns the number of trading days for the current year
  """
  now = dt.datetime.now()

  start = dt.date( now.year, 1, 1 )
  end = dt.date( ((now.year + 1)), 1, 1 )

  bus_days = np.busday_count( start, end )
  trading_days = bus_days - NO_HOLIDAYS[now.year]
  
  return trading_days

