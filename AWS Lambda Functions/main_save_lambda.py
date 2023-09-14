import gspread
import json


def save_data_lambda(event, context):
    gc = gspread.service_account(filename="./service_account/service_account.json")
    wks = gc.open("Stock").sheet1

    for i in range(len(event["responsePayload"])):
        wks.append_row(
            [
                event["responsePayload"][i]["symbol"],
                event["responsePayload"][i]["date"],
                event["responsePayload"][i]["fOpen"],
                event["responsePayload"][i]["fClose"],
                event["responsePayload"][i]["fHigh"],
                event["responsePayload"][i]["fLow"],
                event["responsePayload"][i]["fVolume"],
            ]
        )
