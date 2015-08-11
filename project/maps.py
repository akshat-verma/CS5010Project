from bokeh.browserlib import view
from bokeh.models.widgets import VBox,HBox
from bokeh.models import RadioButtonGroup,ColumnDataSource,HoverTool
from bokeh.document import Document
from bokeh.session import Session
from bokeh.plotting import figure
from bokeh.charts import Bar
from bokeh.sampledata import us_counties
import pandas
import numpy as np
import math

us_counties=us_counties.data.copy()

data=pandas.read_csv('cancer_VA.csv');
data2=pandas.read_csv('alcohol_VA.csv');

data['county']=data['Locale'].apply(lambda x: x.split('-')[1].strip())
data2['county']=data2['Locale'].apply(lambda x: x.split('-')[1].strip())

cancer=pandas.DataFrame({'Cancer_deaths':data['Numeric Value']})
cancer.set_index(data['county'],inplace=True)


alcohol=pandas.DataFrame({'Alcohol_perc':data2['Numeric Value']})
alcohol.set_index(data2['county'],inplace=True)

data_f=pandas.concat([cancer,alcohol],axis=1)

def missing(x):
    if x=='DSU':
        return (np.float('nan'))
    else: return (x)



data_f1=data_f.applymap(missing)
data_f1['Cancer_deaths']=data_f1['Cancer_deaths'].astype('float')

data_f1['Alcohol_perc']=data_f1['Alcohol_perc'].str.strip('%')
data_f1['Alcohol_perc']=data_f1['Alcohol_perc'].astype('float')


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



county_nm=pandas.Series([us_counties[x]["name"] for x in us_counties if us_counties[x]["state"]=='va'])

data_counties=pandas.DataFrame(index=county_nm)
data_counties=pandas.concat([data_counties,data_f1],axis=1)
influencers=[dict(Liquor=[30],Parks=[20]),dict(ambience=[30],hospital_reach=[20])]

top_qtl=data_f1.quantile(0.66)
middle_qtl=data_f1.quantile(0.33)

session=Session()
document=Document()
session.use_doc('python_project')
session.load_document(document)


def update(a):    
    global county_colors
    county_colors=[]    
    
    for county in data_counties.ix[:,a]:
        if county>top_qtl[a] :
            county_colors.append("green")
        elif county>middle_qtl[a]:
            county_colors.append( "yellow")
        else:
            county_colors.append("red")    
    source.data=dict(x=va_x,y=va_y,c=county_colors,i=list(data_counties.index)) 
    inf_source.data=influencers[a]    
    bar=Bar(inf_source.data,title="Top Influencers",legend=True)
    document.clear()
    layout1=HBox(children=[layout,bar])
    document.add(layout,layout1)
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

radio=RadioButtonGroup(labels=['Cancer Deaths','Alcoholic Percentage'],active=0)
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
    


