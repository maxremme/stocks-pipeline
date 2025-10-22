import gspread
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from google.oauth2 import service_account

# Configure page (must be first Streamlit command)
st.set_page_config(page_title="Stock Analytics Dashboard", page_icon="📈", layout="wide")

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


# Define functions for calculating technical indicators
def calculate_bollinger_bands(data, window=20, num_std_dev=2):
    """Calculate Bollinger Bands with middle, upper, and lower bands."""
    rolling_mean = data["Previous Close"].rolling(window=window).mean()
    rolling_std = data["Previous Close"].rolling(window=window).std()

    data["bb_middle"] = rolling_mean
    data["bb_upper"] = rolling_mean + (rolling_std * num_std_dev)
    data["bb_lower"] = rolling_mean - (rolling_std * num_std_dev)
    return data


def calculate_rsi(data, window=14):
    """Calculate Relative Strength Index (RSI)."""
    delta = data["Previous Close"].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    data["rsi"] = 100 - (100 / (1 + rs))
    return data


def calculate_macd(data, fast=12, slow=26, signal=9):
    """Calculate MACD (Moving Average Convergence Divergence)."""
    exp1 = data["Previous Close"].ewm(span=fast, adjust=False).mean()
    exp2 = data["Previous Close"].ewm(span=slow, adjust=False).mean()
    data["macd"] = exp1 - exp2
    data["macd_signal"] = data["macd"].ewm(span=signal, adjust=False).mean()
    data["macd_histogram"] = data["macd"] - data["macd_signal"]
    return data


data = get_data()

# Convert numeric columns to proper data types
numeric_columns = ["Previous Close", "Open", "High", "Low", "Volume"]
for col in numeric_columns:
    data[col] = pd.to_numeric(data[col], errors='coerce')

data = data.sort_values("Date")

# Custom styling
st.markdown("""
<style>
    .main {
        background-color: #0e1117;
    }
    .stPlotlyChart {
        background-color: #1a1d29;
        border-radius: 10px;
        padding: 10px;
    }
    h1 {
        color: #00d4ff;
        font-size: 3em;
        text-align: center;
        padding: 20px 0;
    }
    h2 {
        color: #00d4ff;
        border-bottom: 2px solid #00d4ff;
        padding-bottom: 10px;
    }
    .css-1d391kg {
        padding-top: 2rem;
    }
</style>
""", unsafe_allow_html=True)

st.title("📈 Stock Analytics Dashboard")

st.write(
    "Welcome to the Stock Price Visualization app! This app allows you to explore and visualize stock price data. "
    "You can select a stock symbol from the sidebar to view its historical prices, trading volume, Bollinger Bands, "
    "and compare multiple stocks. Updated daily at 04:00 UTC."
)

symbols = data["Symbol"].unique()
selected_symbol = st.sidebar.selectbox("Select Stock Symbol", symbols)

# Filter the DataFrame based on the selected stock symbol
filtered_df = data[data["Symbol"] == selected_symbol]

# Calculate technical indicators for filtered data
filtered_df = calculate_bollinger_bands(filtered_df.copy())
filtered_df = calculate_rsi(filtered_df)
filtered_df = calculate_macd(filtered_df)

# Create interactive visualizations with modern styling
col1, col2 = st.columns([2, 1])

with col1:
    st.header("📊 Stock Price Chart")
    st.write("Historical closing prices with moving averages")

    # Calculate moving averages
    filtered_df["MA20"] = filtered_df["Previous Close"].rolling(window=20).mean()
    filtered_df["MA50"] = filtered_df["Previous Close"].rolling(window=50).mean()

    # Create enhanced line chart
    fig1 = go.Figure()

    fig1.add_trace(go.Scatter(
        x=filtered_df["Date"],
        y=filtered_df["Previous Close"],
        mode="lines",
        name="Close Price",
        line=dict(color="#00d4ff", width=2),
    ))

    fig1.add_trace(go.Scatter(
        x=filtered_df["Date"],
        y=filtered_df["MA20"],
        mode="lines",
        name="MA 20",
        line=dict(color="#ff6b6b", width=1, dash="dash"),
    ))

    fig1.add_trace(go.Scatter(
        x=filtered_df["Date"],
        y=filtered_df["MA50"],
        mode="lines",
        name="MA 50",
        line=dict(color="#51cf66", width=1, dash="dash"),
    ))

    fig1.update_layout(
        title=f"{selected_symbol} Price & Moving Averages",
        xaxis_title="Date",
        yaxis_title="Price (USD)",
        template="plotly_dark",
        hovermode="x unified",
        height=500,
    )

    st.plotly_chart(fig1, use_container_width=True)

with col2:
    st.header("📈 Key Metrics")

    # Calculate key metrics
    latest_price = filtered_df["Previous Close"].iloc[-1]
    price_change = latest_price - filtered_df["Previous Close"].iloc[-2]
    price_change_pct = (price_change / filtered_df["Previous Close"].iloc[-2]) * 100
    volume = filtered_df["Volume"].iloc[-1]
    high_52w = filtered_df["Previous Close"].max()
    low_52w = filtered_df["Previous Close"].min()

    st.metric("Current Price", f"${latest_price:.2f}", f"{price_change:.2f} ({price_change_pct:.2f}%)")
    st.metric("Volume", f"{volume:,.0f}")
    st.metric("52W High", f"${high_52w:.2f}")
    st.metric("52W Low", f"${low_52w:.2f}")

