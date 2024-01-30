#%%
#region Libraries
import re
import ast
import pandas as pd
from typing import List
from google.cloud import aiplatform
from google.cloud import discoveryengine, bigquery
from google.protobuf.json_format import MessageToDict
from vertexai.preview.generative_models import GenerativeModel
from vertexai.language_models import TextGenerationModel, ChatModel, CodeGenerationModel
#endregion

class Client:
    def __init__(self,iterable=(), **kwargs) -> None:
        self.__dict__.update(iterable, **kwargs)
        
        aiplatform.init(project=self.project, location=self.region)

    #region EnterpriseSearch
    def search(self, prompt, news=False) -> List[discoveryengine.SearchResponse.SearchResult]:
        # Create a client
        client = discoveryengine.SearchServiceClient()
        if news:
            serving_config = client.serving_config_path(
                project=self.project,
                location=self.location,
                data_store="news_1687453492092",
                serving_config="default_config",
            )
        else:
            serving_config = client.serving_config_path(
                project=self.project,
                location=self.location,
                data_store=self.datastore,
                serving_config="default_config",
            )
        request = discoveryengine.SearchRequest(
            serving_config=serving_config, query=prompt, page_size=5)

        response = client.search(request)
        
        if news:
            
            snippets=[]
            links=[]
            for result in response.results:
                data=MessageToDict(result.document._pb)["derivedStructData"]
                links.append(data["link"])
                for i in data["snippets"]:
                    snippets.append(i["snippet"])
                
            df=pd.DataFrame({"link": links, "snippets": snippets})
        
        else:
            col=list(set([key for res in response.results for key in MessageToDict(res.document._pb)["structData"].keys()]))
            _res=[MessageToDict(_.document._pb)["structData"] for _ in response.results]
            for c in col:
                for num,res in enumerate(_res):
                    if c not in res.keys():
                        _res[num][c]="None"

            df=pd.DataFrame(_res)

        return df
    #endregion
    
    #region Text LLM
    def text_bison(self, prompt, parameters="", model="text-bison@002", entities=True):
        if parameters == "":
            parameters = {
                "max_output_tokens": 1024,
                "temperature": 0.2,
                "top_p": 0.8,
                "top_k": 40
                }
        model = TextGenerationModel.from_pretrained(model)
        response = model.predict(prompt,
            **parameters
        )
        if entities:
            response = ast.literal_eval(re.findall(r"\[.*\]",response.text.strip())[0])
        else: response = response.text.replace("$", "\$")
        return response
    #endregion
    
    #region Text LLM
    def llm(self, prompt, context, model, parameters):
        
        prompt = f""" You are an anlyticts chatbot, respond the following question with the details provided in the context:
        - be creative
        
        context:
        {context}
        
        question:
        {prompt}
        
        """
        
        if "text" in model:
            _model = TextGenerationModel.from_pretrained(model)
            response = _model.predict(prompt,**parameters)
        elif model == "code-bison@002":
            model = "text-bison@002"
            _model = TextGenerationModel.from_pretrained(model)
            response = _model.predict(prompt,**parameters)
        elif model == "code-bison-32k@002":
            model = "text-bison-32k@002"
            _model = TextGenerationModel.from_pretrained(model)
            response = _model.predict(prompt,**parameters)
        else:
            _model = GenerativeModel(model)
            response = _model.generate_content([prompt],generation_config=parameters)  

        return response.text, model
    #endregion
    
    #region Chat LLM
    def chat_bison(self, prompt, news_context="", context="", parameters="", model="chat-bison@001"):
        if parameters == "":
            parameters = {
                "max_output_tokens": 1024,
                "temperature": 0.5,
                "top_p": 0.8,
                "top_k": 40
                }
        chat_model = ChatModel.from_pretrained(model)
                
        c_context=f'''You are a very friendly and funny chat, use the following session data as historic information for your conversations: {context},
            use the following news enclosed by backticks as your only source of truth, do not make up or use old data: ```{news_context}```,
            from time to times ask friendly questions to gather more information and do not repeat questions,
            When someone ask for demos give the following links: for Image QnA video: https://genai.sonrobots.net/Image_QnA_[vision], for Movies QnA using Enterprise Search: https://genai.sonrobots.net/Movies_QnA_,
        '''
        chat = chat_model.start_chat(context=c_context)
        response = chat.send_message(prompt, **parameters)
        
        return response.text
    #endregion
    
    #region Code LLM    
    def code_bison(self, prompt, model, parameters, top_k=1000000):
        schema_columns=[i.column_name for i in bigquery.Client(project=self.project).query(f"SELECT column_name FROM `{self.project}`.{self.dataset}.INFORMATION_SCHEMA.COLUMNS WHERE table_name='{self.table}'").result()]

        prompt = f"""You are a GoogleSQL expert. Given an input question, first create a syntactically correct GoogleSQL query to run. This will be the SQLQuery. Then look at the results of the query. This will be SQLResults. Finally return the answer to the input question.
        - Unless the user specifies in the question a specific number of examples to obtain, query for at most {top_k} results using the LIMIT clause as per GoogleSQL. You can order the results to return the most informative data in the database.
        - When running SQLQuery across BigQuery you must only include BigQuery SQL code from SQLQuery.
        - Never query for all columns from a table. You must query only the columns that are needed to answer the question. Wrap each column name in backticks (`) to denote them as delimited identifiers.
        - Pay attention to use only the column names you can see in the tables below. Be careful to not query for columns that do not exist. Also, pay attention to which column is in which table.
        - Do not generate fake responses, only respond with SQL query code.
        
        Match the <prompt> below to this column name schema: {schema_columns}
        
        Use the following project {self.project}, dataset {self.dataset} and {self.table} to create the query
        
        Question: {prompt}
        
        
        Output: 'SQL Query (only) to Run':
        """
        
        if "text" in model:
            model = TextGenerationModel.from_pretrained(model)
            response = model.predict(prompt, **parameters)
        elif "code" in model:
            model = CodeGenerationModel.from_pretrained(model)
            response = model.predict(prefix=prompt, **parameters)
        else:
            model = GenerativeModel("gemini-pro")
            response = model.generate_content([prompt],generation_config=parameters)        
        
        res=re.sub('```', "", response.text.replace("SQLQuery:", "").replace("sql", ""))
    
        return res
    #endregion
    
    #region Vertex Search
    def vertex_search(self, prompt):
        
        self.vsearch_client = discoveryengine.SearchServiceClient()
        self.vsearch_serving_config = self.vsearch_client.serving_config_path(
            project=self.project,
            location=self.location,
            data_store=self.data_store,
            serving_config="default_search",)
        
        request = discoveryengine.SearchRequest(
            serving_config=self.vsearch_serving_config, query=prompt, page_size=100)
    
        content_search_spec = discoveryengine.SearchRequest.ContentSearchSpec(snippet_spec=discoveryengine.SearchRequest.ContentSearchSpec.SnippetSpec(
                return_snippet=True),
        summary_spec = discoveryengine.SearchRequest.ContentSearchSpec.SummarySpec(
                summary_result_count=2, include_citations=True),
        extractive_content_spec=discoveryengine.SearchRequest.ContentSearchSpec.ExtractiveContentSpec(
                max_extractive_answer_count=2,
                max_extractive_segment_count=2))
    
        request = discoveryengine.SearchRequest(
            serving_config=self.vsearch_serving_config, query=prompt, page_size=2, content_search_spec=content_search_spec)                                                         

        response = self.vsearch_client.search(request)

        documents = [MessageToDict(i.document._pb) for i in response.results]

        context = []
        num = 0
        ctx = {}

        for i in documents:
            for ans in i["derivedStructData"]["extractive_segments"]:
                num += 1
                link = "https://storage.googleapis.com"+"/".join(i["derivedStructData"]["link"].split("/")[1:])
                context = ans["content"]
                page = ans["pageNumber"]
                ctx[f"context: {num}"]="text: {}, source: {}, page: {}".format(context, link, page)

        return ctx
    #endregion

# %%
