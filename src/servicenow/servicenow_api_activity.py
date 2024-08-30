import requests
import os

from dotenv import load_dotenv
load_dotenv()

base_url = os.environ["SERVICENOW_BASEURL"]
user = os.environ["SERVICENOW_USERNAME"]
pwd = os.environ["SERVICENOW_PASSWORD"]
headers = {"Content-Type":"application/json","Accept":"application/json"}


def get_specific_catalog_item(sys_id):

    url = f"{base_url}/sn_sc/servicecatalog/items/{sys_id}"
    response = requests.get(url, auth=(user, pwd), headers=headers )
    if response.status_code != 200: 
        print("Status:", response.status_code, "Headers:", response.headers, "Error Response:",response.json())
        exit()
    data = response.json()
    return data

def get_table_response(reference):
    url = f"{base_url}/now/table/{reference}?sysparm_limit=1"
    response = requests.get(url, auth=(user, pwd), headers=headers )
    if response.status_code != 200: 
        print("Status:", response.status_code, "Headers:", response.headers, "Error Response:",response.json())
        exit()
    data = response.json()
    return data


def get_table_sysid(reference, table_field, value_for_query):
    if("@" in value_for_query):
        value_for_query = value_for_query.replace("@","%40")
    sysparm_query = f"{table_field}%3D{value_for_query}" 

    url = f"{base_url}/now/table/{reference}?sysparm_query={sysparm_query}&sysparm_limit=1"
    # print(url)
    response = requests.get(url, auth=(user, pwd), headers=headers )
    if response.status_code != 200: 
        print("Status:", response.status_code, "Headers:", response.headers, "Error Response:",response.json())
        exit()

    data = response.json()
    return data


def get_catalog_item_variables(sys_id):
    url = f"{base_url}/sn_sc/servicecatalog/items/{sys_id}/variables"
    response = requests.get(url, auth=(user, pwd), headers=headers )
    if response.status_code != 200: 
        print("Status:", response.status_code, "Headers:", response.headers, "Error Response:",response.json())
    print(response)
    data = response.json()
    return data

def get_table_values(reference):
    url = f"{base_url}/now/table/{reference}"
    response = requests.get(url, auth=(user, pwd), headers=headers )
    if response.status_code != 200: 
        print("Status:", response.status_code, "Headers:", response.headers, "Error Response:",response.json())
        exit()
    data = response.json()
    return data

def get_catalog_item_collection():
    url = f'{base_url}/now/table/sc_cat_item?sysparm_query=sc_catalogsLIKEe0d08b13c3330100c8b837659bba8fb4%5Eactive%3Dtrue'
    response = requests.get(url, auth=(user, pwd), headers=headers )
    if response.status_code != 200: 
        data = {'result':{'sys_id': "", 'sys_name': "",'short_description':"",'description':""}, 'Status': response.status_code, 'Headers': response.headers, 'Error Response':response.json()}
    data = response.json()
    return data


def get_catalog_item(sys_id):
    url = f'{base_url}/sn_sc/servicecatalog/items/{sys_id}'
    response = requests.get(url, auth=(user, pwd), headers=headers )
    if response.status_code != 200: 
        print('Status:', response.status_code, 'Headers:', response.headers, 'Error Response:',response.json())
    data = response.json()
    return data

def get_kb_articles():
    url = f'{base_url}/now/table/kb_knowledge'
    response = requests.get(url, auth=(user, pwd), headers=headers )
    if response.status_code != 200: 
        print('Status:', response.status_code, 'Headers:', response.headers, 'Error Response:',response.json())
        exit()
    data = response.json()
    return data