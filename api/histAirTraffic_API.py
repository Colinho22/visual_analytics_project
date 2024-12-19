import pandas as pd

# Link: https://data.bs.ch/explore/dataset/100078/table/?disjunctive.kategorie&sort=date

#Request Maximum 100
def getURL(startDate, endDate, offset):
    url = f'https://data.bs.ch/api/explore/v2.1/catalog/datasets/100078/records?where=date%3E%3D%22{startDate}%22AND%20date%3C%3D%22{endDate}%22&order_by=date&limit=100&offset={offset}'
    return url

def getHistoricalFlightData(startDate, endDate):
    offset = 0
    try:
        flightData = pd.read_json(getURL(startDate, endDate, offset))
    except Exception as e:
        #return empty Dataframe
        print(e)


    total_count = flightData.iloc[0]['total_count']
    rest = total_count - 100
    while rest > 0:
        offset = offset + 100
        temp = pd.read_json(getURL(startDate, endDate, offset))
        flightData = pd.concat([flightData, temp])
        rest -= 100

    data = []
    for row in flightData.iterrows():
        date = row[1]['results']['date']
        mvt = row[1]['results']['mvt']

        dict = {'date': date, 'mvt': mvt}
        data.append(dict)

    df = pd.DataFrame(data)
    df = df.groupby(['date']).agg({'mvt': 'sum'}).reset_index()

    return df



#startDate = '2022-01-01'
#endDate = '2022-04-01'
#df = getHistoricalFlightData(startDate, endDate)