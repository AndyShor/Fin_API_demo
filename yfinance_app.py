import yfinance as yf
import streamlit as st
import pandas as pd
from datetime import datetime

# read SEC registered comanies
sec_list = pd.read_csv('cik_ticker.csv', sep='|',
                       names=['CIK', 'Ticker', 'Name', 'Exchange', 'SIC', 'Business', 'Incorporated', 'IRS'])
name_options = ['Microsoft Corp']
name_hint = st.sidebar.text_input(label='Company name contains')
if name_hint is not None:
    name_options = sec_list[sec_list['Name'].str.contains(name_hint, case=False)]['Name'].tolist()
if not name_options:
    name_options = ['Microsoft Corp']

# get ticker from company name and dates from UI
company_name = st.sidebar.selectbox('SEC listed companies', name_options)
ticker = sec_list.loc[sec_list['Name'] == company_name, 'Ticker'].iloc[0]
tickerData = yf.Ticker(ticker)
end_date = st.sidebar.date_input('end date', value=datetime.now()).strftime("%Y-%m-%d")
start_date = st.sidebar.date_input('start date', value=datetime(2010, 5, 31)).strftime("%Y-%m-%d")

# make API query
ticker_df = tickerData.history(period='1d', start=start_date, end=end_date)
md_chart_1 = f"Price of **{ticker}** "
md_chart_2 = f"Volume of **{ticker}** "
if len(ticker_df) == 0:
    tickerData = yf.Ticker('MSFT')
    ticker_df = tickerData.history(period='1d', start=start_date, end=end_date)
    md_chart_1 = f"Invalid ticker **{ticker}** showing **MSFT** price"
    md_chart_2 = f"Invalid ticker **{ticker}** showing **MSFT** volume"

# Add simple moving average
ticker_df['sma 15'] = ticker_df.Close.rolling(window=15).mean()

# plot graphs
st.markdown(f"Demo app showing **Closing price** and **trade volume** of a selected ticker from Yahoo! finance API")
st.markdown(md_chart_1)
st.line_chart(ticker_df[['Close', 'sma 15']])
st.markdown(md_chart_2)
st.line_chart(ticker_df.Volume)
