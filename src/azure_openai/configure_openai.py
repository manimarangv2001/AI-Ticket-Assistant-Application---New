import os
from langchain_core.messages import HumanMessage
from langchain_openai import AzureOpenAIEmbeddings, AzureChatOpenAI 
from servicenow import configure_servicenow
from langchain_core.prompts import PromptTemplate


from dotenv import load_dotenv
load_dotenv()

embedding_function = AzureOpenAIEmbeddings(
    azure_endpoint="https://2000081253-openai.openai.azure.com/",
    api_key="107c20f6b6774c80b98c6f6a828f6374",
    azure_deployment="Text-embedding",
    api_version="2023-03-15-preview"
    )

model = AzureChatOpenAI(
    api_key="107c20f6b6774c80b98c6f6a828f6374",
    azure_deployment="gpt-4",
    azure_endpoint="https://2000081253-openai.openai.azure.com/",
    api_version="2023-03-15-preview"
)