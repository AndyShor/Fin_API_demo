import quandl
import streamlit as st
from datetime import datetime

quandl.ApiConfig.api_key = "YOUR_QUANDL_API_KEY"
ticker = st.sidebar.text_input("Ticker", 'MSFT')
end_date = st.sidebar.date_input('end date', value=datetime.now())
start_date = st.sidebar.date_input('start date', value=datetime(2010, 5, 31))

ticker_df = quandl.get("WIKI/" + ticker, start_date=start_date, end_date=end_date)
ticker_df['sma 15'] = ticker_df.Close.rolling(window=15).mean()

# plot graphs
st.markdown(f"Demo app showing **Closing price** and **trade volume** of a selected ticker from Quandl API")
st.markdown(f"Price of **{ticker}** ")
st.line_chart(ticker_df[['Close', 'sma 15']])
st.markdown(f"Volume of **{ticker}** ")
st.line_chart(ticker_df['Volume'])