# Candlestick Chart
st.header("🕯️ Candlestick Chart")
st.write("OHLC (Open, High, Low, Close) candlestick chart showing detailed price movements")

fig_candle = go.Figure(data=[go.Candlestick(
    x=filtered_df["Date"],
    open=filtered_df["Open"],
    high=filtered_df["High"],
    low=filtered_df["Low"],
    close=filtered_df["Previous Close"],
    name="OHLC"
)])

fig_candle.update_layout(
    title=f"{selected_symbol} Candlestick Chart",
    xaxis_title="Date",
    yaxis_title="Price (USD)",
    template="plotly_dark",
    height=500,
    xaxis_rangeslider_visible=False,
)

st.plotly_chart(fig_candle, use_container_width=True)

# Volume Chart
st.header("📊 Trading Volume")
st.write("Daily trading volume with color-coded price changes")

# Create volume chart with colors based on price change
colors = ["#51cf66" if filtered_df["Previous Close"].iloc[i] >= filtered_df["Previous Close"].iloc[i-1]
          else "#ff6b6b" for i in range(len(filtered_df))]
colors[0] = "#51cf66"  # First bar default

fig2 = go.Figure(data=[go.Bar(
    x=filtered_df["Date"],
    y=filtered_df["Volume"],
    marker_color=colors,
    name="Volume"
)])

fig2.update_layout(
    title=f"{selected_symbol} Daily Trading Volume",
    xaxis_title="Date",
    yaxis_title="Volume",
    template="plotly_dark",
    height=400,
)

st.plotly_chart(fig2, use_container_width=True)

# Bollinger Bands - FIXED VERSION with middle band and fill
st.header("📉 Bollinger Bands")
st.write("Bollinger Bands show volatility and potential price reversal points (20-day SMA ± 2 std dev)")

fig3 = go.Figure()

# Add filled area between bands
fig3.add_trace(go.Scatter(
    x=filtered_df["Date"],
    y=filtered_df["bb_upper"],
    mode="lines",
    line=dict(width=0),
    showlegend=False,
    hoverinfo='skip'
))

fig3.add_trace(go.Scatter(
    x=filtered_df["Date"],
    y=filtered_df["bb_lower"],
    mode="lines",
    line=dict(width=0),
    fillcolor="rgba(68, 68, 68, 0.3)",
    fill='tonexty',
    showlegend=False,
    hoverinfo='skip'
))

# Add the middle band (SMA) - THIS WAS MISSING BEFORE!
fig3.add_trace(go.Scatter(
    x=filtered_df["Date"],
    y=filtered_df["bb_middle"],
    mode="lines",
    name="Middle Band (20-SMA)",
    line=dict(color="#ffd700", width=1, dash="dash"),
))

# Add the stock price line
fig3.add_trace(go.Scatter(
    x=filtered_df["Date"],
    y=filtered_df["Previous Close"],
    mode="lines",
    name=f"{selected_symbol} Price",
    line=dict(color="#00d4ff", width=2),
))

# Add the upper band
fig3.add_trace(go.Scatter(
    x=filtered_df["Date"],
    y=filtered_df["bb_upper"],
    mode="lines",
    line=dict(color="#ff6b6b", width=1, dash="dash"),
    name="Upper Band (+2σ)",
))

# Add the lower band
fig3.add_trace(go.Scatter(
    x=filtered_df["Date"],
    y=filtered_df["bb_lower"],
    mode="lines",
    line=dict(color="#51cf66", width=1, dash="dash"),
    name="Lower Band (-2σ)",
))

fig3.update_layout(
    title=f"{selected_symbol} Bollinger Bands (FIXED)",
    xaxis_title="Date",
    yaxis_title="Price (USD)",
    template="plotly_dark",
    hovermode="x unified",
    height=500,
)

st.plotly_chart(fig3, use_container_width=True)

# RSI (Relative Strength Index)
st.header("📈 RSI - Relative Strength Index")
st.write("RSI measures momentum - values above 70 indicate overbought, below 30 indicate oversold")

fig_rsi = go.Figure()

fig_rsi.add_trace(go.Scatter(
    x=filtered_df["Date"],
    y=filtered_df["rsi"],
    mode="lines",
    name="RSI",
    line=dict(color="#00d4ff", width=2),
))

# Add overbought/oversold lines
fig_rsi.add_hline(y=70, line_dash="dash", line_color="#ff6b6b", annotation_text="Overbought (70)")
fig_rsi.add_hline(y=30, line_dash="dash", line_color="#51cf66", annotation_text="Oversold (30)")
fig_rsi.add_hline(y=50, line_dash="dot", line_color="gray", annotation_text="Neutral (50)")

