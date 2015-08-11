'''
Created on Aug 11, 2015

@author: akshat
'''
import pandas as pd
import numpy as np
import statsmodels.formula.api as sm

df = pd.read_csv("test.csv")
df = pd.DataFrame({'Value' : df.groupby( [ "County", "Indicator Type"] )['Value'].mean()}).reset_index()
df = df.pivot_table("Value",["County"],"Indicator Type").reset_index()

#result = sm.ols(formula="Heart_Deaths ~ Obesity", data=df).fit()
#print(dict(zip(result.pvalues.index,result.pvalues)))

#Regression

heart_deaths = sm.ols(formula="Heart_Disease_Deaths ~ Obesity + Smoking + Primary_Care + No_Insurance + Median_Household_Income + College_Degrees + Long_Term_Care_Hospital_Admissions + Unemployed_Persons + Healthy_Food_Outlets + Liquor_Stores", data=df).fit()
print(dict(zip(heart_deaths.pvalues.index,heart_deaths.pvalues)))

cancer_deaths = sm.ols(formula="Cancer_Deaths ~ Obesity + Smoking + Primary_Care + No_Insurance + Median_Household_Income + College_Degrees + Long_Term_Care_Hospital_Admissions + Unemployed_Persons + Healthy_Food_Outlets + Liquor_Stores", data=df).fit()
print(dict(zip(cancer_deaths.pvalues.index,cancer_deaths.pvalues)))

diabetes_deaths = sm.ols(formula="Diabetes_Deaths ~ Obesity + Smoking + Primary_Care + No_Insurance + Median_Household_Income + College_Degrees + Long_Term_Care_Hospital_Admissions + Unemployed_Persons + Healthy_Food_Outlets + Liquor_Stores", data=df).fit()
print(dict(zip(diabetes_deaths.pvalues.index,cancer_deaths.pvalues)))

hiv_deaths = sm.ols(formula="HIV_deaths ~ Obesity + Smoking + Primary_Care + No_Insurance + Median_Household_Income + College_Degrees + Long_Term_Care_Hospital_Admissions + Unemployed_Persons + Healthy_Food_Outlets + Liquor_Stores", data=df).fit()
print(dict(zip(diabetes_deaths.pvalues.index,cancer_deaths.pvalues)))
