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
import math
import operator



df = pd.read_csv("indicators.csv")
df = pd.DataFrame({'Value' : df.groupby( [ "County", "Indicator Type"] )['Value'].mean()}).reset_index()
df = df.pivot_table("Value",["County"],"Indicator Type").reset_index()
df.set_index('County',inplace=True)

def normalize(df):
    normalized = df.copy()
    for col_name in df.columns:
        max_val = df[col_name].max()
        min_val = df[col_name].min()
        normalized[col_name] = (df[col_name] - min_val) / (max_val- min_val)
    return normalized


df = normalize(df)


'''
result = sm.ols(formula="Heart_Deaths ~ Obesity", data=df).fit()
print(dict(zip(result.pvalues.index,result.pvalues)))
'''
#Regression

heart_deaths = sm.glm(formula="Heart_Disease_Deaths ~ Obesity + Binge_Drinking + Smoking + Primary_Care + No_Insurance + Median_Household_Income + College_Degrees + Long_Term_Care_Hospital_Admissions + Unemployed_Persons + Liquor_Stores", data=df).fit()
cancer_deaths = sm.glm(formula="Cancer_Deaths ~ Obesity + Binge_Drinking + Smoking + Primary_Care + No_Insurance + Median_Household_Income + College_Degrees + Long_Term_Care_Hospital_Admissions + Unemployed_Persons + Liquor_Stores", data=df).fit()
diabetes_deaths = sm.glm(formula="Diabetes_Deaths ~ Obesity + Smoking + Binge_Drinking + Primary_Care + No_Insurance + Median_Household_Income + College_Degrees + Long_Term_Care_Hospital_Admissions + Unemployed_Persons + Liquor_Stores", data=df).fit()
resp_deaths = sm.glm(formula="Respiratory_Disease_Deaths ~ Obesity + Smoking + Binge_Drinking + Primary_Care + No_Insurance + Median_Household_Income + College_Degrees + Long_Term_Care_Hospital_Admissions + Unemployed_Persons + Liquor_Stores", data=df).fit()

models = []
models.append(heart_deaths)
models.append(cancer_deaths)
models.append(diabetes_deaths)
models.append(resp_deaths)

#models.append(heart_deaths).append(cancer_deaths).append(diabetes_deaths).append(hiv_deaths)

factor_list = []
for model in models:
    p_dict = dict(zip(model.pvalues.index,model.pvalues))
    params_dict = dict(zip(model.params.index,model.params))
    filtered_dict = {k:abs(v) for (k,v) in params_dict.items() if p_dict.get(k) < 0.1 and k is not 'Intercept'}
    sorted_list = sorted(filtered_dict.items(), key=operator.itemgetter(1),reverse = True)
    if len(sorted_list) >2:
        sorted_list = sorted_list[0:2] 
    factor_list.append(sorted_list)
    

print(factor_list)



us_counties=us_counties.data.copy()
fips_list = [ (a*1000+b)for (a,b) in us_counties.keys() if a is 51]



va_xs=[us_counties[x]["lons"] for x in us_counties if us_counties[x]["state"]=='va']
va_ys=[us_counties[y]["lats"] for y in us_counties if us_counties[y]["state"]=='va']


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

col_dic =  {0:"Cancer_Deaths", 1:"Heart_Disease_Deaths", 2:"Respiratory_Disease_Deaths", 3:"Diabetes_Deaths"}

def update(a):    

    global county_colors
    document.clear()
    hover=HoverTool(tooltips=[("County Name","@i")])
    p = figure(title="US Health Indicator-Virginia", toolbar_location="left",
           plot_width=1100, plot_height=700,tools=[hover])

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
         
    data_counties_map=data_counties.reset_index()
    data_counties_map['color']=pd.Series(county_colors)
    data_counties_map.sort(col_dic.get(a),inplace=True)
    ind_top3=list(data_counties_map.index[0:3])
    data_counties_map.sort(col_dic.get(a),inplace=True,ascending=False)
    ind_bot3=list(data_counties_map.index[0:3])    
    
    p.patches(xs='x',ys='y', fill_color='c',source=source,alpha=0.5)

    for i in ind_top3:
        p.patch(x=va_xs[i],y=va_ys[i],fill_color=data_counties_map.ix[i,'color'],line_color="black",line_width=2)
    
    for i in ind_bot3:
        p.patch(x=va_xs[i],y=va_ys[i],fill_color=data_counties_map.ix[i,'color'],line_color="blue",line_width=2)

   # bar=Bar(inf_source.data,title="Top Influencers",legend=True)
    layout=VBox(children=[radio,p])
    #layout1=HBox(children=[layout,bar])
    document.add(layout)
    session.store_document(document)
        
    
source=ColumnDataSource(data=dict(x=[],y=[],c=[],i=[]))
inf_source=ColumnDataSource(data=dict(facs=[]))

radio=RadioButtonGroup(labels=['Cancer Deaths','Heart Disease Deaths', 'Respiratory Disease Deaths', 'Diabetes Deaths'],active=0)
radio.on_click(update)

update(0)


if __name__=='__main__':
    link = session.object_link(document.context)
    print("Please visit %s to see the plots" % link)
    view(link)
    session.poll_document(document)
    

