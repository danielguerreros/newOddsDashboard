import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

from app_utils import *


st.set_page_config(
    page_title = 'Bet Tracker - Dashboard',
    page_icon = '🎰',
    layout = 'wide'
)
# Dashboard title
st.title("Bets Report ⚽️")

with st.sidebar:
    dates_to_scrape = st.date_input("Dates to scrape",[],datetime.today())
    scrape = st.button("Scrape")




tab1,tab2,tab3 = st.tabs(["Create Bets","Bets","Update Bets"])

with tab1:
    if len(dates_to_scrape)==2 and scrape:
        dates = pd.date_range(start=dates_to_scrape[0],end=dates_to_scrape[1])
        for x in dates:
            st.header(f"{x.day}/{x.month}/{x.year}")
            matches = scrape_date(x.day,x.month,x.year)
            st.dataframe(matches)

            bets = create_bets(matches)
            for _, row in bets.replace(np.nan,'').iterrows():
                try:
                    add_row(row['Date'], row['Time'], row['Tournament'], row['Url'], row['Match'], row['Bet'], row['Bookie'], row['Odd'], row['Stake'], row['Outcome'], row['Ev'], row['Probability'], row['Market'])
                except Exception as e:
                    st.exception(e)
            st.header("Bets")    
            st.dataframe(bets)

with tab2:
    st.header("Next Bets")

    bankroll = st.number_input("Input your bankroll:",value=100)

    df = show_table().rename(
        columns={
            'DATE_':'Date',
            'TOURNAMENT':'Tournament',
            'URL_':'Url',
            'MATCH_':'Match',
            'BET':'Bet',
            'BOOKIE':'Bookie',
            'ODD':'Odd',
            'STAKE':'Stake',
            'Probability':'Probability',
            'OUTCOME':'Outcome',
            'MARKET':'Market',
            'PROBABILITY':'Bet Outcome Probability'
        }
    ).drop(columns=['TIME_'])
    df['Date'] = pd.to_datetime(df['Date'])
    df['Stake'] = bankroll*df['Stake']
    st.dataframe(df.round(2))

    if st.button("Update Results"):
        for i,row in df.iterrows():
            if not row['Outcome']:
                updated_outcome = find_outcome(row['Url'],row['Market'],row['Bet'])
                if updated_outcome:
                    update_outcome(str(row['Tournament']), row['Match'], row['Market'], updated_outcome)

        st.dataframe(show_table())