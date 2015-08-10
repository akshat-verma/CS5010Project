'''
Created on Aug 9, 2015

@author: akshat
'''

import requests
from xml.etree import ElementTree

indicator_map = {83:"Heart Deaths"}
auth = "Key=5346643abe134855907383ecf8bd7db0"

for ind in indicator_map:
    response = requests.get("http://services.healthindicators.gov/v5/REST.svc/IndicatorDescription/" + str(ind) +"/Indicators/PageCount?" + auth)
    if response.status_code == 200:
        tree = ElementTree.fromstring(response.content)
        page_count = str(tree.find('Data').text)
        print (int(page_count))
        for i in reversed(range(1,int(page_count))):
            url = "http://services.healthindicators.gov/v5/REST.svc/IndicatorDescription/" + str(ind) +"/Indicators/" +str(i)+ "?" + auth
            response = requests.get(url)
            if response.status_code == 200:
                    tree = ElementTree.fromstring(response.content)
                    data = tree.find('Data')
                    for indicator in data.findall('Indicator'):
                        fips = str(indicator.find('FIPSCode').text).strip()
                        if  fips.startswith('51') and len(fips)==5 and str(indicator.find('DimensionGraphHeader').text).lower() == 'total' :
                            print(indicator_map.get(ind)+ "," + str(indicator.find('FIPSCode').text) + "," + str(indicator.find('FloatValue').text) + "," + str(indicator.find('TimeframeID').text) )
                        
                        
                