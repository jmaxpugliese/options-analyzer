# custom methods
from equity import Equity

def main():
  """
  Stock_price Options_price Call_strike_price Dividends 
  """
  # option = {
  #   'price': 4.41,
  #   'type': 'call',
  #   'strike': 28.38,
  #   'dividends': .8,
  #   'stock_price': 25
  # }
  # print(option)

  # bes = option.stock_price - option.price - option.dividends
  # print("break even stock price", bes)

  benchmark = Equity('VOO')
  print(benchmark.benchmark)

  e = Equity('IBM', benchmark)
  print( e.beta() )


if __name__ == '__main__':
  main()