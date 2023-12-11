import sys
sys.path.append("utils")
import numpy as np
import sockcop_vertexai
import streamlit as st
from google.cloud import bigquery
from k import *

variables={
    "project":"vtxdemos",
    "region": "us-central1",
    "dataset": "public",
    "table": "citibike_stations"
}

source_df = bigquery.Client(project=variables["project"]).query(f"SELECT * FROM `{variables['dataset']}.{variables['table']}` LIMIT 5").to_dataframe()
client = sockcop_vertexai.Client(variables)

st.title("Analytics Code-b and BQ")
with st.sidebar:
    st.markdown(
        """
        Follow me on:

        ldap → [@jesusarguelles](https://moma.corp.google.com/person/jesusarguelles)

        GitHub → [jchavezar](https://github.com/jchavezar)
        
        LinkedIn → [Jesus Chavez](https://www.linkedin.com/in/jchavezar)
        
        Medium -> [jchavezar](https://medium.com/@jchavezar)
        """
    )
    
st.write("Citibike Stations Datastore: ")
st.dataframe(source_df)
res, df = client.code_bison(st.text_input("Enter some text 👇", value="Show me the max capacity by grouping per latitude and longitude"))

st.write("**Query From code-bison@002:**")
st.write(res)

st.write("**Response Table:**")
st.dataframe(df)

st.write(df.dtypes)

object_columns = df.select_dtypes(include='object').columns.to_list()
num_columns = df.select_dtypes(include='int64').columns.to_list()
num_lat_long = df.select_dtypes(include='float64').columns.to_list()
if len(object_columns) != 0 and len(num_columns) != 0:
    st.write("**Bar Chart**")
    st.bar_chart(df, x=object_columns[0], y=num_columns[0])

if len(num_lat_long) != 0:
    df["color"]=np.random.rand(df.shape[0], 4).tolist()
    st.write("**Data Map**")
    st.map(df, latitude="latitude", longitude="longitude", size=num_columns[0], color="color")
    
button = f'''<script src="https://www.gstatic.com/dialogflow-console/fast/df-messenger/prod/v1/df-messenger.js"></script>
<df-messenger
  agent-id="{dialogflow_id}"
  language-code="en">
  <df-messenger-chat-bubble
   chat-title="infobot"
   bot-writing-text="..."
   placeholder-text="Tell me something!">
  </df-messenger-chat-bubble>
</df-messenger>
<style>
  df-messenger {{
    z-index: 999;
    position: fixed;
    bottom: 16px;
    right: 16px;
  }}
</style>'''

st.components.v1.html(button, height=700, width=350)

st.markdown(
    """
    <style>
        iframe[width="350"] {
            position: fixed;
            bottom: 60px;
            right: 40px;
    </style>
    """,
    unsafe_allow_html=True,
)