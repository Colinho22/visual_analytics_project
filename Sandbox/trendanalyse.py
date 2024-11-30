import pandas as pd
from datetime import date
import streamlit as st
import numpy as np
from sklearn.linear_model import LinearRegression
from statsmodels.tsa.statespace.sarimax import SARIMAX

import plotly.graph_objs as go

def linReg(x, y):
    model = LinearRegression()
    model.fit(x, y)
    y_pred = model.predict(x)
    return y_pred

def autoCorrlation(y):
    p, d, q = 1, 1, 1
    P, D, Q, s = 1, 1, 1, 12
    model = SARIMAX(y, order=(p, d, q), seasonal_order=(P, D, Q, s))
    results = model.fit()
    return results

def generate_continuation(results, forecast_periods):
    forecast = results.get_forecast(steps=forecast_periods)
    forecast_mean = forecast.predicted_mean
    return forecast_mean

def fillUpDates(dates):
    fullDateList = []
    for curr_date in dates:
        if isinstance(curr_date, date):
            lastMonth = curr_date.month
            lastYear = curr_date.year
            fullDateList.append(curr_date)
        else:
            lastMonth += 1
            if lastMonth == 13:
                lastMonth = 1
                lastYear += 1
            nextDate = date(lastYear, lastMonth, 1)
            fullDateList.append(nextDate)
    return fullDateList

def maxSquaredError(x,y):
    maxSE = 0
    maxIndex = 0
    for i in range(len(x)):
        if isinstance(x[i], float) and isinstance(y[i], float):
            curr_se = (x[i] - y[i])**2
            if curr_se > maxSE:
                maxSE = curr_se
                maxIndex = i

    # Array aufbauen, mit alles NaN ausser dem maxSquareError Wert
    out = [np.nan] * len(x)
    out[maxIndex] = x[maxIndex]
    return out

#### Import Data aus csv ####
# data = pd.read_csv('ngdata.csv') # fuer lokales deployment
data = pd.read_csv('https://raw.githubusercontent.com/Colinho22/visual_analytics_project/main/Sandbox/ngdata.csv', #für streamlit online deployment
                   on_bad_lines='skip',  # Falsch formatierte Einträge im CSV werden geskipped
                   encoding='utf-8')     # Encoding um Fehler bei der Interpretation zu verhindern
data = data.dropna(axis=0, how='any')
#Daten stammen asu dem Kaggle Datensatz: https://www.kaggle.com/datasets/alistairking/natural-gas-usage


#### Datacleaning ####
#Unnötige spalten entfernen
#alle units sind MMCF --> Spalte kann weg
#alle product-names sind natural Gas --> Spalte kann weg
#series ud series-description werden nicht beötigt
#duoarea and are-name haben denselben Inhalt anders formatiert --> nur duoare behalten

#übrig bleibende Spalten: year, month, duoarea, value
data = data[['year', 'month', 'duoarea','value']]
areas = data['duoarea'].unique()


#### Jahr und Monat Spalte mit "date" Spalte ersetzen ####
DATE = []
DATEname = []
for y, m in zip(data.year, data.month):
    DATE.append(date(y, m, 1))
    DATEname.append(f"{m}-{y}")

data['Datum'] = DATE
data['datename'] = DATEname

data = data[['Datum', 'datename', 'duoarea', 'value']]
#Group By two sum up over dates and Areas
data = data.groupby(['Datum', 'duoarea', 'datename']).sum()



#### Alle Spalten wieder mit allen Inhalten befüllen, welche bei der Gruppierung verloren gingen ####
newDF = []
for item in data.iterrows():
    curr_date = item[0][0]
    curr_duoarea = item[0][1]
    curr_datename = item[0][2]
    curr_value = int(item[1])
    row = [curr_date, curr_duoarea, curr_datename, curr_value]
    newDF.append(row)

data = pd.DataFrame(newDF, columns=['Datum', 'duoarea', 'datename', 'Gas Verbrauch'])




