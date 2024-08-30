import os
from langchain_core.messages import HumanMessage
from langchain_openai import AzureOpenAIEmbeddings, AzureChatOpenAI 
from servicenow import configure_servicenow
from langchain_core.prompts import PromptTemplate


from dotenv import load_dotenv
load_dotenv()

embedding_function = AzureOpenAIEmbeddings(model="Text-embedding")

model = AzureChatOpenAI(
    openai_api_version=os.environ["AZURE_OPENAI_API_VERSION"],
    azure_deployment=os.environ["AZURE_OPENAI_CHAT_DEPLOYMENT_NAME"],
)