fig_rsi.update_layout(
    title=f"{selected_symbol} RSI (14-day)",
    xaxis_title="Date",
    yaxis_title="RSI",
    template="plotly_dark",
    height=400,
    yaxis=dict(range=[0, 100]),
)

st.plotly_chart(fig_rsi, use_container_width=True)

# MACD
st.header("📊 MACD - Moving Average Convergence Divergence")
st.write("MACD shows the relationship between two moving averages - useful for identifying trend changes")

fig_macd = go.Figure()

# MACD line
fig_macd.add_trace(go.Scatter(
    x=filtered_df["Date"],
    y=filtered_df["macd"],
    mode="lines",
    name="MACD",
    line=dict(color="#00d4ff", width=2),
))

# Signal line
fig_macd.add_trace(go.Scatter(
    x=filtered_df["Date"],
    y=filtered_df["macd_signal"],
    mode="lines",
    name="Signal",
    line=dict(color="#ff6b6b", width=2),
))

# Histogram
colors_macd = ["#51cf66" if val >= 0 else "#ff6b6b" for val in filtered_df["macd_histogram"]]
fig_macd.add_trace(go.Bar(
    x=filtered_df["Date"],
    y=filtered_df["macd_histogram"],
    name="Histogram",
    marker_color=colors_macd,
))

fig_macd.update_layout(
    title=f"{selected_symbol} MACD (12, 26, 9)",
    xaxis_title="Date",
    yaxis_title="MACD",
    template="plotly_dark",
    height=400,
)

st.plotly_chart(fig_macd, use_container_width=True)

# Stock Comparison Section
st.markdown("---")
st.header("🔄 Multi-Stock Comparison")

# Add a sidebar to allow users to select multiple stock symbols
st.sidebar.markdown("## 🔄 Compare Stocks")
selected_symbols_to_compare = st.sidebar.multiselect(
    "Select Stock Symbols to Compare", symbols
)

# Filter the DataFrame for selected symbols to compare
filtered_df_compare = data[data["Symbol"].isin(selected_symbols_to_compare)]

# Create an interactive line chart to overlay stock prices for comparison
if selected_symbols_to_compare:
    st.write(f"Comparing {len(selected_symbols_to_compare)} stocks: {', '.join(selected_symbols_to_compare)}")

    # Normalize prices to percentage change from first date for better comparison
    normalized_df = filtered_df_compare.copy()
    for symbol in selected_symbols_to_compare:
        symbol_mask = normalized_df["Symbol"] == symbol
        first_price = normalized_df[symbol_mask]["Previous Close"].iloc[0]
        normalized_df.loc[symbol_mask, "Normalized"] = (
            (normalized_df.loc[symbol_mask, "Previous Close"] / first_price - 1) * 100
        )

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Absolute Prices")
        fig5 = go.Figure()

        for symbol in selected_symbols_to_compare:
            symbol_data = filtered_df_compare[filtered_df_compare["Symbol"] == symbol]
            fig5.add_trace(go.Scatter(
                x=symbol_data["Date"],
                y=symbol_data["Previous Close"],
                mode="lines",
                name=symbol,
                line=dict(width=2),
            ))

        fig5.update_layout(
            title="Stock Price Comparison",
            xaxis_title="Date",
            yaxis_title="Price (USD)",
            template="plotly_dark",
            hovermode="x unified",
            height=500,
        )

        st.plotly_chart(fig5, use_container_width=True)

    with col2:
        st.subheader("Normalized Performance (%)")
        fig6 = go.Figure()

        for symbol in selected_symbols_to_compare:
            symbol_data = normalized_df[normalized_df["Symbol"] == symbol]
            fig6.add_trace(go.Scatter(
                x=symbol_data["Date"],
                y=symbol_data["Normalized"],
                mode="lines",
                name=symbol,
                line=dict(width=2),
            ))

        fig6.update_layout(
            title="Normalized Performance (% Change)",
            xaxis_title="Date",
            yaxis_title="Change from Start (%)",
            template="plotly_dark",
            hovermode="x unified",
            height=500,
        )

        st.plotly_chart(fig6, use_container_width=True)
else:
    st.info("👈 Select stocks from the sidebar to compare their performance")

# Download Section
st.sidebar.markdown("---")
st.sidebar.markdown("## 💾 Download Data")
st.sidebar.markdown(f"Download **{selected_symbol}** data with all indicators")

if st.sidebar.button("📥 Prepare Download"):
    # Define the file name
    csv_file_name = f"{selected_symbol}_data_with_indicators.csv"

    # Create a CSV string from the current selected output (filtered_df)
    csv_data = filtered_df.to_csv(index=False)

    # Use the download_button to trigger the download
    st.sidebar.download_button(
        label="⬇️ Download CSV",
        data=csv_data.encode(),
        key="csv_data",
        file_name=csv_file_name,
        mime="text/csv",
    )
    st.sidebar.success("✅ Ready to download!")

# Footer
st.sidebar.markdown("---")
st.sidebar.markdown("### 📊 Stock Analytics Dashboard")
st.sidebar.markdown("Updated daily at 04:00 UTC")
st.sidebar.markdown("Built with Streamlit & Plotly")
