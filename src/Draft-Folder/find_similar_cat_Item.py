import requests
import os
from langchain.docstore.document import Document
from langchain_openai import AzureOpenAIEmbeddings, AzureChatOpenAI 
from langchain_core.prompts import PromptTemplate
from langchain_chroma import Chroma


embedding_function = AzureOpenAIEmbeddings(model="Text-embedding")

model = AzureChatOpenAI(
    openai_api_version=os.environ["AZURE_OPENAI_API_VERSION"],
    azure_deployment=os.environ["AZURE_OPENAI_CHAT_DEPLOYMENT_NAME"],
)

user = 'admin'
pwd = 'wr^zd%PWRC12'

headers = {"Content-Type":"application/json","Accept":"application/json"}

def get_catalog_item_collection():
    url = 'https://dev199703.service-now.com/api/now/table/sc_cat_item?sysparm_query=sc_catalogsLIKEe0d08b13c3330100c8b837659bba8fb4%5Eactive%3Dtrue'
    response = requests.get(url, auth=(user, pwd), headers=headers )
    if response.status_code != 200: 
        data = {'result':{'sys_id': "", 'sys_name': "",'short_description':"",'description':""}, 'Status': response.status_code, 'Headers': response.headers, 'Error Response':response.json()}
    data = response.json()
    return data


def get_catalog_item(sys_id):
    url = f'https://dev199703.service-now.com/api/sn_sc/servicecatalog/items/{sys_id}'
    response = requests.get(url, auth=(user, pwd), headers=headers )
    if response.status_code != 200: 
        print('Status:', response.status_code, 'Headers:', response.headers, 'Error Response:',response.json())
    data = response.json()
    return data


def get_table_values(reference):
    url = f'https://dev199703.service-now.com/api/now/table/{reference}'
    response = requests.get(url, auth=(user, pwd), headers=headers )
    if response.status_code != 200: 
        print('Status:', response.status_code, 'Headers:', response.headers, 'Error Response:',response.json())
        exit()
    data = response.json()
    return data


def descriptionMaker(data):

    template = """{data}
    
    using this data provide a proper description for this catalog item.
    In the Json data, variables has choices mention all of it in description (Mandatory)
    
    Example:

    Catalog Item Name: Software Services

    Description:
    The Software Services catalog item allows users to request various software-related services. This includes the following actions:

    Software Installation: Users can request the installation of software such as Adobe Acrobat DC Pro or Python.
    Software Uninstallation: Users can request the removal of existing software.
    OS Update: Users can request updates to their operating systems.
    This item is available on the desktop and is designed to streamline the process of managing software needs efficiently.

    Variables (Fields):
    Requested for: The user for whom the request is made (mandatory).
    Contact Number: The contact number of the requester.
    Location: The location of the requester.
    Project Name: The department or project name associated with the request.
    Business Service: The specific service being requested (Software Installation, Software Uninstallation, OS Upgrade).
    Software Name: The specified software being requested (Adobe Acrobat DC Pro, Python).
    Add Software: Option to add software.
    Request Type: The type of request, e.g., Software Installation - Freeware.
    Duration: The expected duration for the service.
    Correct Host Name: Selection of the correct host name where the service will be applied.
    UI Policy Description
    UI Policies define the visibility and behavior of certain fields based on the selected Business Service.

    UI Policy for Software Installation:

    Condition:
    This policy is triggered if the Business Service field is set to "Software Installation".
    Actions:
    When this condition is met, several fields related to the software installation process are made visible to the user.
    Fields affected by this policy include the Software Name, Request Type, Duration, and Add Software options.
    UI Policy for Software Uninstallation:

    Condition:
    This policy is triggered if the Business Service field is set to "Software Uninstallation".
    Actions:
    When this condition is met, fields related to the software uninstallation process are made visible.
    Specifically, the Software Name field will be visible, allowing users to select which software they wish to uninstall.
    These UI policies ensure that users only see and interact with fields relevant to the specific service they are requesting, enhancing the user experience by simplifying the form and reducing unnecessary complexity.

    
    """
    
    prompt_template = PromptTemplate(template=template, input_variables=["data"])
    chain = prompt_template | model
    response = chain.invoke({"data": data})
    return response


catalog_item_collection = get_catalog_item_collection()

def set_reference_value(variable):
    if(variable['type'] == 8 and variable['dynamic_value_field'] == ''):
        reference = variable['reference']
        table_content = get_table_values(reference=reference)
        # print(table_content)
        names_in_table = []
        for content in table_content['result']:
            if('u_name' in content):
                names_in_table.append(content['u_name'])
        variable['value'] = names_in_table
        #print(variable)
        return variable
    else:
        return variable

def arrange_response(catalog_item_json):
    variables = catalog_item_json['result']['variables']
    new_variables = []
    for variable in variables:
        if 'children' in variable:
            children_List = []
            for children in variable['children']:
                children_List.append(set_reference_value(children))
            variable['children'] = children_List
            new_variables.append(variable)
        else:
            new_variables.append(set_reference_value(variable))

    catalog_item_json['result']['variables'] = new_variables
    return catalog_item_json



elemenate_items = [
    'Password Reset',
    'Service Fulfillment Steps - Custom approval step',
    'Record Producer Builder',
    'Report Performance Problem',
    'Report Outage',
    'Service Fulfillment Steps - Base step',
    'Service Fulfillment Steps - Task step',
    'Catalog Variable Creation',
    'Catalog UI Policy',
    'Catalog Item Builder',
    'Replace printer toner',
    'Password Reset Enrollment'
    ]

def createDocuments():
    docs=[]
    for catalog_item in catalog_item_collection['result']:
        if(catalog_item['sys_name'] in elemenate_items):
            continue
        print(catalog_item)
        metadata = {"sys_id":catalog_item['sys_id'], "sys_name":catalog_item['sys_name']}
        catalog_item_json = arrange_response(get_catalog_item(catalog_item['sys_id']))
        description = descriptionMaker(catalog_item_json)
        docs.append(Document(page_content=description.content, metadata=metadata))
        print(description.content)
    return docs

query = "I need to install python"

path = './chroma_db'
isdir = os.path.isdir(path)
if(not isdir):
    db2 = Chroma.from_documents(documents=createDocuments(), embedding=embedding_function, persist_directory=path)

docs = db2.similarity_search(query)
print(docs[0].page_content)

# load from disk
db3 = Chroma(persist_directory="./chroma_db", embedding_function=embedding_function)
docs = db3.similarity_search(query)
print(docs[0].page_content)