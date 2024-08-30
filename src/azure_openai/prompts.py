import os
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser
from langchain_chroma import Chroma

from .configure_openai import model, embedding_function

def descriptionMaker(data):

    template = """{data}
    
    using this data provide a proper description for this catalog item.
    also it should contain variable(parent and child) and variable description.
    In the Json data, If variables have reference_values, mention all of it in variable description.
    In the Json data, If variables have choices, mention all of it in variable description.
    The variables description should mention the ui policy condtions and actions if exist.
    It should not contain other then that.
    
    Format:
    Catalog Item Name: Name of the catalog item
    Description: detailed description about catalog item.
    Variables (Fields):
    Name of the variable: About the variable.
    """
    
    prompt_template = PromptTemplate(template=template, input_variables=["data"])
    chain = prompt_template | model
    response = chain.invoke({"data": data})
    return response



def fetchDescribe(data):

    template = """{data}
    
    from the given data Return only the 100 words of description of the catalog item.
    Output should not contain the variables
    And no premable or explaination.

    """
    
    prompt_template = PromptTemplate(template=template, input_variables=["data"])
    chain = prompt_template | model | StrOutputParser()
    response = chain.invoke({"data": data})
    return response


def prepare_missed_param_questions(catalog_description, fetched_variables, missed_variables):

    template = """{catalog_description}
    
    I have a catalog item with the following details:
    {fetched_variables}
    
    Some variables are missing from the request:
    {missed_variables}

    Please generate a JSON object with questions for each missing variable based on the given catalog item description and fetched data. 
    The JSON should include the following missing variables: {missed_variables}. 
    Do not include choices in the questions.

    Example:
    missedvariable1: question1 etc 

    And no premable or explaination.
            
    """
    prompt_template = PromptTemplate(template=template, input_variables=["catalog_description", "fetched_variables", "missed_variables"])
    chain = prompt_template | model | JsonOutputParser()
    response = chain.invoke({"catalog_description": catalog_description, "fetched_variables": fetched_variables, "missed_variables": missed_variables})
    return response



# def openAIFunction(name: str):

#     template = """You are an AI assistant designed to classify user queries. Your task is to determine whether a given query is a normal conversation or a ServiceDesk conversation. 
#     A normal conversation includes everyday, casual, or non-service-related topics. Examples include discussing hobbies, plans, general inquiries, and personal matters.
#     A ServiceDesk conversation involves requests for assistance, support issues, troubleshooting, or inquiries related to IT services, technical support, or customer service.
#     For each query, respond with either "Conversation" if it is a normal conversation or "ServiceDesk" if it is a ServiceDesk conversation.
#     Examples:
#     Query: "How was your weekend?"
#     Classification: Conversation
    
#     Query: "I'm having trouble logging into my email."
#     Classification: ServiceDesk
    
#     Query: "What's your favorite movie?"
#     Classification: Conversation
    
#     Query: "Can you help me reset my password?"
#     Classification: ServiceDesk
    
#     Query: {query}
#     Classification: 
#     """
#     prompt_template = PromptTemplate(template=template, input_variables=["query"])
#     chain = prompt_template | model
#     response = chain.invoke({"query": name})

#     if(response.content == 'ServiceDesk'):
#         return ServiceDesk_Function(question=name)
#     else:
#         return Conversational_Function(question=name)


# def Conversational_Function(question):
#     message = HumanMessage(
#         content=question
#     )
#     answer=model.invoke([message])
#     response = answer.content
#     return response


# def ServiceDesk_Function(question):
#     similar_catalog_items = configure_servicenow.get_similar_catalog_item(question)
    

#     # if not similar_catalog_items['result']:
#     #     print(f"similar_catalog_items: {similar_catalog_items}")
#     #     return {
#     #         "content": "There is no matching catalog available currently, Will include shortly.",
#     #         "response_detail": "service_desk_response"
#     #     }
#     return similar_catalog_items
