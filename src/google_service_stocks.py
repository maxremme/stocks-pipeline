from stocks_main import get_data, extract_values
import gspread
import time
import datetime as dt
from dotenv import load_dotenv
import os

load_dotenv()

API_KEY = os.getenv("KEY")


def save_data():
    data = extract_values(get_data(API_KEY))
    gc = gspread.service_account(filename="../service_account/service_account.json")

    wks = gc.open("Stock").sheet1

    column_names = [
        "Symbol",
        "Date",
        "fOpen",
        "fClose",
        "fHigh",
        "fLow",
        "fVolume",
    ]

    symbol = data["Symbol"].tolist()
    date = data["Date"].tolist()
    fopen = data["fOpen"].tolist()
    fclose = data["fClose"].tolist()
    fhigh = data["fHigh"].tolist()
    flow = data["fLow"].tolist()
    fvolume = data["fVolume"].tolist()

    wks.append_row(column_names)

    for i in range(len(data)):
        wks.append_row(
            [
                symbol[i],
                date[i],
                fopen[i],
                fclose[i],
                fhigh[i],
                flow[i],
                fvolume[i],
            ]
        )

        # for i in range(len(data)):
        #     wks.append_row(
        #         [
        #             symbol[i],
        #             date[i],
        #             fclose[i],
        #             fhigh[i],
        #             flow[i],
        #             fvolume[i],
        #         ]
        #     )
        time.sleep(1)


save_data()
