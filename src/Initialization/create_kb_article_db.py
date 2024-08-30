import requests
import os
from langchain.docstore.document import Document
from langchain_openai import AzureOpenAIEmbeddings, AzureChatOpenAI 
from langchain_core.prompts import PromptTemplate
from langchain_chroma import Chroma
from langchain_core.output_parsers import StrOutputParser
from bs4 import BeautifulSoup
from servicenow.servicenow_api_activity import get_kb_articles
from azure_openai.configure_openai import model, embedding_function


def convert_html_to_text(html):
    soup = BeautifulSoup(html, 'html.parser')
    for br in soup.find_all("br"):
        br.replace_with("\n")
    text = soup.get_text(separator="\n")
    text = "\n".join([line.strip() for line in text.splitlines() if line.strip()])
    return text


def createDocuments():
    docs=[]
    articles = get_kb_articles()
    for kb_article in articles['result']:
        metadata = {"sys_id":kb_article['sys_id'], "short_description":kb_article['short_description'], "Number":kb_article["number"]}
        content = convert_html_to_text(kb_article['text'])
        docs.append(Document(page_content=content, metadata=metadata))
    return docs


def initialize_kb_art_docs():
    KBARTICLESDOCS = "Document_Store\\kb_articles_db"
    dir_path = os.path.join(os.getcwd(), KBARTICLESDOCS)
    isdir = os.path.isdir(dir_path)
    if(not isdir):
        Chroma.from_documents(documents=createDocuments(), embedding=embedding_function, persist_directory=dir_path)

