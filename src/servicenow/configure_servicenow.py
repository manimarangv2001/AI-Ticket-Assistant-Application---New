import os
from langchain.schema import HumanMessage
import json
from .servicenow_api_activity import (get_table_sysid,
                                      get_specific_catalog_item, 
                                      get_table_values, 
                                      get_table_response, 
                                      get_tableValue_via_link,
                                      add_cart, 
                                      request_item_api_call,
                                      submit_order
                                      )
from langchain_openai import AzureOpenAIEmbeddings, AzureChatOpenAI 
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser
from langchain_core.prompts import PromptTemplate
import re
import sqlite3

model = AzureChatOpenAI(
    api_key="107c20f6b6774c80b98c6f6a828f6374",
    azure_deployment="gpt-4",
    azure_endpoint="https://2000081253-openai.openai.azure.com/",
    api_version="2023-03-15-preview"
)

def fetchVariables(data, variables_name):

    template = """{data}
    
    from the given data Return only the variables name as a key and variable description as a value in JSON.
    The description must describe contains choices and ui_policy too as a single output
    Variable Description must contain all choices without leave
    The variablename should be one of the name from the given List. {variables_name}
    And no premable or explaination.

    Example:
    variablename : variabledescription

    """
    
    prompt_template = PromptTemplate(template=template, input_variables=["data", variables_name])
    chain = prompt_template | model | JsonOutputParser()
    response = chain.invoke({"data": data, "variables_name": variables_name})
    # # # print(response)
    return response


def create_custom_function(variable_info, custom_functions, variables_description):
    inner_json = {}
    inner_json["type"] = "string"
    if(variable_info["name"] in variables_description):
        inner_json["description"] = variables_description[variable_info["name"]]
        custom_functions[0]["parameters"]["properties"][variable_info["name"]] = inner_json
    return custom_functions


