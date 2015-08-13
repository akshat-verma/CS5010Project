'''
Created on Aug 11, 2015

@author: akshat
'''
import pandas as pd
import statsmodels.formula.api as sm
from bokeh.browserlib import view
from bokeh.models.widgets import VBox,HBox
from bokeh.models import RadioButtonGroup,ColumnDataSource,HoverTool
from bokeh.document import Document
from bokeh.session import Session
from bokeh.plotting import figure
from bokeh.charts import Bar
from bokeh.sampledata import us_counties
import numpy as np
import math
from sympy.printing.pretty.pretty_symbology import MID



df = pd.read_csv("indicators.csv")
df = pd.DataFrame({'Value' : df.groupby( [ "County", "Indicator Type"] )['Value'].mean()}).reset_index()
df = df.pivot_table("Value",["County"],"Indicator Type").reset_index()
df.set_index('County',inplace=True)



'''
result = sm.ols(formula="Heart_Deaths ~ Obesity", data=df).fit()
print(dict(zip(result.pvalues.index,result.pvalues)))
'''
#Regression

heart_deaths = sm.ols(formula="Heart_Disease_Deaths ~ Obesity + Binge_Drinking + Smoking + Primary_Care + No_Insurance + Median_Household_Income + College_Degrees + Long_Term_Care_Hospital_Admissions + Unemployed_Persons + Liquor_Stores", data=df).fit()
print (heart_deaths.summary())
print(dict(zip(heart_deaths.pvalues.index,heart_deaths.pvalues)))

cancer_deaths = sm.ols(formula="Cancer_Deaths ~ Obesity + Binge_Drinking + Smoking + Primary_Care + No_Insurance + Median_Household_Income + College_Degrees + Long_Term_Care_Hospital_Admissions + Unemployed_Persons + Liquor_Stores", data=df).fit()
print(dict(zip(cancer_deaths.pvalues.index,cancer_deaths.pvalues)))

diabetes_deaths = sm.ols(formula="Diabetes_Deaths ~ Obesity + Smoking + Binge_Drinking + Primary_Care + No_Insurance + Median_Household_Income + College_Degrees + Long_Term_Care_Hospital_Admissions + Unemployed_Persons + Liquor_Stores", data=df).fit()
print(dict(zip(diabetes_deaths.pvalues.index,diabetes_deaths.pvalues)))

hiv_deaths = sm.ols(formula="HIV_Deaths ~ Obesity + Smoking + Binge_Drinking + Primary_Care + No_Insurance + Median_Household_Income + College_Degrees + Long_Term_Care_Hospital_Admissions + Unemployed_Persons + Liquor_Stores", data=df).fit()
print(dict(zip(diabetes_deaths.pvalues.index,hiv_deaths.pvalues)))

'''
us_counties=us_counties.data.copy()
fips_list = [ (a*1000+b)for (a,b) in us_counties.keys() if a is 51]



va_xs=[us_counties[x]["lons"] for x in us_counties if us_counties[x]["state"]=='va']
va_ys=[us_counties[y]["lats"] for y in us_counties if us_counties[y]["state"]=='va']

def miss(x):
    if not(math.isnan(x)):
        return(x)

va_x=[]
for l in va_xs:
    va_x.append([a for a in l if not(math.isnan(a))])

va_y=[]
for l in va_ys:
    va_y.append([a for a in l if not(math.isnan(a))])



county_nm=pd.Series([us_counties[x]["name"] for x in us_counties if us_counties[x]["state"]=='va'])

data_counties=pd.DataFrame(index=pd.Series(fips_list))
data_counties=pd.concat([data_counties,df],axis=1)
influencers=[dict(Liquor=[30],Parks=[20]),dict(ambience=[30],hospital_reach=[20])]

top_qtl=df.quantile(0.66)
middle_qtl=df.quantile(0.33)

session=Session()
document=Document()
session.use_doc('python_project')
session.load_document(document)

col_dic =  {0:"Cancer_Deaths", 1:"Heart_Disease_Deaths", 2:"HIV_Deaths", 3:"Diabetes_Deaths"}

def update(a):    
    global county_colors
    county_colors=[]    
    for county in data_counties[col_dic.get(a)]:
        if county>top_qtl[col_dic.get(a)] :
            county_colors.append("red")
            print (county,"red")
        elif county>middle_qtl[col_dic.get(a)]:
            county_colors.append( "yellow")
            print (county,"yellow")
        elif not math.isnan(county):
            county_colors.append("green")
            print (county,"green")
            print(top_qtl[col_dic.get(a)])

        else:
            county_colors.append("white") 
    source.data=dict(x=va_x,y=va_y,c=county_colors,i=list(data_counties.index)) 
    #inf_source.data=influencers[a]    
    #print(source.data['x'])

    bar=Bar(inf_source.data,title="Top Influencers",legend=True)
    document.clear()
    layout1=HBox(children=[layout,bar])
    document.add(layout1)
    session.store_document(document)
        
    
source=ColumnDataSource(data=dict(x=[],y=[],c=[],i=[]))
inf_source=ColumnDataSource(data=dict(facs=[]))

hover=HoverTool(tooltips=[("County Name","@i")])

p = figure(title="US Health Indicator-Virginia", toolbar_location="left",
           plot_width=1100, plot_height=700,tools=[hover])

#x=[[1,2,3],[4,5,6,5]]
#y=[[1,2,1],[4,5,5]]
#p.patches(xs=x, ys=y,fill_color=["#43a2ca", "#a8ddb5"])

p.patches(xs='x',ys='y', fill_color='c',source=source,alpha=0.5)
bar=Bar(inf_source.data,title="Top Influencers",legend=True)

radio=RadioButtonGroup(labels=['Cancer Deaths','Heart Disease Deaths', 'HIV Deaths', 'Diabetes Deaths'],active=0)
radio.on_click(update)


layout=VBox(children=[radio,p])
layout1=HBox(children=[layout,bar])
document.add(layout1)

update(0)


if __name__=='__main__':
    link = session.object_link(document.context)
    print("Please visit %s to see the plots" % link)
    view(link)
    session.poll_document(document)
    
'''
