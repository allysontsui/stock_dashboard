import pandas as pd 
import yfinance as yf
import datetime
from datetime import date,timedelta
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

# Streamlit side bar
st.title('Stock Dashboard')
ticker_list = pd.read_csv('S&P500ticker.csv')
ticker = st.sidebar.selectbox('S&P 500 Stock ticker', ticker_list)
custom_ticker = st.sidebar.text_input('Enter Custom Ticker')
selected_ticker = custom_ticker if custom_ticker else ticker

d = date.today() - timedelta(days=365)
d1 = st.sidebar.date_input('Start Date', d)
start_date = d1.strftime("%Y-%m-%d")
d2 = st.sidebar.date_input('End Date',date.today())
end_date = d2.strftime("%Y-%m-%d")

#Get tabs
ticker_information, price_chart, analysis_chart = st.tabs(["Ticker Information", "Price Chart", "Analysis Chart"])

# Ticker info
with ticker_information: 
    tickerData = yf.Ticker(selected_ticker)
    string_name = tickerData.info['longName']
    st.header(string_name)
    string_summary = tickerData.info['longBusinessSummary']
    st.info(string_summary)

    st.header('**Ticker data**')
    tickerDf = tickerData.history(period='1d', start=start_date, end=end_date)
    st.write(tickerDf)

# Get stock price data
def get_stock_data(ticker):
    data = yf.download(ticker, start=start_date, end=end_date, progress=False)
    data['Date'] = data.index 
    data = data[["Date", "Open", "High", "Low", "Close", "Adj Close", "Volume"]]
    return data

# Get line plot
def plot_line_slider(data):
    line_trace = go.Scatter(x=data['Date'], y=data['Close'], mode='lines', name='Close')
    figure = go.Figure(data=[line_trace])
    figure.update_xaxes(rangeslider_visible=True)
    st.plotly_chart(figure)

# Get line plot based on different time period
def plot_line_time(data):
    figure = make_subplots(specs=[[{"secondary_y": True}]])
    line = go.Scatter(x=data['Date'], y=data['Close'], mode='lines', name='Close')
    bar = go.Bar(x=data['Date'],y=data['Volume'],yaxis='y2',name='Volume')
    figure.update_xaxes(rangeslider_visible=False,
        rangeselector=dict(
            buttons=list([
            dict(count=7, label="1w", step="day", stepmode="backward"),
            dict(count=3, label="3m", step="month", stepmode="backward"),
            dict(count=6, label="6m", step="month", stepmode="backward"),
            dict(count=1, label="1y", step="year", stepmode="backward"),
            dict(step="all")]))
    )
    figure.add_trace(line)
    figure.add_trace(bar)
    figure.update_layout(title="Stock Market Analysis with Time Period Selectors")
    st.plotly_chart(figure)

# Get MA
def get_ma(data, ma1, ma2):
    data[f'SMA {ma1}'] = data['Adj Close'].rolling(window=int(ma1)).mean()
    data[f'SMA {ma2}'] = data['Adj Close'].rolling(window=int(ma2)).mean()
    return data

# Get candle plot with moving average
def plot_candel_ma(data,ma1,ma2):
    figure = make_subplots(specs=[[{"secondary_y": True}]])
    candlestick_trace = go.Candlestick(x=data['Date'],open=data['Open'],high=data['High'],low=data['Low'],close=data['Close'])
    bar = go.Bar(x=data['Date'],y=data['Volume'],yaxis='y2',name='Volume')
    ma1_trace = go.Scatter(x=data['Date'], y=data[f'SMA {ma1}'], mode='lines', name=f'SMA {ma1}')
    ma2_trace = go.Scatter(x=data['Date'], y=data[f'SMA {ma2}'], mode='lines', name=f'SMA {ma2}')
    figure.update_layout(title='Stock Market Analysis with Moving Average',xaxis_rangeslider_visible=False,
                xaxis=dict(rangeselector=dict(
                    buttons=list([
                        dict(count=7, label="1w", step="day", stepmode="backward"),
                        dict(count=3, label="3m", step="month", stepmode="backward"),
                        dict(count=6, label="6m", step="month", stepmode="backward"),
                        dict(count=1, label="1y", step="year", stepmode="backward"),
                        dict(step="all")])
                    )
                )
            )
    figure.add_trace(candlestick_trace)
    figure.add_trace(bar)
    figure.add_trace(ma1_trace)
    figure.add_trace(ma2_trace)
    st.plotly_chart(figure)

# Plot all analytics chart
with price_chart:
    data = get_stock_data(selected_ticker)
    plot_line_slider(data)
    plot_line_time(data)

with analysis_chart:
    ma1_input = st.text_input('Enter the first moving average window:', 50)
    ma2_input = st.text_input('Enter the second moving average window:', 20)
    data = get_stock_data(selected_ticker)
    get_ma(data,ma1_input,ma2_input)
    plot_candel_ma(data,ma1_input,ma2_input)