#### Streamlit Seite aufbauen ####
st.write("Trendanalyse 'Natural Gas Consumption' Data")
option = st.selectbox(
    "Which State would you like to analyze?",
    (areas),
)
col1, col2= st.columns(2)

MIN_DATE = date(2014, 1, 1)
MAX_DATE = date(2024, 12, 1)
with col1:
    d_start = st.date_input("Start date",  MIN_DATE, min_value=MIN_DATE, max_value=MAX_DATE, key= "d_start")
with col2:
    d_end = st.date_input("End date", MAX_DATE, min_value=MIN_DATE, max_value=MAX_DATE,  key= "d_end")


#### Daten nach der Auswahl der Start- und Enddaten und dem Ort filtern ####
filtered_Data = data[(data.duoarea == option) & (data.Datum >= d_start) & (data.Datum <= d_end)]
filtered_Data.reset_index(inplace=True, drop=True)


#### Erstellung von Daten und Listen für weitere Verarbeitungen ####
x_dict = filtered_Data[['datename']].to_dict()
y_dict = filtered_Data[['Gas Verbrauch']].to_dict()
x_timeDict = filtered_Data[['Datum']].to_dict()

x_list =[]
for key, value in dict.items(x_dict['datename']):
    x_list.append(value)

y_list =[]
for key, value in dict.items(y_dict['Gas Verbrauch']):
    y_list.append(value)

x_timesteps = np.arange(len(filtered_Data.index))



#### Lineare Regression in die das Dataframe einfügen ####
linReg_vals = linReg(x_timesteps.reshape(-1,1), y_list)
filtered_Data['Lineare Regression'] = linReg_vals



#### Auto Korrelation in das erstellen ####
results = autoCorrlation(y_list)
n_continuation = 20
continuation = generate_continuation(results, n_continuation).tolist()

# Alle bereits existierenden Daten bleiben leer, ausser der letzte. Der Rest wird mit den AutoCorr Daten befüllt
lastVal = y_list[-1]
fullAutoCorr = [np.nan] * (len(filtered_Data)-1) + [lastVal] + continuation

# Neue AutoCorr Daten ans Ende des DF anhängen und restliche Spalten mit NaN füllen
additional = pd.DataFrame({'Auto Korrelation': fullAutoCorr})
filtered_Data = pd.concat([filtered_Data, additional], axis=1)

# Complete the x-Axis Dates
dates = filtered_Data.Datum
fullDateList = fillUpDates(dates)
filtered_Data['Datum'] = fullDateList


#### Grösste Abweichung von lin Reg ####
values = filtered_Data["Gas Verbrauch"].tolist()
linReg_vals = filtered_Data["Lineare Regression"].tolist()

mse_vals = maxSquaredError(values, linReg_vals)
filtered_Data['Max Squared Error'] = mse_vals


trace1 = go.Line(
    x=filtered_Data["Datum"],
    y=filtered_Data["Gas Verbrauch"],
    name='Gas Verbrauch',
    line=dict(color='blue', width=2)
)
trace2 = go.Line(
    x=filtered_Data["Datum"],
    y=filtered_Data["Lineare Regression"],
    name='Lineare Regression',
    line=dict(color='lightgray', width=2)
)
trace3 = go.Line(
    x=filtered_Data["Datum"],
    y=filtered_Data["Auto Korrelation"],
    name='Auto Korrelation',
    line=dict(color='lightblue', width=2)
)
trace4 = go.Scatter(
    x=filtered_Data["Datum"],
    y=filtered_Data["Max Squared Error"],
    name='Grösster Ausreisser',
    mode='markers',
    marker=dict(size=20, color="red", opacity=0.2),
)

data = [trace1, trace2, trace3, trace4]

fig = dict(data=data)
#fig.update_layout(legend=dict(orientation="h",yanchor="top", y=0.99, xanchor="left", x=0.01))

st.plotly_chart(fig, key="iris", on_select="rerun")
