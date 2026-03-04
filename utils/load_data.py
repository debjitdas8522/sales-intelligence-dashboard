import pandas as pd
from sqlalchemy import create_engine
import streamlit as st

@st.cache_data
def load_sales_data():

    engine = create_engine("sqlite:///database/sales.db")

    df = pd.read_sql("SELECT * FROM sales_data", engine)

    df['Order Date'] = pd.to_datetime(df['Order Date'])

    return df
