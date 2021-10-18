
"""
Python version: 3.9.7
Numpy version: 1.21.2
Pandas version: 1.3.3
Programmed by Richard Post

Currently I am working with multiple software-(data) teams for a major American
company in the Netherlands, but not as developer (I am working as a Scrum Master).
Actually I want to move into (Python/Numpy/Pandas) coding, for Data Science.
So this is about my journey to move into that area. I realize that I need to
spend a lot of time to be a good developer.

A long time ago I have been a developer (Pascal). I am very eager to learn
Python, Numpy , Pandas, Spark. I have spend already a lot of time to learn
Python/Numpy/Pandas via CodeCademy, so now it's time to bring my learnings into
practice.

This project is about statistics regarding Covid in the Netherlands.
To learn fast and to share my knowledge I added as much comments as possible.
The program will pull live Covid-19 data via web-scraping.
There are a lot of numbers available from many countries. In this project
I generate relevant Covid-19 graphs focusing on the Netherlands, to Visual
analyse in a realtime way how we are doing at this moment in the Netherlands.
While creating the graphs I will have more ideas on exactly what I would
like to analyse. This project will evolve while working on it.

For this project the following steps are take:
Data Collection (acquiring correct data at right time)
Data Pre Processing
EDA (Exploratory Data Analysis)
Conclusions (did the analysis answer our questions, was there a limitation
in our analysis which could affect our conclusion, was analysis sufficient
enough in decision making).

"""

from bs4 import BeautifulSoup as soup #used to webscrape data from Worldometers
from datetime import date, datetime #we want to show user that we are updating
#data at a particular time
from urllib.request import Request, urlopen
import pandas as pd
import numpy as np

import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px
import plotly.offline as py
import seaborn as sns
import gc
import warnings
warnings.filterwarnings("ignore")
from pandas_profiling import ProfileReport


today = datetime.now() #to get the previous day data, which is the complete dataset
yesterday_str = "%s %d,%d" %(date.today().strftime("%b"), today.day-1, today.year)
#for debugging: 'print(yesterday_str)' should print the date of yesterday

#==============================================================
#WEBSCRAPING
#==============================================================

url = "https://www.worldometers.info/coronavirus/#countries"
req = Request(url, headers={'User-Agent':"Mozilla/5.0"})
webpage = urlopen(req)
page_soup = soup(webpage, "html.parser") #pass http response to beautifulsoup
#for debugging: 'print(page_soup)' will show you the complete webpage.

#we don't want the complete data for the webpage, but only the specific table
#with country data. Just check for the tablename in the Webpage (view as source)
table = page_soup.findAll("table",{"id": "main_table_countries_yesterday"})

#Grab the title bar [0] of the table and assign it to variable containers
#if you use [1] it will grab the row below that
containers = table[0].findAll("tr",{"style":""})
title = containers[0]

del containers[0]
#Create empty list all_data which will hold all of its table data
all_data = []
clean = True

for country in containers:
    country_data = [] #temp store the country data in this list
    country_container = country.findAll("td") #country_container provides the
    #list of components present in that country. e.g. if you take country_container
    #India then we will have all the values with respect of India, presented as
    #a list

    if country_container[1].text == "China":
        continue
    for i in range(1, len(country_container)):
        final_feature = country_container[i].text #i = index
        if clean : #clean is initially defined as True
            if i != 1 and i != len(country_container)-1:
                #clean our data a bit
                final_feature = final_feature.replace(",","") #replacing , with empty space

                if final_feature.find('+') != -1:
                    final_feature = final_feature.replace("+","") #replacing + with empty space
                    final_feature = float(final_feature)
                elif final_feature.find("-") != -1:
                    final_feature = final_feature.replace("-", "") #replacing - with empty space
                    final_feature = float(final_feature)*-1
        if final_feature == 'N/A': #if missing data (N/A)
            final_feature = 0
        elif final_feature == "" or final_feature == " ": #if empty space or space
            #replace with -1
            final_feature = -1

        country_data.append(final_feature) #add cleaned final_feature data to
        #the list country_data

    all_data.append(country_data) #once out of the for loop all country_data will
    #be added to the list all_data
#for debug: 'print all_data()' should print data for all countries as a list

#now let's put the data in a form of a DataFrame, using Pandas.
df = pd.DataFrame(all_data)

#Remove columns with missing or incomplete data
df.drop([15,16,17,18,19,20], inplace= True, axis =1)
#For debugging: 'print(df.head())' should list the data in table form
df.head()

#Convert everything to numeric, except for Country and Continent
for label in df.columns:
    if label != 'Country' and label != "Continent":
        df[label] = pd.to_numeric(df[label], errors='ignore')
        #df[label] = pd.to_numeric(df[label])

#best way to get the column names is to scrape them with a for loop.
#but for now I hardcode them (sorry.... :-))
column_labels = ["Country", "Total Cases", "New Cases", "Total Deaths",
                 "New Deaths", "Total Recovered", "New Recovered",
                 "Active Cases", "Serious/Critical", "Total Cases/1M",
                 "Deaths/1M", "Total Tests", "Test/1M","Population",
                 "Continent"]

