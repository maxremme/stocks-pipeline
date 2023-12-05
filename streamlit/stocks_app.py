import gspread
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from google.oauth2 import service_account

credentials_dict = st.secrets["gcp_service_account"]
# Create a connection object.
credentials = service_account.Credentials.from_service_account_info(
    credentials_dict,
    scopes=[
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ],
)


def get_data():
    """Gets all Values from a Google Spreadsheet.

    Args:
        worksheet (str): Name of the Google Spreadsheet.

    Returns:
        Pandas DataFrame: Returns a dataframe with all values from  the spreadsheet.
    """

    gc = gspread.Client(auth=credentials)

    sh = gc.open("stocks_new")

    wks = sh.worksheet("Sheet1")

    data = wks.get_all_values()

    df = pd.DataFrame(data[1:], columns=data[0])

    return df


# Define functions for calculating and plotting Bollinger Bands
def calculate_bollinger_bands(data, window=20, num_std_dev=2):
    data["rolling_mean"] = data["Previous Close"].rolling(window=window).mean()
    data["upper_band"] = data["rolling_mean"] + (
        data["Previous Close"].rolling(window=window).std() * num_std_dev
    )
    data["lower_band"] = data["rolling_mean"] - (
        data["Previous Close"].rolling(window=window).std() * num_std_dev
    )
    return data


def plot_bollinger_bands(data, symbol):
    data = calculate_bollinger_bands(data)
    return data


data = get_data()
data = data.sort_values("Date")

st.title("Stock Price Visualization")

st.write(
    "Welcome to Maxwells Stock Price Visualization app! This app allows you to explore and visualize stock price data. "
    "You can select a stock symbol from the sidebar to view its historical prices, trading volume, Bollinger Bands, "
    "and compare multiple stocks. Updated daily."
)

symbols = data["Symbol"].unique()
selected_symbol = st.sidebar.selectbox("Select Stock Symbol", symbols)

# Filter the DataFrame based on the selected stock symbol
filtered_df = data[data["Symbol"] == selected_symbol]

# Create interactive visualizations
st.header("Stock Prices Over Time")
st.write("Historical closing prices of the selected stock over time.")
# Line chart for stock prices over time
fig1 = px.line(
    filtered_df,
    x="Date",
    y="Previous Close",
    title=f"{selected_symbol} Stock Prices Over Time",
)
st.plotly_chart(fig1)

st.header("Daily Trading Volume")
st.write(
    "Daily trading volume for the selected stock, helps identify patterns in trading activity."
)
# Bar chart for daily trading volume
fig2 = px.bar(
    filtered_df, x="Date", y="Volume", title=f"{selected_symbol} Daily Trading Volume"
)
st.plotly_chart(fig2)

# Calculate and plot Bollinger Bands for the selected stock symbol
if "upper_band" not in filtered_df.columns:
    filtered_df = plot_bollinger_bands(filtered_df, selected_symbol)

    st.header("Bollinger Bands")
    st.write(
        "Bollinger Bands are used to visualize the volatility and potential price reversal points for the selected stock."
    )

    # Line chart for Bollinger Bands
    fig3 = go.Figure()

    # Add the stock price line
    fig3.add_trace(
        go.Scatter(
            x=filtered_df["Date"],
            y=filtered_df["Previous Close"],
            mode="lines",
            name=f"{selected_symbol} Price",
        )
    )

    # Add the upper and lower Bollinger Bands
    fig3.add_trace(
        go.Scatter(
            x=filtered_df["Date"],
            y=filtered_df["upper_band"],
            mode="lines",
            line=dict(dash="dash"),
            name="Upper Bollinger Band",
        )
    )

    fig3.add_trace(
        go.Scatter(
            x=filtered_df["Date"],
            y=filtered_df["lower_band"],
            mode="lines",
            line=dict(dash="dash"),
            name="Lower Bollinger Band",
        )
    )

    fig3.update_layout(
        title=f"{selected_symbol} Bollinger Bands",
        xaxis_title="Date",
        yaxis_title="Price",
    )
    st.plotly_chart(fig3)

st.header("High vs. Low Prices")
st.write(
    "This scatter plot shows the relationship between daily high and low prices of the selected stock."
)
# Scatter plot for high vs. low prices
fig4 = px.scatter(
    filtered_df, x="High", y="Low", title=f"{selected_symbol} High vs. Low Prices"
)
st.plotly_chart(fig4)

# Add a section for comparing multiple stocks

# Add a sidebar to allow users to select multiple stock symbols
st.sidebar.markdown("## Compare Stocks")
selected_symbols_to_compare = st.sidebar.multiselect(
    "Select Stock Symbols to Compare", symbols
)

# Filter the DataFrame for selected symbols to compare
filtered_df_compare = data[data["Symbol"].isin(selected_symbols_to_compare)]

# Create an interactive line chart to overlay stock prices for comparison
if selected_symbols_to_compare:
    fig5 = px.line(
        filtered_df_compare,
        x="Date",
        y="Previous Close",
        color="Symbol",
        title="Stock Price Comparison",
    )
    st.plotly_chart(fig5)

if st.sidebar.button("Download CSV"):
    # Define the file name
    csv_file_name = f"{selected_symbol}_data.csv"

    # Create a CSV string from the current selected output (filtered_df)
    csv_data = filtered_df.to_csv(index=False)

    # Use the download_button to trigger the download
    st.sidebar.download_button(
        label="Click here to download",
        data=csv_data.encode(),
        key="csv_data",
        file_name=csv_file_name,
    )

# Add an explanation for what will be downloaded
st.sidebar.markdown("Download the data for the currently selected stock as a CSV file.")
