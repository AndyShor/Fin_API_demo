import streamlit as st
from alpha_vantage.timeseries import TimeSeries
from datetime import datetime
import quandl
import pandas as pd

quandl.ApiConfig.api_key = "YOUR_QUANDL_API_KEY"
ts = TimeSeries(key='YOUR_ALPHA_VANTAGE_API_KEY', output_format='pandas')

st.markdown(f"Demo app showing **Closing price** and  daily **APR change** of a selected ticker from alpha vantage API")
ticker = st.sidebar.text_input("Ticker", 'MSFT').upper()
end_date = st.sidebar.date_input('end date', value=datetime.now()).strftime("%Y-%m-%d")
start_date = st.sidebar.date_input('start date', value=datetime(2015, 5, 31)).strftime("%Y-%m-%d")


@st.cache(suppress_st_warning=True, allow_output_mutation=True)
def get_ticker_daily(ticker_input):
    ticker_data, ticker_metadata = ts.get_daily(symbol=ticker_input, outputsize='full')
    return ticker_data, ticker_metadata


try:
    price_data, price_meta_data = get_ticker_daily(ticker)
    market_data, market_meta_data = get_ticker_daily('SPY')
    md_chart_1 = f"Price of **{ticker}** "
    md_chart_2 = f"APR daily change of **{ticker}** "
except:
    price_data, price_meta_data = get_ticker_daily('MSFT')
    market_data, market_meta_data = get_ticker_daily('SPY')
    md_chart_1 = f"Invalid ticker **{ticker}** showing **MSFT** price"
    md_chart_2 = f"Invalid ticker **{ticker}** showing **MSFT** APR daily change of"


def apr_change(pandas_series_input):
    return ((pandas_series_input - pandas_series_input.shift(periods=-1,
                                                             fill_value=0)) / pandas_series_input) * 100 * 252


price_data['change'] = apr_change(price_data['4. close'])
market_data['change'] = apr_change(market_data['4. close'])

price_data_filtered = price_data[end_date:start_date]
market_data_filtered = market_data[end_date:start_date]
stock_market_correlation = price_data_filtered['change'].corr(market_data_filtered['change'], method='pearson')

# estimate risk free return via 3 months treasury bonds
treasury_yield = quandl.get("FRED/TB3MS", start_date=start_date, end_date=end_date)
rfr = treasury_yield['Value'].mean()  # mean treasury yield over period

stock_volatility = price_data_filtered['change'].std()
market_volatilidy = market_data_filtered['change'].std()
stock_excess_return = price_data_filtered['change'].mean() - rfr
market_excess_return = market_data_filtered['change'].mean() - rfr
beta = stock_market_correlation * stock_volatility / market_volatilidy
alpha = stock_excess_return - beta * market_excess_return
sharpe = stock_excess_return / stock_volatility
metrics_df = pd.DataFrame(
    data={'mkt correlation': [stock_market_correlation], 'alpha': [alpha], 'beta': [beta], 'Sharpe ratio': [sharpe]})
metrics_df.index = [ticker]

st.markdown(md_chart_1)
st.line_chart(price_data_filtered['4. close'])
st.markdown(md_chart_2)
st.line_chart(price_data_filtered['change'])

st.table(metrics_df)