#Show titles on top of our columns
df.columns = column_labels

#with Pandas Dataframes its very simple to calculate in table columns and rows
df["%Inc Cases"] = df["New Cases"]/df["Total Cases"]*100
df["%Inc Deaths"] = df["New Deaths"]/df["Total Deaths"]*100
df["%Inc Recovered"] = df["New Recovered"]/df["Total Recovered"]*100

#==============================================================
#EDA (Exploratory Data Analysis)
#==============================================================

"""
#we use a DataFrame because we want to pick values, we use loc[0] because we need
the value
cases = df[["Total Recovered", "Active Cases", "Total Deaths"]].loc[0]
#print(cases)
cases_df = pd.DataFrame(cases).reset_index()
cases_df.columns = ["Type", "Total"]
cases_df["Percentage"] = np.round(100*cases_df['Total']/np.sum(cases_df["Total"]),2)
cases_df["Virus"] = ["COVID-19" for i in range(len(cases_df))]
"""

cases = df[["New Cases", "New Recovered", "New Deaths"]].loc[0]
#for debugging: print(cases)

#Add cases into a DataFrame
cases_df = pd.DataFrame(cases).reset_index()

#Add "Type", "Total", "Percentage" and "Virus" to the Cases Dataframe.
cases_df.columns = ["Type", "Total"]
cases_df["Percentage"] = np.round(100*cases_df['Total']/np.sum(cases_df["Total"]),2)
cases_df["Virus"] = ["COVID-19" for i in range(len(cases_df))]
#for debugging: print(cases_df)

# create a new Dataframe from the start (same explanation as above)
per = np.round(df[["%Inc Cases", "%Inc Deaths", "%Inc Recovered"]].loc[0], 2)
per_df = pd.DataFrame(per)
per_df.columns = ["Percentage"]

# For plotting we are using Plotly instead of Seaborn or Matplotlib,
# because Plotly gives us a better visualization
fig = go.Figure()
fig.add_trace(go.Bar(x=per_df.index, y = per_df['Percentage'],
                     marker_color = ["Yellow", "blue", "red"]))
# Hide for now, just uncomment to see the bar-charts
# fig.show()

# use bar-graph, and pass dataset cases, x-axis, y-axis and color, and show "total"
# when hovering over graph
fig = px.bar(cases_df, x = "Virus", y = "Percentage", color = "Type",
             hover_data=["Total"])
# Hide for now, just uncomment to see the bar-charts
# fig.show()


#==============================================================
# PLOT PER CONTINENT
#==============================================================

# Create a DataFrame Continent, get the continents which are same by
# name(groupby) and sum the rows.
continent_df = df.groupby("Continent").sum().drop("All")
# Generate an index while plotting
continent_df = continent_df.reset_index()
# for debugging 'print(continent_df)'


#=============================================================
# FUNCTION WHICH RECEIVES LIST OF DATA AND CREATE THE OUTPUT
#=============================================================

# vis_list = list of data which need to be visualized
def continent_visualization(vis_list):
    for label in vis_list:
        # take the column 'Continent' and 'label'
        c_df = continent_df[['Continent', label]]
        # calculate percentage and do rounding. Label(data) could be any columnn.
        c_df['Percentage'] = np.round(100*c_df[label]/ np.sum(c_df[label]), 2)
        c_df['Virus'] = ["COVID-19" for i in range (len(c_df))]
        # here we define also the (6) different colours for the Continent
        fig = px.bar(c_df, x="Virus", y="Percentage", color="Continent",
                     hover_data=[label])
        # Show label in Title
        fig.update_layout(title={"text":f"{label}"})
        fig.show()
        gc.collect()

cases_list = ["Total Cases", "Active Cases", "New Cases", "Serious/Critical",
              "Total Cases/1M"]
deaths_list = ["Total Deaths", "New Deaths", ""]
recovered_list = ["Total Recovered", "New Recovered", "%Inc Recovered"]

print (continent_df)
continent_visualization(cases_list)

#==============================================================
# PLOT PER COUNTRY
#==============================================================

# create a new DataFrame
df = df.drop([len(df)-1])
# we don't want the first row (which are stats for 'World')
country_df = df.drop([0])
# for debugging: 'print(country_df)'
# Variable 'LOOK_AT' represents how many top countries you want to look at
LOOK_AT = 5
# create a DF and look into top 5 countries affected with Covid
# we take it from 1 since we don't need the country-names
country = country_df.columns[1:14]
fig = go.Figure()
c=0
for i in country_df.index:
    if c < LOOK_AT:
        # loop through the top country index till a max of LOOK_AT
        fig.add_trace(go.Bar(name = country_df['Country'][i], x = country,
                             y = country_df.loc[i][1:14]))
    else:
        break
    c += 1
# for yaxis_type we use "log" since we want to normalize data instead of having
# numerical data (coverting into log), otherwise we will miss some
# visual data on our chart
fig.update_layout(title = {"text":f'top {LOOK_AT} countries affected'},
                  yaxis_type = "log")
fig.show()

#==============================================================
# SPECIFIC ANALYSIS FOR THE NETHERLANDS
#==============================================================

# To come.......




















