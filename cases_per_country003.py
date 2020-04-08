from bs4 import BeautifulSoup as bs
from collections import Counter
import csv
from datetime import date
import json
import os
import pandas as pd
import regex as re
import requests
from requests_html import HTMLSession
import sys


#Build dictionary of case numbers
#Access the internet resource to be scraped
# URL2 = r'https://en.wikipedia.org/wiki/2019%E2%80%9320_coronavirus_pandemic'
URL2 = r'https://www.worldometers.info/coronavirus/#countries'
response = requests.get(URL2)
soup = bs(response.text, 'html.parser')

#finds the on the wikipwdia page
# table = soup.find('table', {'id':'thetable'})
table = soup.find('table', {'id':'main_table_countries_today'})

rows = table.find_all('tr')
cols = [v.text for v in rows[0].find_all('th')]

#regular expressions to find data
reChartTitleCases = re.compile(r'coronavirus-cases-linear')
reChartTitleDeaths = re.compile(r'coronavirus-deaths-linear')
reLabels = re.compile(r'categories:\[.*?\]')
reData = re.compile(r'data:\[.*?\]')


totalCases = {}
totalDeaths = {}

labels = []
# numOfCases = []
# numOfDeaths = []

for i in range(2,len(rows) - 1):
    try:
        #find country names to redirect to individual country websites
        c = rows[i].find('td', {'class': ''}).text
        c_name = c.casefold().replace(' ','-')
        if c_name == 'usa':
            c_name = c_name[:2]
        if c_name == 's.-korea':
            c_name = 'south-korea'
        if c_name == 'czechia':
            c_name = 'czech-republic'
        if c_name == 'uae':
            c_name = 'united-arab-emirates'
        if c_name == 'hong-kong':
            c_name = 'china-hong-kong-sar'
        if c_name == 'north-macedonia':
            c_name = 'macedonia'
        if c_name == 'ivory-coast':
            c_name = 'cote-d-ivoire'
        if c_name == 'palestine':
            c_name = 'state-of-palestine'
        if c_name == 'vietnam':
            c_name = 'viet-nam'
        if c_name == 'drc':
            c_name = 'democratic-republic-of-the-congo'
        if c_name == 'brunei-':
            c_name = 'brunei-darussalam'
        if c_name == 'macao':
            c_name = 'china-macao-sar'
        if c_name == 'eswatini':
            c_name = 'swaziland'
        if c_name == 'turks-and-caicos':
            c_name = 'turks-and-caicos-islands'
        if c_name == 'car':
            c_name = 'central-african-republic'
        if c_name == 'vatican-city':
            c_name = 'holy-see'
        if c_name == 'st.-vincent-grenadines':
            c_name = 'saint-vincent-and-the-grenadines'
        if c_name == 'st.-barth':
            c_name = 'saint-barthelemy'
        if c_name == 'falkland-islands':
            c_name = 'falkland-islands-malvinas'
        if c_name == 'saint-pierre-miquelon':
            c_name = 'saint-pierre-and-miquelon'
        if c_name == 'ms-zaandam':
            continue
        if c_name == 'diamond-princess':
            continue
        print(c_name)
        countryURL = r'https://www.worldometers.info/coronavirus/country/'+c_name
        session = HTMLSession()

        countryResponse = session.get(countryURL)
        
        countrySoup = bs(countryResponse.text, 'lxml')
        # cases = countrySoup.find_all('div', {'class':'maincounter-number'})
        scripts = countrySoup.find_all('script', {'type':'text/javascript'})


        # countryResponse.html.search('Cases')
        for n, script in enumerate(scripts):
            data = script.text.replace(' ','').replace('\n','')
            # print(data)
            dataMatchCases = reChartTitleCases.search(data)
            dataMatchDeaths = reChartTitleDeaths.search(data)
            if dataMatchCases:                
                labels = reLabels.findall(data)[0].replace('categories:[','').replace(']','').replace('\"','').split(',')
                rawData = reData.findall(data)[0].replace('data:[','').replace(']','').split(',')
                # numOfCases = {c_name : list(map(int,rawData))}
                # print(numOfCases)
                totalCases[c_name] = list(map(int,rawData))
            elif dataMatchDeaths:
                labels = reLabels.findall(data)[0].replace('categories:[','').replace(']','').replace('\"','').split(',')
                rawData = reData.findall(data)[0].replace('data:[','').replace(']','').split(',')
                totalDeaths[c_name] = list(map(int,rawData))
            else:
                pass

            # print(script.text.replace(' ','').replace('\n',''))
            # for m in script.children:
            #     print(type(m), len(m))
            #     print(m)
            #     # print(script)
            # print('=============================')
        if i == 2:
            labels.insert(0,'country')
        #     # filewriter.writerow(labels)
        #     numOfCases.insert(0, c_name)
        #     numOfDeaths.insert(0, c_name)
        #     # filewriter.writerow(rawData)
        # else:
        #     numOfCases.insert(0, c_name)
        #     numOfDeaths.insert(0, c_name)
        #     # filewriter.writerow(rawData)
        
        # cases = rows[i].find_all('td')[1].text
        # print(graph)
        break
        
    except Exception as e:
        print(e)
        break

print("Data for the past {} days".format(len(labels) - 1))
print(totalCases)
# print("Case data for {} countries".format(len(totalCases) - 1))
# print("Death data for {} countries".format(len(totalDeaths) - 1))

#initialise new .csv file for cases
#Populate .csv file
with open('COVID_cases_country.csv', 'w', newline = '') as csvfile:
    filewriter = csv.writer(csvfile, delimiter=',',quotechar='|', quoting = csv.QUOTE_MINIMAL)
    filewriter.writerow(labels)
    for k in totalCases.keys():
        # print(k)
        # print(totalCases[k])
        row = totalCases[k]
        row.insert(0,k)
        filewriter.writerow(row)


#initialise new .csv file for deaths
#Populate .csv file
with open('COVID_deaths_country.csv', 'w', newline = '') as csvfile:
    filewriter = csv.writer(csvfile, delimiter=',',quotechar='|', quoting = csv.QUOTE_MINIMAL)
    filewriter.writerow(labels)
    for k in totalDeaths.keys():
        # print(k)
        # print(totalCases[k])
        row = totalDeaths[k]
        row.insert(0,k)
        filewriter.writerow(row)