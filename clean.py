import requests
import modal
from funcs.db import *
from datetime import datetime, time
import time as sleep_time
import os
import pytz
import math
import random
from bs4 import BeautifulSoup

stub = modal.Stub("clean")

funcs = modal.Mount.from_local_dir(
    "~/side-projects/stocker-python/funcs",
    condition=lambda pth: not ".venv" in pth,
    remote_path="/root/funcs",
)

modal_image = modal.Image.debian_slim(python_version="3.10").run_commands(
    "apt-get update",
    "apt-get install -y software-properties-common",
    "apt-add-repository non-free",
    "apt-add-repository contrib",
    "apt-get update",
    "apt-get install -y postgresql postgresql-contrib",
    "pip install psycopg2-binary",
    "pip install python-dotenv",
    "pip install requests",
    "pip install pytz",
    "pip install beautifulsoup4"
)

@stub.function(image=modal_image, secret=modal.Secret.from_name("database_connection_string"), mounts=[funcs], schedule=modal.Cron("0 5 * * *"), timeout=23400)
def clean():
  delete_all_but_last_60_prices()
  # Get all stocks except last 60 somehow
  # Delete em

@stub.local_entrypoint()
def main():
  clean.remote()
  print("Done!")