# Stocker

This project scrapes stock data into a PlanetScale database from which a Flask API accesses to retrieve stock data. This is a service for my StockSim project.

## Installation

1. Clone the repo and cd into it
`git clone https://github.com/jaredcoderman/stocker`
`cd stocker`

2. Make a venv i.e.
`python3 -m venv .`
`source bin/activate

3. Run poetry install
`poetry install`

4. Make env variables for a planetscale database by following PlanetScale's "Connect with python" instructions after making a database.
5. Start the API/Scraper
`python3 api.py`
OR
`python3 scrape.py`
