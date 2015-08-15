'''
Created on Aug 11, 2015
CS5010 Project
@author: Akshat Verma (av2zf)
         Paul Cherian (pmc6dn)
         Prateek Agarwal (pa7sb)
'''

import math
import operator

from bokeh.browserlib import view
from bokeh.charts import Bar
from bokeh.document import Document
from bokeh.models import RadioButtonGroup, ColumnDataSource, HoverTool
from bokeh.models.widgets import VBox, HBox
from bokeh.plotting import figure
from bokeh.sampledata import us_counties  # might have to download the data the first time
from bokeh.session import Session

import pandas as pd
import statsmodels.formula.api as sm


col_dic = {0:"Cancer_Deaths", 1:"Heart_Disease_Deaths", 2:"Respiratory_Disease_Deaths", 3:"Diabetes_Deaths"}

# Function to normalize the columns in a dataframe
def normalize(df):
    normalized = df.copy()
    for col_name in df.columns:
        max_val = df[col_name].max()
        min_val = df[col_name].min()
        normalized[col_name] = (df[col_name] - min_val) / (max_val - min_val)
    return normalized

# Function to generate regression models and return a list of models
def generate_regression_models(df):
    # Using glm function in statsmodels.formula.api class to create regression models
    heart_deaths = sm.glm(formula="Heart_Disease_Deaths ~ Obesity + Binge_Drinking + Smoking + Primary_Care + No_Insurance + Median_Household_Income + College_Degrees + Long_Term_Care_Hospital_Admissions + Unemployed_Persons + Liquor_Stores", data=df).fit()
    cancer_deaths = sm.glm(formula="Cancer_Deaths ~ Obesity + Binge_Drinking + Smoking + Primary_Care + No_Insurance + Median_Household_Income + College_Degrees + Long_Term_Care_Hospital_Admissions + Unemployed_Persons + Liquor_Stores", data=df).fit()
    diabetes_deaths = sm.glm(formula="Diabetes_Deaths ~ Obesity + Smoking + Binge_Drinking + Primary_Care + No_Insurance + Median_Household_Income + College_Degrees + Long_Term_Care_Hospital_Admissions + Unemployed_Persons + Liquor_Stores", data=df).fit()
    resp_deaths = sm.glm(formula="Respiratory_Disease_Deaths ~ Obesity + Smoking + Binge_Drinking + Primary_Care + No_Insurance + Median_Household_Income + College_Degrees + Long_Term_Care_Hospital_Admissions + Unemployed_Persons + Liquor_Stores", data=df).fit()
   
    # Appending the different models to a list
    models = []
    models.append(heart_deaths)
    models.append(cancer_deaths)
    models.append(resp_deaths)
    models.append(diabetes_deaths)
    return models

# Populate a list of tuple-list where each tuple-list has variable name and variable importance
def populate_factor_list(df):
    factor_list = []
    models = generate_regression_models(df)
    for model in models:
        p_dict = dict(zip(model.pvalues.index, model.pvalues))
        params_dict = dict(zip(model.params.index, model.params))
        filtered_dict = {k:[abs(v)] for (k, v) in params_dict.items() if p_dict.get(k) < 0.1 and k is not 'Intercept'}
        sorted_list = sorted(filtered_dict.items(), key=operator.itemgetter(1), reverse=True)
        if len(sorted_list) > 2:
            sorted_list = sorted_list[0:2] 
        factor_list.append(sorted_list)
    return factor_list

