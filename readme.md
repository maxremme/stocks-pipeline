# Data Pipeline Project: Stock Information Retrieval and Visualization
## Overview

This project implements a data pipeline for retrieving stock information from the IEX API, storing it in Google Sheets, and visualizing it using a Streamlit cloud frontend. The pipeline consists of three main components: two AWS Lambda functions and a Streamlit web application.

### Components
#### 1. Initial Data Retrieval

    Function Name: main_lambda.py
    Description: This AWS Lambda function makes an initial API call to the IEX API to fetch stock information for a chosen stock, including Symbol, Date, Open, Close, High, Low, and Volume. It executes once a day at 9am CET time.

#### 2. Data Storage and Population

    Function Name: main_save_lambda.py
    Description: This AWS Lambda function is triggered upon the successful execution of the initial data retrieval function. It takes the retrieved stock information and populates a Google Spreadsheet with the data.

#### 3. Streamlit Cloud Frontend

    File Name: stocks_app.py
    Description: This Streamlit web application fetches data from the Google Sheets populated by the second Lambda function. It provides a user-friendly interface for visualizing the stock data through interactive graphs and charts.

#### Understanding Stock Data Fields

    fOpen: The opening price of the stock on a given date.
    fClose: The closing price of the stock on a given date.
    fHigh: The highest price of the stock on a given date.
    fLow: The lowest price of the stock on a given date.
    fVolume: The trading volume (number of shares traded) on a given date.

#### Different Types of Graphs

The Streamlit frontend offers various interactive graphs to analyze stock data:

    Daily Trading Volume: This graph displays the daily trading volume for the selected stock, helping users identify patterns in trading activity.

    Bollinger Bands: Bollinger Bands provide insights into stock price volatility by showing the price's upper and lower bands relative to its moving average.

    Daily High vs. Low Price: This graph visualizes the daily high and low prices for the selected stock, allowing users to observe price fluctuations throughout the day.

#### Getting Started

To view the app, follow the link https://maxwells-stock-analysis.streamlit.app/

#### License

This project is licensed under the MIT License.

#### Acknowledgments

    Mention any libraries, frameworks, or APIs used.
    Give credit to any contributors or sources of inspiration.

Feel free to expand on each section with more details, code snippets, and usage instructions as needed. This outline provides a structure for your README.txt to effectively convey the purpose and functionality of your project.