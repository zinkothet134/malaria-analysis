import pandas as pd 
import streamlit as st
import matplotlib.pyplot as plt
import plotly.express as px
# import seaborn as sns
import pandas as pd
import glob

st.set_page_config(page_title='malaria data analysis',page_icon=None,layout='wide')
st.title("Malaria Analysis")
col1,col2 = st.columns(2)


#glob.glob('/Users/zinkothet/Desktop/Malaria CSV/20.csv')
#all_dfs = []
#for one_filename in glob.glob('/Users/zinkothet/Desktop/Malaria CSV/20*.csv'):
 #   print(f"Loading {one_filename}")
  #  new_Df = pd.read_csv(one_filename,usecols=['date of consultation','township','chw village','mam village code','patient name','age month', 'age year', 'agegroup', 'gender','rdt','type of malaria'])
   # all_dfs.append(new_Df)


df=pd.concat([pd.read_csv(one_filename,usecols=['date of consultation','township','chw village','mam village code','patient name','age month', 'age year', 'agegroup', 'gender','rdt','type of malaria'])
              for one_filename in glob.glob('/Users/zinkothet/Desktop/Ilove/20*.csv')])
df['date of consultation']=pd.to_datetime(df['date of consultation'],format='%d/%m/%Y',errors='coerce')
df.set_index(df['date of consultation'],inplace=True)

startDate = pd.to_datetime(df['date of consultation']).min()
endDate = pd.to_datetime(df['date of consultation']).max()
with col1:
    date1=pd.to_datetime(st.date_input('Start Date',startDate))

with col2:
    date2 = pd.to_datetime(st.date_input('End Date',endDate))

df=df[(df['date of consultation']>=date1) & (df['date of consultation']<=date2)].copy()
townshipMaping={
    'Kyainseikgyi': 'Kyainseikgyi',
    'Kawkareik' : 'Kyainseikgyi',
    'Kyainseikgyi (Kyaik Don)': 'Kyainseikgyi',
    'Kyainseikgyi_Hpayathonsu': 'Kyainseikgyi',
    'Ye' : 'Kyainseikgyi'
}
df['township']=df['township'].replace(townshipMaping)

st.subheader('Township Wise RDT Testing')
dataByTownship = df.groupby('township')['patient name'].count().reset_index()
dataByTownship.columns=['township','RDT Testing']
dataByTownship=dataByTownship.sort_values('RDT Testing',ascending=False)
fig =px.bar(dataByTownship,x='township',y='RDT Testing',text=['{:,.0f}'.format(x) for x in dataByTownship['RDT Testing']],template='seaborn')
st.plotly_chart(fig,use_container_width=True)

dataByTownship = df.groupby('township')['patient name'].count().reset_index()
dataByTownship.columns=['township','RDT Testing']
st.subheader('Township Wise RDT Testing')
fig = px.pie(dataByTownship,values='RDT Testing',names='township',hole=0.5)
fig.update_traces(text=dataByTownship['township'],textposition='outside')
st.plotly_chart(fig,use_container_width=True)

st.sidebar.header('Select township')
township=df['township'].unique()
selected_townships=st.sidebar.multiselect('Township',township)

if selected_townships:
    df_filtered = df[df['township'].isin(selected_townships)]
else:
    df_filtered = df.copy()
    
st.subheader('Time Series Analysis')
# # df['date of consultation'] = df['date of consultation'].to_period("W")
# linechart = df.groupby(df['date of consultation'].dt.to_period('M'))['patient name'].count().reset_index()
# linechart.columns = ['Year_Month','# of Test']
# linechart['Year_Month'] = linechart['Year_Month'].dt.to_timestamp()
# fig2 = px.line(linechart,x='Year_Month',y='# of Test',labels={'Year_Month':'Month_Year',
#                                                               '# of Test':'#ofRDT'},height=500,width=1000,template='gridon')
# st.plotly_chart(fig2,use_container_width=True)

#################kjfalkdjlfakdjflakdjfl#################
df_filtered['date of consultation'] = pd.to_datetime(df_filtered['date of consultation'])

# Reset index to avoid conflicts
df_filtered = df_filtered.reset_index(drop=True)

positive = df_filtered[df_filtered['rdt'] == 1].groupby(df_filtered['date of consultation'].dt.to_period('M'))['rdt'].count().reset_index()
positive.columns = ['Date','Positive']

test = df_filtered.groupby(df_filtered['date of consultation'].dt.to_period('M'))['rdt'].count().reset_index()
test.columns = ['Date','RDT']

merged_df = pd.merge(test,positive,on='Date',how='outer').fillna(0)
merged_df['Date'] = merged_df['Date'].dt.to_timestamp()
fig3 = px.line(merged_df,x='Date',y=['RDT','Positive'],labels={'Date':'Date','value':'#of RDT/Positive'},template='seaborn')
st.plotly_chart(fig3,use_container_width=True)


############################
st.subheader('ICMV Workload Analysis')
positive_Day = df_filtered[df_filtered['rdt'] == 1].groupby(df_filtered['date of consultation'].dt.to_period('D'))['rdt'].count().reset_index()
positive_Day.columns = ['Date','Positive']

test_Day = df_filtered.groupby(df_filtered['date of consultation'].dt.to_period('D'))['rdt'].count().reset_index()
test_Day.columns = ['Date','RDT']

village = df_filtered.groupby(df_filtered['date of consultation'].dt.to_period('D'))['chw village'].nunique().reset_index()
village.columns = ['Date','# of village']

merged_df_ICMV=pd.merge(test_Day,positive_Day,on='Date',how='outer').fillna(0)
merged_df_ICMV = pd.merge(merged_df_ICMV,village,on='Date',how='outer').fillna(0)
merged_df_ICMV['Date']=merged_df_ICMV['Date'].dt.to_timestamp()
merged_df_ICMV['RDT/village/day']=(merged_df_ICMV['RDT'])/(merged_df_ICMV['# of village'])
fig4=px.line(merged_df_ICMV,x='Date',y='RDT/village/day',labels={'Date':'Date','RDT/village/day':'# of Test per ICMV'},template='seaborn')
st.plotly_chart(fig4,use_container_width=True)
