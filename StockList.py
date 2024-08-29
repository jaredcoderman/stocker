from Stock import Stock
from typing import List, Tuple
class StockList:

  def __init__(self, stocks):
    self.stocks: List[Stock] = stocks

  def to_tuple(self):
    new_list = []
    for stock in self.stocks:
      new_list.append(stock.get_tuple_of_data())
    return new_list