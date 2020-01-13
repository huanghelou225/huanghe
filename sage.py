import requests
from bs4 import BeautifulSoup
import datetime
import pandas as pd
import csv

def get_date(origin):
    origin = origin[0:6]
    date = -1
    mon = -1
    if origin.find("Jan") > 1:
        mon = 1
    if origin.find("Feb") > 1:
        mon = 2
    if origin.find("Mar") > 1:
        mon = 3
    if origin.find("Apr") > 1:
        mon = 4
    if origin.find("May") > 1:
        mon = 5
    if origin.find("Jun") > 1:
        mon = 6
    if origin.find("Jul") > 1:
        mon = 7
    if origin.find("Aug") > 1:
        mon = 8
    if origin.find("Sep") > 1:
        mon = 9
    if origin.find("Oct") > 1:
        mon = 10
    if origin.find("Nov") > 1:
        mon = 11
    if origin.find("Dec") > 1:
        mon = 12
    
    if origin.find(" ") > -1 and mon > -1:
        try:
            date = int(origin[0:origin.find(" ")])
        except ValueError:
            date = -1

    return {"mon": mon, "date": date}
    
output_file = "output.csv"
year = 2019
time_range = pd.date_range("2019-01-01", "2019-12-31")
data_url = "https://en.wikipedia.org/wiki/2019_in_spaceflight#Orbital_launches"
data_source = requests.get(data_url).text

html = BeautifulSoup(data_source, 'lxml')
table = html.find('table', {'class':'wikitable collapsible'})

# get each row in the table
rows = table.findAll("tr")
i = 0

# store data
data = {}

while i < len(rows):

    cells = rows[i].findAll("td")

    if len(cells) > 0:
    
        cell = cells[0]
       
        # first see if we can get time
        time = get_date(cell.text)
        if time["mon"] > -1 and time["date"] > -1:
        # we get how many rocket it will lanch
            num_rows = 1
            if cell.has_attr("rowspan"):
                num_rows = int(cell["rowspan"])
            i = i+num_rows

            # processing time object
            tmp_time = datetime.datetime(year, time["mon"], time["date"])
            time_str = tmp_time.strftime("%Y-%m-%d")
            if time_str in data:
                data[time_str] = data[time_str] + num_rows
            else:
                data[time_str] = num_rows
        else:
            i = i+1
    else:
        i = i+1

unfilled_data = pd.Series(data)
unfilled_data.index = pd.DatetimeIndex(unfilled_data.index)
filled_data = unfilled_data.reindex(time_range, fill_value = 0)

# write to the file
with open(output_file, mode="w") as output:
    wirter = csv.writer(output, delimiter=',', quotechar='"')
    for i in range(len(filled_data)):
        time = datetime.datetime.strptime(str(filled_data.index[i]), "%Y-%m-%d %H:%M:%S")
        time = datetime.datetime.strftime(time, "%Y-%m-%dT%H:%M:%S+00:00")
        wirter.writerow([time, filled_data[i]])
