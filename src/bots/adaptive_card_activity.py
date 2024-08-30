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

