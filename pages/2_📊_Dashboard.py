import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import math
from app_utils import *

# Dashboard title
st.title("Bets Report ⚽️")

st.sidebar.title("Parameters")
bankroll = st.sidebar.number_input("Enter your Bankroll",value=570)


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
            'PROBABILITY':'Bet Outcome Probability',
            'TIME_':'Time'
        }
    )

leagues = st.sidebar.multiselect("Filter by League",df.Tournament.unique())
if len(leagues)!=0:
    df = df[df['Tournament'].isin(leagues)]
markets = st.sidebar.multiselect("Filter by Market",df.Market.unique())
if len(markets)!=0:
    df = df[df['Market'].isin(markets)]
min_ev = st.sidebar.number_input("Select the minium EV",min_value=0.0,value=0.03)
df = df[df.EV>=min_ev]

st.sidebar.markdown('''
    Created by [Daniel Guerrero](https://twitter.com/danielguerrer0s)

    Visit [My Blog](https://medium.com/@danielguerrerosantaren)
''')
df["Date"] = pd.to_datetime(df["Date"],format='%d/%m/%Y %H:%M')
df["Time"] = df["Date"].astype(str)
new_bets = df[df['Outcome'].isna()].sort_values('Date',ascending=False).reset_index(drop=True).round(3)
new_bets['Date'] = new_bets['Date'].dt.date
new_bets['Bankroll'] = np.round(new_bets['Stake']*bankroll,3)
df = df.dropna(subset='Outcome')

df['Bankroll'] = df['Stake']*bankroll
df['Payout'] = df[['Bet','Outcome','Bankroll','Odd']].apply(lambda x: x[2]*x[3] if x[0]==x[1] else (0 if x[0]!=x[1] else None), axis=1)

win_bets = len(df[df["Payout"]>0])
total_bets = len(df)


# Calculate the total amount of money bet and payout for the last 30 days and the 30 days prior
today = datetime.now()
df_last_30_days = df[(df['Date'] >= today - timedelta(days=7)) & (df['Date'] <= today)]
df_30_days_prior = df[(df['Date'] >= today - timedelta(days=13)) & (df['Date'] <= today - timedelta(days=7))]
total_stake_last_30_days = df_last_30_days['Bankroll'].sum()
total_payout_last_30_days = df_last_30_days['Payout'].sum()
total_stake_30_days_prior = df_30_days_prior['Bankroll'].sum()
total_payout_30_days_prior = df_30_days_prior['Payout'].sum()

roi_last_30_days = np.round(100*(total_payout_last_30_days - total_stake_last_30_days) / total_stake_last_30_days,2)
roi_30_days_prior = np.round(100*(total_payout_30_days_prior - total_stake_30_days_prior) / total_stake_30_days_prior,2)

if math.isnan(roi_30_days_prior):
    roi_30_days_prior = 0

# Calculate the delta between the two periods
delta_roi = roi_last_30_days - roi_30_days_prior


total_stake = df['Bankroll'].sum()
total_payout = df['Payout'].sum()



# Calculate the ROI
roi = np.round(100*(total_payout - total_stake) / total_stake,2)


data = df.copy()
data['Date'] = data['Date'].dt.date
data = data.groupby('Date').sum().reset_index()
data['Profit'] = data['Payout'] - data['Bankroll']
data['Cumulative Profit'] = data['Profit'].cumsum()

data['ROI'] = np.round(100*((data['Payout']-data['Bankroll'])/data['Bankroll']),2)

# cumulative ROI
data['Cumulative ROI'] = 100* (data['Payout'].cumsum() - data['Bankroll'].cumsum())/(data['Bankroll'].cumsum())



kpi1,kpi2,kpi3,kpi4,kpi5 = st.columns(5)

kpi1.metric(label="ROI last 7 days", value=roi_last_30_days, delta= np.round(delta_roi,2))
kpi2.metric(label="ROI historically", value=roi)
kpi3.metric(label="Total bets", value = total_bets)
kpi4.metric(label="Corrects bets %", value=round((win_bets/total_bets)*100,2))
kpi5.metric(label="Cummulative Profit",value=round(data['Profit'].sum(),2))


fig,ax =plt.subplots(figsize=(5,2)) 


for index, row in data.iterrows():
    if row['ROI'] >= 0:
        ax.bar(row['Date'], row['ROI'], color='green', alpha=0.5)
    else:
        ax.bar(row['Date'], row['ROI'], color='red', alpha=0.5)

ax.set_ylabel('ROI', color='black')


ax.plot(data['Date'], data['Cumulative ROI'], color='blue', label='Cumulative ROI')
plt.xticks(rotation=45, ha='right')
ax.grid(True,linestyle='--', alpha=0.5)
# add labels and legend
ax.set_xlabel('Date')
ax.set_title('Daily ROI')


c1,c2 = st.columns(2)
with c1:
    st.markdown("### Chart")
    st.write(fig)
with c2:
    st.markdown("### Data per day")
    data = data.sort_values("Date",ascending=False).set_index("Date").head(7)
    st.dataframe(data[['Bankroll','Payout','Profit','ROI']].rename(columns={"Bankroll":"Stake"}).round(2))


st.markdown("### New bets")
st.dataframe(new_bets[['Date','Tournament','Match','Bet','Bookie','Odd','Bankroll','EV']].rename(columns={"Bankroll":"Stake"}).set_index("Date"))

st.markdown("### All bets")

st.dataframe(df[["Date","Tournament","Match","Bookie","Odd","Bankroll","Bet","Outcome","Payout","EV"]].rename(columns={"Bankroll":"Stake"}).sort_values("Date",ascending=False).set_index("Date"))



c3,c4 = st.columns(2)
df['Correct'] = (df['Payout']>0).astype(int)

df_tournament = df.groupby('Tournament').agg(
    Percentage = ('Correct',np.mean),
    Correct = ('Correct',np.sum),
    Total = ('Correct','count'),
    Stake = ('Stake',np.sum),
    Bankroll = ('Bankroll',np.sum),
    Payout = ('Payout',np.sum)
).sort_values('Total',ascending=False).round(2)
with c3:
    st.markdown("## Statistics per Tournament")
    st.dataframe(df_tournament[['Percentage','Correct','Total']])
df_tournament['Profit'] = df_tournament['Payout'] - df_tournament['Bankroll']

fig3,ax3 =plt.subplots(figsize=(5,2)) 
df_tournament.sort_values('Profit',ascending=False)['Profit'].head(15).plot.bar(ax=ax3)
with c4:
    st.markdown("## Statistics per Bookie")
    per_Bookie=df.groupby("Bookie").sum()[['Bankroll','Payout']].rename(columns={"Bankroll":"Stake"})
    per_Bookie["Profit"] = per_Bookie["Payout"] - per_Bookie["Stake"]
    per_Bookie["ROI"] = 100*(per_Bookie["Profit"]/per_Bookie["Stake"])
    st.dataframe(per_Bookie.sort_values("ROI",ascending=False).round(2))