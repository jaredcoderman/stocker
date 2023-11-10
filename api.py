from flask import Flask, jsonify, request
from db import *

app = Flask(__name__)

# @app.route('/stock/', methods=['GET'])
# def get_stock():
#     return jsonify({"stocks": stocks})

@app.route('/prices/<string:ticker>', methods=['GET'])
def get_prices_by_ticker(ticker):
    prices = get_prices(ticker)
    return jsonify({ticker: {
      "prices": prices
    }})

if __name__ == '__main__':
    app.run(debug=True)
