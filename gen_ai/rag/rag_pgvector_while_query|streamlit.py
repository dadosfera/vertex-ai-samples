#%%
import os
import base64
import time
import asyncio
from k import k
import pandas as pd
import streamlit as st 
from utils import google
from openai import OpenAI
from utils.credentials import *

os.environ["OPENAI_API_KEY"] = k

variables = {
    "project_id": "vtxdemos",
    "region": "us-central1",
    "instance_name": "pg15-pgvector-demo",
    "database_user": "emb-admin",
    "database_password": DATABASE_PASSWORD,
    "database_name": "rag-pgvector-langchain-1",
    "docai_processor_id": "projects/254356041555/locations/us/processors/7e6b9d94d3bafa4f",
    "location": "us"
}

client = google.Client(variables)

#region Model Settings
settings = ["text-bison", "text-bison@001", "text-bison-32k"]
model = st.sidebar.selectbox("Choose a text model", settings)

temperature = st.sidebar.select_slider("Temperature", [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1], value=0.2) 
if model == "text-bison" or model == "text-bison@001":
        token_limit = st.sidebar.select_slider("Token Limit", range(1, 1025), value=256)
else:token_limit = st.sidebar.select_slider("Token Limit", range(1,8193), value=1024)
top_k = st.sidebar.select_slider("Top-K", range(1, 41), value=40)
top_p = st.sidebar.select_slider("Top-P", [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1], value=0.8) 
    
parameters =  {
    "temperature": temperature,
    "max_output_tokens": token_limit,
    "top_p": top_p,
    "top_k": top_k
    }

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
#endregion

async def db_functions(documents, query):
    await client.create_table()
    await client.insert_documents_vdb(documents)    
    return await client.query(query)

# %%
# LLM prompt + context

@st.cache_data
def prepare(file):
    documents, ocr_time, embeddings_time = client.prepare_file(file)
    #st.write(f"Embeddings time: {round(embeddings_time, 2)} sec")
    start = time.time()
    asyncio.run(client.create_table())
    asyncio.run(client.insert_documents_vdb(documents))
    st.write(f"OCR Time: **{round(ocr_time, 2)} sec**, Embeddings time: **{round(embeddings_time, 2)} sec**, Vector DB Inserting Time: **{round(time.time()-start, 2)} sec**")

    #st.write(f"Vector DB Inserting Time: {round(time.time()-start, 2)} sec")
    return documents

def display_document(file):
    base64_pdf = base64.b64encode(file.read()).decode("utf-8")
    pdf_display = F'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="1000" type="application/pdf"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)

def open_ai_chatpgt(prompt, context):
    client = OpenAI(
        # defaults to os.environ.get("OPENAI_API_KEY")
        api_key=k,
    )

    completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": f"""

                Prompt: {prompt}

                Context: {context}

                """,
            }
        ],
        model="gpt-4",
    )
    return completion.choices[0].message.content


def query(query):
    start = time.time()
    matches = asyncio.run(client.query(query))
    st.markdown(f"Vector DB Query Time: **{round(time.time() - start, 2)} sec**")
    df = pd.DataFrame(matches)
    google_response = client.llm_predict(query, context=pd.DataFrame(matches).to_json(), parameters=parameters)
    open_ai_response = open_ai_chatpgt(query, context=pd.DataFrame(matches).to_json())
    return str(google_response), str(open_ai_response), df

#%%
st.title("Tax Bot")

import streamlit as st 

def main(): 
    #st.title("Chat with Your PDF") 
    pdf = st.file_uploader("Upload your PDF", type="pdf")
    if pdf:
        display_document(pdf)
        documents = prepare(pdf)
        text = st.text_input("Prompt")
    
        if text:
            google_response, open_ai_response, df = query(text)
            st.markdown("***Google:***")
            st.write(google_response)
            st.markdown("***OpenAI:***")
            st.write(open_ai_response)
            st.write(documents)
            st.write(df)    

if __name__ == '__main__': main() 
