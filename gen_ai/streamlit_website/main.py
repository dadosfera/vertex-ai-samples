import streamlit as st
from streamlit_option_menu import option_menu
from utils.model_selection import ModelSelection
from streamlit_extras.colored_header import colored_header
import home, fin_rag_diy, fin_rag_oob, news_elpais_qa, news_conv_elpais_qa,  news_chatbot, med_contex_search, movies_qa, analytics_bq, ent_caregiver_bio, culture_react, crewai_qa, reading_35_pages, ask_your_doc, ask_your_image

#st.title("# Main")
st.set_page_config(page_title="main", page_icon=":tada:")
colored_header(
    label="Google Generative AI 👋",
    description="Natural Language Demos Prototype",
    color_name="violet-70",
)

md = ModelSelection()

class MultiApp:
    def __init__(self):
        self.apps = []

    def add_app(self, title, func):
        self.apps.append({
            "title": title,
            "function": func
        })

    def run():

        with st.sidebar:
            app = option_menu(
                menu_title="Generative AI",
                options=[
                    "Home",
                    "Document Q&A DIY", 
                    "Document Q&A OOB", 
                    "Multiturn News Feed", 
                    "Q&A (El Pais)", 
                    "Multiturn (El Pais)",
                    "Video Search",
                    "Movies Q&A",
                    "Analytics BQ Q&A",
                    "Caregiver Bio Gen",
                    "LLM ReAct Q&A", 
                    "CrewAI Q&A",
                    "Reading 35 Pages Q&A",
                    "Ask your Document",
                    "Ask your Photo"
                    ],
                icons=[
                    "house",
                    "bounding-box",
                    "boxes",
                    "wechat",
                    "question-lg",
                    "wechat",
                    "camera-video",
                    "camera-reels",
                    "database",
                    "person-badge",
                    "bezier2",
                    "collection",
                    "book",
                    "file-earmark-pdf",
                    "file-image"
                    ],
                menu_icon="building-fill",
                default_index=0,
                styles={
                        "container": {"padding": "2!important","background-color":'black'},
                        "icon": {"color": "white", "font-size": "23px"}, 
                        "nav-link": {"color":"white","font-size": "20px", "text-align": "left", "margin":"0px", "--hover-color": "blue"},
                        "nav-link-selected": {"background-color": "#02ab21"},}
            )
            
        print(app)
   
        if app == "Home":
            home.app()
        if app == "Document Q&A DIY":
            model, parameters = md.get_parameters_text()
            fin_rag_diy.app(model, parameters)
        if app == "Document Q&A OOB":
            model, parameters = md.get_parameters_text()
            fin_rag_oob.app(model, parameters)
        if app == "Multiturn News Feed":
            model, parameters = md.get_parameters_chat()
            news_chatbot.app(model, parameters)
        if app == "Q&A (El Pais)":
            model, parameters = md.get_parameters_text()
            news_elpais_qa.app(model, parameters)
        if app == "Multiturn (El Pais)":
            model, parameters = md.get_parameters_text()
            news_conv_elpais_qa.app(model, parameters)
        if app == "Video Search":
            med_contex_search.app()
        if app == "Movies Q&A":
            model, parameters = md.get_parameters_text()
            movies_qa.app(model, parameters)
        if app == "Analytics BQ Q&A":
            model_code, parameters_code = md.get_parameters_all_models()
            model_text, parameters_text = md.get_parameters_text()
            analytics_bq.app(model_text, parameters_text, model_code, parameters_code)
        if app == "Caregiver Bio Gen":
            ent_caregiver_bio.app()
        if app == "LLM ReAct Q&A":
            with st.sidebar:
                st.info("Model for Summarization Function:")
            model, parameters = md.get_parameters_text()
            culture_react.app(model, parameters)
        if app == "CrewAI Q&A":
            model, parameters = md.get_parameters_text()
            crewai_qa.app(model, parameters)
        if app == "Reading 35 Pages Q&A":
            model, parameters = md.get_parameters_32k_models()
            reading_35_pages.app(model, parameters)
        if app == "Ask your Document":
            model, parameters = md.get_parameters_text()
            ask_your_doc.app(model, parameters)    
        if app == "Ask your Photo":
            model, parameters = md.get_parameters_images() 
            ask_your_image.app(model, parameters)
    run()