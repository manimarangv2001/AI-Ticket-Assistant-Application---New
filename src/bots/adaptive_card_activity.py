import os
import json
from botbuilder.core import CardFactory, MessageFactory
from botbuilder.schema import Attachment
from typing import List



async def show_welcome_card() -> Attachment:
    ADAPTIVECARDTEMPLATE = "adaptive_card_json\\welcome_card.json"
    card_path = os.path.join(os.getcwd(), ADAPTIVECARDTEMPLATE)
    with open(card_path, 'r') as openfile:
        json_object = json.load(openfile)
    return CardFactory.adaptive_card(json_object)


def text_prompt_card(text: str) -> Attachment:
    ADAPTIVECARDTEMPLATE = "adaptive_card_json\\text_prompt_card.json"
    card_path = os.path.join(os.getcwd(), ADAPTIVECARDTEMPLATE)
    with open(card_path, 'r') as openfile:
        json_object = (json.load(openfile))
        json_object['body'][0]['text'] = text
    return CardFactory.adaptive_card(json_object)


def generate_similar_results(similar_results: List):
    carousel_card = []
    ADAPTIVECARDTEMPLATE = "adaptive_card_json\\similar_result_form.json"
    card_path = os.path.join(os.getcwd(), ADAPTIVECARDTEMPLATE)
    
    for result in similar_results:
        with open(card_path, 'r') as openfile:
            json_object = (json.load(openfile))
            json_object['body'][1]['text'] = result['sys_name']
            json_object['body'][2]['text'] = result['short_description']
            json_object['body'][3]['text'] = result['description']
            json_object['body'][4]['actions'][0]['data']['sys_id'] = result['sys_id']

        cardform = CardFactory.adaptive_card(json_object)
        carousel_card.append(cardform)

    message = MessageFactory.carousel(carousel_card)
    return message


def create_choice_field(variable, question):
    choice_field = {
            "type": "Input.ChoiceSet",
            "style": "compact"
        }
    choice_field['id'] = variable['name']
    choice_field['label'] = question
    choice_field['isRequired'] = True
    choice_field['errorMessage'] = f"{variable['label']} is mandatory"
    choice_field['value'] = variable['value']
    choices = []
    if("reference_values" in variable):
        for value in variable['reference_values'].split(', '):
            choices.append({"title": value, "value": value})
        choice_field["choices"] = choices
    return choice_field


def create_input_text_field(variable, question):
    input_text_field = {
                "type": "Input.Text",
                "style": "text",
            }
    input_text_field['id'] = variable['name']
    input_text_field['label'] = question
    input_text_field['isRequired'] = True
    input_text_field['errorMessage'] = f"{variable['label']} is mandatory"
    input_text_field['value'] = variable['value']
    input_text_field['placeholder'] = variable['label']
    
    return input_text_field    

async def create_variables_fields(catalog_variables, questions):
    variables_fields = []
    for variable in catalog_variables:
        type = variable['type']
        for questionVariable in questions:
            if(variable['name'] == questionVariable):
                if(type == 6):
                    variables_fields.append(create_input_text_field(variable, questions[questionVariable]))
                elif(type == 8 or type == 31 or type == 5 or type == 18):
                    variables_fields.append(create_choice_field(variable, questions[questionVariable]))
    return variables_fields


async def get_missing_variables_card(catalog_item, questions) -> Attachment:
    ADAPTIVECARDTEMPLATE = "adaptive_card_json\\missing_param_form.json"
    card_path = os.path.join(os.getcwd(), ADAPTIVECARDTEMPLATE)
    with open(card_path, 'r') as openfile:
        json_object = json.load(openfile)
        print(catalog_item)
        variable_fields = await create_variables_fields(catalog_item, questions)
        print(variable_fields)
        json_object['body'].extend(variable_fields)
        print(json_object)
    return CardFactory.adaptive_card(json_object)


async def prepare_validation_card(catalog_item, parsed_variables):
    text = []
    count = 0
    for variable in catalog_item:
            if(variable['name'] in parsed_variables):
                if(count < len(variable['label'])):
                    count = len(variable['label'])
                if(variable['type'] == 31):
                    text.append({"name":variable['label'],"value": os.environ["SERVICENOW_USERNAME"]})
                else:
                    text.append({"name":variable['label'],"value": parsed_variables[variable['name']]})
    print(text)
    result = ""
    for variable in text:
        result += f"**{variable['name'].ljust(count)}:** {variable['value']}\n\n"
    print(result)
    return result

async def show_validationCard(catalog_item, parsed_variables):
    ADAPTIVECARDTEMPLATE = "adaptive_card_json\\validation_form.json"
    card_path = os.path.join(os.getcwd(), ADAPTIVECARDTEMPLATE)
    with open(card_path, 'r') as openfile:
        json_object = json.load(openfile)
        print(json_object)
        json_object['body'][1]['text'] = await prepare_validation_card(catalog_item, parsed_variables)
    return CardFactory.adaptive_card(json_object)



    
def get_state(state):
    if(state == "1"):
        state = "Open"
    return state



async def show_RequestItemCard(request_item_response):
    ADAPTIVECARDTEMPLATE = "adaptive_card_json\\RequestItem_Card.json"
    card_path = os.path.join(os.getcwd(), ADAPTIVECARDTEMPLATE)
    result = []
    json_object = {}
    with open(card_path, 'r') as openfile:
        json_object = json.load(openfile)
        print(json_object)
    for request_item in request_item_response["result"]:
        adaptive_card = json_object
        adaptive_card["body"][0]["items"][0]["columns"][1]["items"][0]["actions"][0]["url"] = request_item["sys_id"]
        facts = [
            {
                "title": "Number", 
                "value": request_item["number"]
            }, 
            {
                "title": "Short Description", 
                "value": request_item["short_description"]
            },
            {
                "title": "State", 
                "value": get_state(request_item["state"])
            }
        ]
        adaptive_card["body"][0]["items"][1]["facts"] = facts
        result.append(CardFactory.adaptive_card(adaptive_card))
        print(result)
    return result

        