'''
Created on Aug 9, 2015

@author: akshat
'''

import requests
from xml.etree import ElementTree

indicator_map = {83:"Heart Deaths"}
timeframe_map = {"33":"2013"}
county_map = {}
auth = "Key=5346643abe134855907383ecf8bd7db0"

def populate_county_map():
    f = open("FPS_county_mapping.txt","r")
    for line in f.readlines():
        if "\t" in line:
            county_map["51"+line.strip().split("\t")[1]] = line.strip().split("\t")[0]
        
populate_county_map()

f = open("indicators.csv","w")
for ind in indicator_map:
    response = requests.get("http://services.healthindicators.gov/v5/REST.svc/IndicatorDescription/" + str(ind) +"/Indicators/PageCount?" + auth)
    if response.status_code == 200:
        tree = ElementTree.fromstring(response.content)
        page_count = str(tree.find('Data').text)
        for i in reversed(range(1,int(page_count))):
            url = "http://services.healthindicators.gov/v5/REST.svc/IndicatorDescription/" + str(ind) +"/Indicators/" +str(i)+ "?" + auth
            response = requests.get(url)
            if response.status_code == 200:
                    tree = ElementTree.fromstring(response.content)
                    data = tree.find('Data')
                    for indicator in data.findall('Indicator'):
                        fips = str(indicator.find('FIPSCode').text).strip()
                        if  fips.startswith('51') and len(fips)==5 and str(indicator.find('DimensionGraphHeader').text).lower() == 'total' and str(indicator.find('DimensionGraphLabel').text).lower() == 'total':
                            f.write(indicator_map.get(ind)+ "," + county_map.get(str(indicator.find('FIPSCode').text).strip()) + "," + str(indicator.find('FloatValue').text) + "," + timeframe_map.get(str(indicator.find('TimeframeID').text).strip()) + "\n")
                         
                        
                