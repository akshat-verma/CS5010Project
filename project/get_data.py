'''
Created on Aug 9, 2015
CS 5010 Project
@author: Akshat Verma(av2zf)
         Paul Cherian(pmc6dn)
         Prateek Agarwal(pa7sb)
'''

from xml.etree import ElementTree

import requests


# Dictionary of Indicator Description Id's (as in the API) and the indicator names
indicator_map = {15:"Obesity", 13:"Smoking", 25:"Primary_Care", 34:"College_Degrees", 23:"No_Insurance", 10003:"Median_Household_Income", 51:"Liquor_Stores", 200:"Long_Term_Care_Hospital_Admissions", 35:"Unemployed_Persons", 50011:"Diabetes_Deaths", 486:"Cancer_Deaths", 83:"Heart_Disease_Deaths", 50012:"Respiratory_Disease_Deaths" }

# Authorization key to communicate with the API
auth = "Key=5346643abe134855907383ecf8bd7db0"


# Function to invoke the API service, parse the XML response and write the extracted fields to CSV file
def extract_and_write_to_file():
    f = open("Indicators.csv", "w")
    f.write("Indicator Type,County,Value\n")
    for ind in indicator_map:
        # Invoking the sepcific API service for each indicator in the indicator map and getting the response
        response = requests.get("http://services.healthindicators.gov/v5/REST.svc/IndicatorDescription/" + str(ind) + "/Indicators/PageCount?" + auth)
        if response.status_code == 200:
            # Parsing the XML response and getting the page count
            tree = ElementTree.fromstring(response.content)
            page_count = str(tree.find('Data').text)
            # Looping over all the pages
            for i in range(1, int(page_count)):
                url = "http://services.healthindicators.gov/v5/REST.svc/IndicatorDescription/" + str(ind) + "/Indicators/" + str(i) + "?" + auth
                # Invoking the service and getting the response
                response = requests.get(url)
                if response.status_code == 200:
                        # Parsing the XML response and extracting the value field pertaining to county level data in VA
                        tree = ElementTree.fromstring(response.content)
                        data = tree.find('Data')
                        for indicator in data.findall('Indicator'):
                            fips = str(indicator.find('FIPSCode').text).strip()
                            if  fips.startswith('51') and len(fips) == 5 and str(indicator.find('DimensionGraphHeader').text).lower() == 'total':
                                # writing to the csv file
                                f.write(indicator_map.get(ind) + "," + str(indicator.find('FIPSCode').text).strip() + "," + ("" if indicator.find('FloatValue').text is None else str(indicator.find('FloatValue').text).strip()) + "\n")
    f.close()

# calling the function and populating the csv file    
extract_and_write_to_file()

                            
                         
                        
                
