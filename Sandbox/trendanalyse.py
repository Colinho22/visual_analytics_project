import pandas as pd
from datetime import date, datetime
import streamlit as st
from streamlit_echarts import st_echarts
import numpy as np


data = pd.read_csv('dok/data.csv')
data = data.dropna(axis=0, how='any')
#Daten stammen asu dem Kaggle Datensatz: https://www.kaggle.com/datasets/alistairking/natural-gas-usage


#Datacleaning
#Unnötige spalten entfernen
#alle units sind MMCF --> Spalte kann weg
#alle product-names sind natural Gas --> Spalte kann weg
#series ud series-description werden nicht beötigt
#duoarea and are-name haben denselben Inhalt anders formatiert --> nur duoare behalten



#übrig bleibende Spalten: year, month, duoarea, value
data = data[['year', 'month', 'duoarea','value']]
areas = data['duoarea'].unique()

#Replace year and month column with date column and remove them aftter
DATE = []
DATEname = []
for y, m in zip(data.year, data.month):
    DATE.append(date(y, m, 1))
    DATEname.append(f"{m}-{y}")

data['date'] = DATE
data['datename'] = DATEname

data = data[['date', 'datename', 'duoarea', 'value']]
print(type(data.date[0]))
#Group By two sum up over dates and Areas
data = data.groupby(['date', 'duoarea', 'datename']).sum()



#Give each row all values back (no longer grouped info columns)
newDF = []
for item in data.iterrows():
    curr_date = item[0][0]
    curr_duoarea = item[0][1]
    curr_datename = item[0][2]
    curr_value = int(item[1])
    row = [curr_date, curr_duoarea, curr_datename, curr_value]
    newDF.append(row)

data = pd.DataFrame(newDF, columns=['date', 'duoarea', 'datename', 'value'])
print(type(data.date[0]))


st.write("Trendanalyse 'Natural Gas Consumption' Data")
option = st.selectbox(
    "Which State would you like to analyze?",
    (areas),
)
d_start = st.date_input("Start date", date(2014, 1, 1), key= "d_start")
d_end = st.date_input("End date", date(2024, 12, 1), key= "d_end")

#Filter data for SFL
sflData = data[(data.duoarea == option) & (data.date >= d_start) & (data.date <= d_end)]
sflData.reset_index(inplace=True, drop=True)
x = sflData[['datename']].to_dict()
y = sflData[['value']].to_dict()


#Show as simple Line chart
st.line_chart(sflData, x="date", y="value")


#Show with e-charts to show more details and infos
options = {
    "xAxis": {
        "type": "category",
        "data": x,
    },
    "yAxis": {"type": "value"},
    "series": [{"data": y, "type": "line"}],
}

st_echarts(options=options)