def function_calling_catVar(catalog_variables, catalog_item_description, variables_name):
    custom_functions = [
        {
            "name": "extract_catalog_variables",
            "description": "Get the values from the body of the user query",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
        ]
    variables_description = fetchVariables(catalog_item_description, variables_name)


    for variable_info in catalog_variables:
        if "children" in variable_info:
            for child_var_info in variable_info["children"]:
                # # # print(child_var_info)
                custom_functions = create_custom_function(child_var_info, custom_functions, variables_description)
        else:
            custom_functions = create_custom_function(variable_info, custom_functions, variables_description)
    # print(catalog_item_description)
    print(custom_functions)
    return custom_functions


def get_all_variables_List(catalog_item_variable):
    def extract_variables(variables):
        variable_List = []
        for variable_info in variables:
            if variable_info["type"] == 24 or variable_info['type'] == 11:
                continue
            if "children" in variable_info:
                variable_List.extend(extract_variables(variable_info["children"]))
            else:
                variable_List.append(variable_info)
        return variable_List
    return extract_variables(catalog_item_variable)


def set_reference_value(variable):

    if(variable["type"] == 8 and variable["dynamic_value_field"] == ""):
        reference = variable["reference"]
        table_content = get_table_values(reference=reference)
        names_in_table = []
        for content in table_content["result"]:
            if("u_name" in content):
                names_in_table.append(content["u_name"])
            elif("name" in content):
                names_in_table.append(content["name"])
        variable["reference_values"] = ", ".join(names_in_table)
        return variable
    
    elif (variable["type"] == 5 or variable["type"] == 18):
        choiceList = []
        for choice in variable["choices"]:
            choiceList.append(choice["value"])
        variable["reference_values"] = ", ".join(choiceList)
        return variable

    elif(variable["value"] != ""):
        variable["displayvalue"] = variable["value"]
        return variable

    else:
        return variable

def fetch_ui_actions(action_field, catalog_variables):
    ui_action_variable_list = []
    for action_variables in action_field:
        action_variable_id = action_variables["name"].split(":")[1] 
        for variable in catalog_variables:
            # # # print(f"{variable["id"]} = {action_variable_id}")
            if(variable["id"] == action_variable_id):
                ui_action_variable_list.append({"name": variable["name"], "mandatory": action_variables["mandatory"]})
    
    return ui_action_variable_list


def fetch_ui_policy(catalog_item, catalog_variables):
    final_ui_condition_action = []
    for catalog_ui_policy in catalog_item["result"]["ui_policy"]:
        for condition_field in catalog_ui_policy["conditions"]:
            action_field = catalog_ui_policy["actions"]
            ui_action_variable_list = fetch_ui_actions(action_field, catalog_variables)
            variable_id = condition_field["field"].split(":")[1]
            for variable in catalog_variables:
                if variable["id"] == variable_id:
                    ui_condition = {"condition_variable_name":variable["name"],"condition_variable_value": condition_field["value"], "condition_operation": condition_field["oper"], "ui_actions": ui_action_variable_list}
                    final_ui_condition_action.append(ui_condition)
    return final_ui_condition_action


def combine_values(parse_variable_details,variables_template):
    for key in parse_variable_details:
        if key in variables_template:
            variables_template[key] = parse_variable_details[key]
    return variables_template


def get_valuefor_reqfor(variable_info, variables_template, fetched_variables):
        reference = variable_info["reference"]
        sysparm_for_query = "user_name"
        value_for_query = os.environ["SERVICENOW_USERNAME"]
        # print(reference + sysparm_for_query + value_for_query)
        sys_id = get_table_sysid(reference, sysparm_for_query, value_for_query)["result"][0]["sys_id"]
        variables_template[variable_info["name"]] = sys_id
        fetched_variables[variable_info["name"]] = sys_id
        return fetched_variables, variables_template

def get_valuefor_reference(variable_info, variables_template, fetched_variables, dynamic_value_dot_walk_path):
    reference = variable_info["reference"] # u_software

    sample_table_response = get_table_response(reference)
    if "u_name" in sample_table_response["result"][0]:
        sysparm_for_query = "u_name" # name
    elif "name" in sample_table_response["result"][0]:
        sysparm_for_query = "name"

    if(variable_info["name"] in fetched_variables):
        value_for_query = fetched_variables[variable_info["name"]] # python
        sys_id = get_table_sysid(reference, sysparm_for_query, value_for_query)["result"][0][dynamic_value_dot_walk_path]
        variables_template[variable_info["name"]] = sys_id
        
    return fetched_variables, variables_template


def is_valid_sys_id(value):
    return bool(re.fullmatch(r"[0-9a-fA-F]{32}", value))

def get_dynamicvalues_name(link):
    table_content = get_tableValue_via_link(link)
    # print(table_content)
    value = ""
    if("name" in table_content['result']):
        value = table_content['result']['name']
    elif("u_name" in table_content):
        value = table_content["result"]['u_name']
    return value




def get_valuefor_dynamicvalues(variables_List, variable_info, variables_template, fetched_variables):

    for variables in variables_List:
        if(variables["id"] == variable_info["dynamic_value_field"]):
            reference = variables["reference"]
            sysparm_for_query = "sys_id"# variable_info["dynamic_value_dot_walk_path"]
            value_for_query = variables_template[variables["name"]]
        
            # print(" reference =  "+ reference +" sysparm_for_query =  "+ sysparm_for_query +" value_for_query = "+ value_for_query)
            # print([variable_info["dynamic_value_dot_walk_path"]])
            requireddetails = get_table_sysid(reference, sysparm_for_query, value_for_query)
            if("result" in requireddetails):
                resultValue = requireddetails["result"]
                if(isinstance(resultValue, list)):
                    # print(resultValue)
                    if(0<len(resultValue)):
                        requireddetails = resultValue[0][variable_info["dynamic_value_dot_walk_path"]]
            finalDetail = ""
            # print(requireddetails)
            if("value" in requireddetails):
                finalDetail = requireddetails["value"]
                fetched_variables[variable_info["name"]] = get_dynamicvalues_name(requireddetails["link"])
            else:
                finalDetail = requireddetails
                fetched_variables[variable_info["name"]] = finalDetail
            variables_template[variable_info["name"]] = finalDetail

    # print(fetched_variables)

    return fetched_variables, variables_template


def assign_complex_variables(fetched_variables, variables_template, variables_List):
    variables_template = combine_values(fetched_variables, variables_template)
    for variable_info in variables_List:
        # print(variable_info["name"])
        if(variable_info["type"] == 31):            # for requested_for type
            fetched_variables, variables_template = get_valuefor_reqfor(variable_info, variables_template, fetched_variables)

        elif(variable_info["name"] in fetched_variables and variable_info["type"] == 8):
            fetched_variables, variables_template = get_valuefor_reference(variable_info, variables_template, fetched_variables, "sys_id")

        elif (variable_info["dynamic_value_field"] != ""):
            fetched_variables, variables_template = get_valuefor_dynamicvalues(variables_List, variable_info, variables_template, fetched_variables)
    return fetched_variables, variables_template

def fetch_mandatory_variables(variables_template, ui_policy,variables_List):
    missing_mandatory_variables = []
    ui_based_mandatory_variables = []
    for variable in variables_List:
        if(variable["mandatory"] == True):
            if(variables_template[variable["name"]] == ""):
                missing_mandatory_variables.append(variable["name"])
            ui_based_mandatory_variables.append(variable["name"])
    for ui_condition in ui_policy:
        if(ui_condition["condition_operation"] == "="):
            value = variables_template[ui_condition["condition_variable_name"]]
            if(value == ui_condition["condition_variable_value"]):
                ui_actions = ui_condition["ui_actions"]
                for ui_action in ui_actions:
                    if(ui_action["mandatory"] == "true"):
                        if(variables_template[ui_action["name"]] == ""):
                            missing_mandatory_variables.append(ui_action["name"])
                        ui_based_mandatory_variables.append(ui_action["name"])
                    
    return variables_template, missing_mandatory_variables, ui_based_mandatory_variables

def fetch_desc_using_sys_id(sys_id):
    db_path = "c:\\Users\\2000081253\\Desktop\\Work\\AI-Copilot-Ticket-Assistant\\src\\Document_Store\\catalog_item_db\\chroma.sqlite3"
    row_id = 0
    catalog_item_description = ""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM embedding_metadata") 
    rows = cursor.fetchall()
    for row in rows:
        if(row[1] == 'sys_id' and row[2] == sys_id):    
            row_id = row[0]
    for row in rows:
        if(row[0] == row_id and row[1] == 'chroma:document'):
            catalog_item_description = row[2]
    conn.close()
    return catalog_item_description



def fetch_variables_from_query(user_query, sys_id, similar_catalog_items):
    catalog_item_description = ""
    for similar_catalog_item in similar_catalog_items:
        if(similar_catalog_item["sys_id"] == sys_id):
            catalog_item_description = similar_catalog_item["page_content"]


    # catalog_item_description = fetch_desc_using_sys_id(sys_id)
    catalog_item = get_specific_catalog_item(sys_id)
    catalog_variables = catalog_item["result"]["variables"]
    all_variables = get_all_variables_List(catalog_variables)
    ui_policy = fetch_ui_policy(catalog_item, all_variables)
    variables_List = []
    variables_template = {}
    variables_name = []
    for variable in all_variables:
        variable = set_reference_value(variable)
        variables_List.append(variable)
        variables_name.append(variable["name"])
        value = variable["value"]
        if(value == True):
            variables_template[variable["name"]] = "true"
        elif(value == False):
            variables_template[variable["name"]] = "false"
        else:
            variables_template[variable["name"]] = value
    print(variables_template)
    custom_function = function_calling_catVar(variables_List, catalog_item_description, variables_name)
    print(custom_function)
    message = model.predict_messages(
    [HumanMessage(content=f"user query: {user_query}")],
    functions = custom_function
    )

    # print(variables_List)
    # print(custom_function)
    # print(json.dumps(message.__dict__))

    if message.additional_kwargs != {}:
        # print("The "additional_kwargs" attribute exists.")
        parse_variable_details = json.loads(message.additional_kwargs["function_call"]["arguments"])
        for variable in parse_variable_details:
            if(parse_variable_details[variable] == True):
                parse_variable_details[variable] = 'true'
            if(parse_variable_details[variable] == False):
                parse_variable_details[variable] = 'false'
        
        parse_variable_details,variables_template= assign_complex_variables(parse_variable_details,variables_template, variables_List)
        variables_template, missing_mandatory_variables, ui_based_mandatory_variables = fetch_mandatory_variables(variables_template, ui_policy,variables_List)
        
        final_parse_variable_details = {}
        print(f"parse variable : {parse_variable_details}")
        for variable in parse_variable_details:
            # print(variable)
            if (variable in ui_based_mandatory_variables):
                final_parse_variable_details[variable] = parse_variable_details[variable]

    return variables_List,catalog_item_description, final_parse_variable_details, variables_template, missing_mandatory_variables


def submit_catalog_item(sys_id, api_template):
    card_id = add_cart_item(sys_id, api_template)
    submit_result = submit_order(card_id)
    request_sys_id = submit_result["result"]["request_id"]
    return request_sys_id


def add_cart_item(sys_id, api_template):
    add_cart_response = add_cart(sys_id, api_template)
    print(add_cart_response)
    cart_id = add_cart_response["result"]["cart_id"]
    # print(cart_id)
    return cart_id

def get_request_item(request_sys_id):
    request_item_result = request_item_api_call(request_sys_id)
    return request_item_result

