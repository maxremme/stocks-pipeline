import requests
import os
import json

KEY = os.getenv("KEY")


def get_data_lambda(event, context, api_key=KEY):
    """Makes api request to IEX API to get previous day stock quotes.

    Args:
        api_key (str): Your personal API key.

    Returns:
        df: Returns a Pandas DataFrame with chosen stock information: Symbol, Date, Open, Close, High, Low and Volume.
    """
    stock_list = [
        "AAPL",
        "MSFT",
        "AMZN",
        "GOOGL",
        "GOOG",
        "TSLA",
        "JPM",
        "JNJ",
        "V",
        "NVDA",
        "PG",
        "MA",
        "UNH",
        "HD",
        "PYPL",
        "VZ",
        "DIS",
        "BAC",
        "INTC",
        "KO",
        "T",
        "PFE",
        "CMCSA",
        "ORCL",
        "WMT",
        "CSCO",
        "XOM",
    ]
    values_list = []

    for item in stock_list:
        url = f"https://cloud.iexapis.com/stable/stock/{item}/previous?token={KEY}"
        response = requests.get(url)
        if response.status_code == 200:
            resp = response.json()
            # values_list.append(resp)
        else:
            print("Error from server: " + str(response.content))
        values_list.append(resp)

    return values_list
