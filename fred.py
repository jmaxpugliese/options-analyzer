import pandas as pd
import requests
# import requests-cache

from scipy import stats

# https://research.stlouisfed.org/docs/api/fred/series_observations.html

FRED_OBSERVATIONS_API_ENDPOINT = 'https://api.stlouisfed.org/fred/series/observations?series_id='
FRED_API_KEY = 'ed2b29e8c176b41579fcc89c110a4814'

ONE_YR_TREAS_CONS_MATURITY_RATE_SERIES = 'GS1'

def fetch_observations(series, freq):
  """
  Query Fred endpoint based on method specifications 
  """
  url = FRED_OBSERVATIONS_API_ENDPOINT + series + '&aggregation_method=eop&frequency=' + freq + '&sort_order=desc&api_key=' + FRED_API_KEY + '&file_type=json'
  try:
    response = requests.get(url)
    return response.json()
  except:
    print(response.json())


AVG_ONE_YR_TREAS_CONST_MATURITY_RATE = None
def avg_one_yr_treas_const_maturity_rate():
  """
  Returns the geometric average risk free rate over the past 25 years 
  """
  global AVG_ONE_YR_TREAS_CONST_MATURITY_RATE
  if AVG_ONE_YR_TREAS_CONST_MATURITY_RATE is None:
    response_obj = fetch_observations(ONE_YR_TREAS_CONS_MATURITY_RATE_SERIES, 'a')
    observations = pd.DataFrame.from_dict(response_obj['observations'])

    observations = observations[1:-1]
    observations['geo_mean'] = pd.to_numeric(observations['value']) + 1
    annual_return_rate = stats.mstats.gmean( observations['geo_mean'][:25] )

    # divide by 100 to find true value
    AVG_ONE_YR_TREAS_CONST_MATURITY_RATE = annual_return_rate / 100

  return AVG_ONE_YR_TREAS_CONST_MATURITY_RATE

CURR_ONE_YR_TREAS_CONST_MATURITY_RATE = None
def curr_one_yr_treas_const_maturity_rate():
  """
  Returns the current 1 year risk-free rate 
  """
  global CURR_ONE_YR_TREAS_CONST_MATURITY_RATE
  if CURR_ONE_YR_TREAS_CONST_MATURITY_RATE is None:
    response_obj = fetch_observations(ONE_YR_TREAS_CONS_MATURITY_RATE_SERIES, 'm')
    observations = pd.DataFrame.from_dict(response_obj['observations'])
    current_return_rate = pd.to_numeric(observations['value'][0])

    # divide by 100 to find true value
    CURR_ONE_YR_TREAS_CONST_MATURITY_RATE = current_return_rate / 100

  return CURR_ONE_YR_TREAS_CONST_MATURITY_RATE