# Function to update plot data,on radio button click 
def update(a):    

    # clearing document contents
    document.clear()
    # hover tool and figure intialization
    hover = HoverTool(tooltips=[("County Name", "@i"), ("Value" , "@v")])
    p = figure(title="US Health Indicator-Virginia", toolbar_location="left",
           plot_width=900, plot_height=600, tools=[hover])

    county_colors = []   
    # assigning colors to each county according to their values 
    for county in data_counties[col_dic.get(a)]:
        if county > top_qtl[col_dic.get(a)] :
            county_colors.append("red")
        elif county > middle_qtl[col_dic.get(a)]:
            county_colors.append("yellow")
        elif not math.isnan(county):
            county_colors.append("green")
        else:
            county_colors.append("white") 
    # updating plotting data        
    source.data = dict(x=va_x, y=va_y, c=county_colors, i=county_nm, v=[round(val, 2) for val in (data_counties[col_dic.get(a)])])    
         
    data_counties_map = data_counties.reset_index()
    data_counties_map['color'] = pd.Series(county_colors)
    data_counties_map.sort(col_dic.get(a), inplace=True)    
    ind_top3 = list(data_counties_map.index[0:3])
    data_counties_map.sort(col_dic.get(a), inplace=True, ascending=False)
    ind_bot3 = list(data_counties_map.index[0:3])  
    
    
    p.patches(xs='x', ys='y', fill_color='c', source=source, alpha=0.5)
    
    # coloring top3 and bottom3 counties in mortality rates
    for i in ind_top3:
        p.patch(x=va_xs[i], y=va_ys[i], fill_color=data_counties_map.ix[i, 'color'], line_color="black", line_width=2)
    
    for i in ind_bot3:
        p.patch(x=va_xs[i], y=va_ys[i], fill_color=data_counties_map.ix[i, 'color'], line_color="blue", line_width=2)

    bar = Bar(factor_dict[a], title="Top Influencers", legend="top_right", height=600, width=450)
   
    layout = VBox(children=[radio, p])
    layout1 = HBox(children=[layout, bar])
    document.add(layout1)
    # storing document in the session/bokeh server
    session.store_document(document)

# Read data from csv file into pandas dataframe
df = pd.read_csv("indicators.csv")
# Grouping by County and Indicator and type and calulating mean of value field to output time averaged value field for each County and indicator type
df = pd.DataFrame({'Value' : df.groupby([ "County", "Indicator Type"])['Value'].mean()}).reset_index()
# Transposing the dataframe so that distinct Indicator Types become column names
df = df.pivot_table("Value", ["County"], "Indicator Type").reset_index()
# Setting county code as the index
df.set_index('County', inplace=True)
# Storing raw dataframe in raw_df
raw_df = df
# Normalizing the columns of df
df = normalize(df)
# Populating a list of dictionary where each dictionary has variable name and variable importance as key value pair
factor_dict = [dict(x) for x in populate_factor_list(df)]


us_counties = us_counties.data.copy()
# generating FIPS code for counties in VA
fips_list = [ (a * 1000 + b)for (a, b) in us_counties.keys() if a is 51]
# retrieving latitude and longitude values for counties in Virginia State
va_xs = [us_counties[x]["lons"] for x in us_counties if us_counties[x]["state"] == 'va']
va_ys = [us_counties[y]["lats"] for y in us_counties if us_counties[y]["state"] == 'va']
va_x = []
for l in va_xs:
    va_x.append([a for a in l if not(math.isnan(a))])

va_y = []
for l in va_ys:
    va_y.append([a for a in l if not(math.isnan(a))])

county_nm = pd.Series([us_counties[x]["name"] for x in us_counties if us_counties[x]["state"] == 'va'])

data_counties = pd.DataFrame(index=pd.Series(fips_list))
data_counties = pd.concat([data_counties, raw_df], axis=1)

# getting quantile values for categorising counties
top_qtl = raw_df.quantile(0.66)
middle_qtl = raw_df.quantile(0.33)

session = Session()
document = Document()
session.use_doc('python_project')
session.load_document(document)

source = ColumnDataSource(data=dict(x=[], y=[], c=[], i=[]))
inf_source = ColumnDataSource(data=dict(facs=[]))

# radio buttons intialization
radio = RadioButtonGroup(labels=['Cancer Deaths', 'Heart Disease Deaths', 'Respiratory Disease Deaths', 'Diabetes Deaths'], active=0)
radio.on_click(update)

# calling update function to intialize the plot 
update(0)

        

if __name__ == '__main__':
    link = session.object_link(document.context)
    print("Please visit %s to see the plots" % link)
    view(link)
    session.poll_document(document)
    

