'''
Created on Aug 9, 2015

@author: akshat
'''

import requests
from xml.etree import ElementTree

indicator_map = {15:"Obesity", 13:"Smoking", 25:"Primary_Care", 34:"College_Degrees", 23:"No_Insurance", 10003:"Median_Household_Income", 51:"Liquor_Stores", 200:"Long_Term_Care_Hospital_Admissions",35:"Unemployed_Persons",50011:"Diabetes_Deaths", 486:"Cancer_Deaths", 83:"Heart_Disease_Deaths", 50012:"Respiratory_Disease_Deaths" }

auth = "Key=5346643abe134855907383ecf8bd7db0"

f = open("indicators.csv", "a")
for ind in indicator_map:
    response = requests.get("http://services.healthindicators.gov/v5/REST.svc/IndicatorDescription/" + str(ind) + "/Indicators/PageCount?" + auth)
    if response.status_code == 200:
        tree = ElementTree.fromstring(response.content)
        page_count = str(tree.find('Data').text)
        for i in range(1, int(page_count)):
            url = "http://services.healthindicators.gov/v5/REST.svc/IndicatorDescription/" + str(ind) + "/Indicators/" + str(i) + "?" + auth
            response = requests.get(url)
            if response.status_code == 200:
                    tree = ElementTree.fromstring(response.content)
                    data = tree.find('Data')
                    for indicator in data.findall('Indicator'):
                        fips = str(indicator.find('FIPSCode').text).strip()
                        print (fips)
                        if  fips.startswith('51') and len(fips) == 5 and str(indicator.find('DimensionGraphHeader').text).lower() == 'total':
                            f.write(indicator_map.get(ind)+","+str(indicator.find('FIPSCode').text).strip() + "," + ("" if indicator.find('FloatValue').text is None else str(indicator.find('FloatValue').text).strip()) + "\n")
                            
f.close()
                         
                        
                
