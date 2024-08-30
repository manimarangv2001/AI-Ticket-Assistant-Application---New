import os
from langchain.docstore.document import Document
from langchain_openai import AzureOpenAIEmbeddings, AzureChatOpenAI 
from langchain_chroma import Chroma
from azure_openai.prompts import descriptionMaker
from servicenow.servicenow_api_activity import get_catalog_item_collection, get_catalog_item, get_table_values
from azure_openai.configure_openai import model, embedding_function

def set_reference_value(variable):
    if(variable['type'] == 8 and variable['dynamic_value_field'] == ''):
        reference = variable['reference']
        table_content = get_table_values(reference=reference)
        # print(table_content)
        names_in_table = []
        for content in table_content['result']:
            if('u_name' in content):
                names_in_table.append(content['u_name'])
            elif('name' in content):
                names_in_table.append(content['name'])
        variable['Choices'] = list(set(names_in_table))
        print(variable)
        return variable
    else:
        return variable
    

def get_all_variables_List(catalog_item_variable):
    def extract_variables(variables):
        variable_List = []
        for variable_info in variables:
            if variable_info['type'] == 24:
                continue
            if 'children' in variable_info:
                variable_List.extend(extract_variables(variable_info['children']))
            else:
                variable_List.append(variable_info)
        return variable_List
    
    return extract_variables(catalog_item_variable)




def arrange_response(catalog_item_json):
    print(catalog_item_json)
    variables = catalog_item_json['result']['variables']
    new_variables = get_all_variables_List(variables)
    final_result = []
    for variable in new_variables:
        if variable['type'] == 11:
            continue
        else:
            final_result.append(set_reference_value(variable))
    catalog_item_json['result']['variables'] = final_result
    return catalog_item_json


def createDocuments():
    docs=[]
    catalog_item_collection = get_catalog_item_collection()
    for catalog_item in catalog_item_collection['result']:
        if(catalog_item['sys_class_name'] != 'sc_cat_item'):
            continue
        # print(catalog_item)
        metadata = {"sys_id":catalog_item['sys_id'], "sys_name":catalog_item['sys_name'], "short_description":catalog_item["short_description"]}
        catalog_item_json = arrange_response(get_catalog_item(catalog_item['sys_id']))
        description = descriptionMaker(catalog_item_json)
        docs.append(Document(page_content=description.content, metadata=metadata))
        print(description.content)
    return docs



def initialize_cat_item_docs():
    CATALOGITEMDOCS = "Document_Store\\catalog_item_db"
    dir_path = os.path.join(os.getcwd(), CATALOGITEMDOCS)
    isdir = os.path.isdir(dir_path)
    if(not isdir):
        Chroma.from_documents(documents=createDocuments(), embedding=embedding_function, persist_directory=dir_path)
    else:
        print("catalog_item_db already Exist")
