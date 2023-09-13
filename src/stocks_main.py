import requests
import pandas as pd
import datetime as dt


def get_data(api_key):
    """Makes api request to IEX API to get historical stock information of the last 2 months.

    Returns:
        JSON object: symbol,date,fclose,fhigh, flow,fvolume,
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
        url = f"https://cloud.iexapis.com/v1/data/core/historical_prices/{item}?range=2m&token={api_key}"
        resp = requests.get(url)

        if resp.status_code == 200:
            r = resp.json()
            values_list.append(r)
        else:
            print("Error from server: " + str(resp.content))

    return values_list


def extract_values(data):
    """Parses Data received from IEX API.

    Args:
        data (list): list of dictionaries of json objects from API request

    Returns:
        Pandas Dataframe: Returns a dataframe of all information requested from IEX API.
    """
    df = pd.DataFrame()
    symbol_list = []
    dates = []
    fopen_list = []
    fclose_list = []
    fhigh_list = []
    flow_list = []
    fvolume_list = []

    for i in range(len(data)):
        for k in range(len(data[i])):
            symbol_list.append(data[i][k]["key"])
            date = data[i][k]["date"]
            dates.append(dt.datetime.utcfromtimestamp(date / 1000).strftime("%Y-%m-%d"))
            fopen_list.append(data[i][k]["fopen"])
            fclose_list.append(data[i][k]["fclose"])
            fhigh_list.append(data[i][k]["fhigh"])
            flow_list.append(data[i][k]["flow"])
            fvolume_list.append(data[i][k]["fvolume"])

    df["Symbol"] = pd.DataFrame(symbol_list)
    df["Date"] = pd.DataFrame(dates)
    df["fOpen"] = pd.DataFrame(fopen_list)
    df["fClose"] = pd.DataFrame(fclose_list)
    df["fHigh"] = pd.DataFrame(fhigh_list)
    df["fLow"] = pd.DataFrame(flow_list)
    df["fVolume"] = pd.DataFrame(fvolume_list)

    return df
