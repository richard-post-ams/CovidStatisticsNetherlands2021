# This project is about statistics regarding Covid in the Netherlands

# For this the following steps are take:
# Data Collection
# Data Pre Processing
# EDA
# Conclusions

from bs4 import BeautifulSoup as soup
from datetime import date, datetime
from urllib.request import Request, urlopen
import pandas as pd
import numpy as np


today = datetime.now()
yesterday_str = "%s %d,%d" %(date.today().strftime("%b"), today.day-1, today.year)

url = "https://www.worldometers.info/coronavirus/#countries"
req = Request(url, headers={'User-Agent':"Mozilla/5.0"})
webpage = urlopen(req)
page_soup = soup(webpage, "html.parser")

table = page_soup.findAll("table",{"id": "main_table_countries_yesterday"})

containers = table[0].findAll("tr",{"style":""})
title = containers[0]

del containers[0]
all_data = []
clean = True

for country in containers:
    country_data = []
    country_container = country.findAll("td")

    if country_container[1].text == "China":
        continue
    for i in range(1, len(country_container)):
        final_feature = country_container[i].text
        if clean :
            if i != 1 and i != len(country_container)-1:
                final_feature = final_feature.replace(",","")

                if final_feature.find('+') != -1:
                    final_feature = final_feature.replace("+","")
                    final_feature = float(final_feature)
                elif final_feature.find("-") != -1:
                    final_feature = final_feature.replace("-", "")
                    final_feature = float(final_feature)*-1
        if final_feature == 'N/A':
            final_feature = 0
        elif final_feature == "" or final_feature == " ":
            final_feature = -1

        country_data.append(final_feature)

    all_data.append(country_data)

df = pd.DataFrame(all_data)

#df.drop([15,16,17], inplace= True, axis =1)
df.drop([15,16,17,18,19,20], inplace= True, axis =1)
df.head()
print(df.head())

for label in df.columns:
    if label != 'Country' and label != "Continent":
        df[label] = pd.to_numeric(df[label], errors='ignore')
        #df[label] = pd.to_numeric(df[label])

column_labels = ["Country", "Total Cases", "New Cases", "Total Deaths", "New Deaths", "Total Recovered", "New Recovered", "Active Cases", "Serious/Critical", "Total Cases/1M", "Deaths/1M", "Total Tests", "Test/1M","Population", "Continent"]
df.columns = column_labels

df["%Inc Cases"] = df["New Cases"]/df["Total Cases"]*100
df["%Inc Deaths"] = df["New Deaths"]/df["Total Deaths"]*100
df["%Inc Recovered"] = df["New Recovered"]/df["Total Recovered"]*100















