from typing import Tuple
class Stock:

  def __init__(self, ticker, name, price):
    self.ticker = ticker
    self.name = name
    self.price = price

  def get_tuple_of_data(self) -> Tuple:
    return (self.ticker, self.name, self.price)