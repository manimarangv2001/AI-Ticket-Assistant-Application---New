import os
import sys
import traceback
import json

from botbuilder.core import MemoryStorage, TurnContext, MessageFactory
from teams import Application, ApplicationOptions, TeamsAdapter
from teams.state import TurnState

from state import AppTurnState

from config import Config

from .dialog_activity import DialogActivity
from .adaptive_card_activity import (show_welcome_card, 
                                     text_prompt_card, 
                                     generate_similar_results, 
                                     get_missing_variables_card, 
                                     show_validationCard,
                                     show_RequestItemCard
                                     )
from Initialization import create_catalog_item_db, create_kb_article_db
from Document_Store.retrive_from_dstore import checkSimilarity
from servicenow.configure_servicenow import fetch_variables_from_query, submit_catalog_item, get_request_item
from azure_openai.prompts import prepare_missed_param_questions

create_catalog_item_db.initialize_cat_item_docs()
create_kb_article_db.initialize_kb_art_docs()


config = Config()

# Define storage and application
storage = MemoryStorage()

app = Application[TurnState](
    ApplicationOptions(
        bot_app_id=config.APP_ID,
        storage=storage,
        adapter=TeamsAdapter(config),
    )
)

@app.turn_state_factory
async def turn_state_factory(context: TurnContext):
    return await AppTurnState.load(context, storage)


@app.conversation_update("membersAdded")
async def on_members_added(context: TurnContext, state: AppTurnState):
    state.user.userMail = 'admin'
    attachment = await show_welcome_card()
    await context.send_activity(MessageFactory.attachment(attachment))
    return True

@app.adaptive_cards.action_submit("ITSMService")
async def on_ITSMservice_submit(context: TurnContext, state: AppTurnState, data) -> None:
    # await context.send_activity(configure_openai.openAIFunction(context.activity.text))
    await context.send_activity(
                MessageFactory.attachment(text_prompt_card("Please provide a detailed explanation of your requirement."))
            )
    state.conversation.conversationType = data
    state.conversation.missingParam = True

    
@app.adaptive_cards.action_submit("TicketStatus")
async def on_TicketStatus_submit(context: TurnContext, state: AppTurnState, data) -> None:
    await context.send_activity(str(data))


@app.adaptive_cards.action_submit("SimilarResultForm")
async def on_SimilarResultForm_submit(context: TurnContext, state: AppTurnState, data) -> None:
    state.conversation.conversationType = data
    # await context.send_activity(str(data))
    await getting_param_from_query(context, state)

@app.adaptive_cards.action_submit("MadatoryParameter")
async def on_MandatoryParams_submit(context: TurnContext, state: AppTurnState, data) -> None:
    del data['verb']
    print(data)
    state.conversation.listOfQnA = data
    await ValidationStep(context, state, data)
    state.conversation.conversationType["verb"] = "ValidationStep"

@app.adaptive_cards.action_submit("ValidationSubmit")
async def on_ValidationCard_submit(context: TurnContext, state: AppTurnState, data) -> None:
    api_template = json.dumps(prepare_api_request(context, state))
    print(api_template)
    sys_id = state.conversation.conversationType["sys_id"]
    request_sys_id = submit_catalog_item(sys_id, api_template)
    request_item_response = get_request_item(request_sys_id)
    attachments = await show_RequestItemCard(request_item_response)
    for attachment in attachments:
        await context.send_activity(MessageFactory.attachment(attachment))
    state.conversation.conversationType["verb"] = "RequestItemCard"
    

def prepare_api_request(context: TurnContext, state: AppTurnState):
    template = {
        "sysparm_quantity": "1",
        "variables": {}
    }
    api_variables = state.conversation.arranged_api_request
    template["variables"] = api_variables
    state.conversation.arranged_api_request = template
    return template
    



@app.activity("message")
async def on_message(context: TurnContext, state: AppTurnState):
    # print(context.activity.text)
    print(state.conversation.conversationType)
    if context.activity.text != None:
        if state.conversation.conversationType['verb'] == "ITSMService":
            await ITSMService(context, state)
        elif state.conversation.conversationType['verb'] == "SimilarResultForm":
            await getting_param_from_query(context, state)
        elif state.conversation.conversationType["verb"] == "ValidationStep":
            print("Hello")

    else:
        if(state.conversation.conversationType['verb'] == "MissingViariablesPrompting"):
            variable_List = state.conversation.variable_List
            questions = state.conversation.listOfQuestions
            attachment = await get_missing_variables_card(variable_List, questions)
            await context.send_activity(MessageFactory.attachment(attachment))
        else:
            print("None value")

async def ValidationStep(context: TurnContext, state: AppTurnState, data):
    parsed_variables = state.conversation.parse_variable_details
    api_request = state.conversation.arranged_api_request
    for variable in data:
        api_request[variable] = data[variable]
        parsed_variables[variable] = data[variable]
    state.conversation.arranged_api_request = api_request
    state.conversation.parse_variable_details = parsed_variables
    print(f"api_request : {api_request}")
    variable_List = state.conversation.variable_List
    # print(variable_List)
    print(state.conversation.parse_variable_details)
    state.conversation.arranged_api_request = api_request
    attachment = await show_validationCard(variable_List, parsed_variables)
    await context.send_activity(MessageFactory.attachment(attachment))
    

async def getting_param_from_query(context: TurnContext, state: AppTurnState):
    sys_id = state.conversation.conversationType['sys_id'] 
    user_query = state.conversation.userQuery
    similar_catalog_items = state.conversation.similar_catalog_items
    print(state.conversation.conversationType['sys_id'])
    variable_List, catalog_item_description, parse_variable_details, arranged_api_request, missing_mandatory_variables = fetch_variables_from_query(user_query, sys_id,similar_catalog_items)
    print(catalog_item_description)
    print(parse_variable_details)
    print(arranged_api_request)
    print(missing_mandatory_variables)
    state.conversation.variable_List = variable_List
    state.conversation.arranged_api_request = arranged_api_request
    state.conversation.catalog_item_description = catalog_item_description
    state.conversation.parse_variable_details = parse_variable_details
    state.conversation.missing_mandatory_variables = missing_mandatory_variables

    if(missing_mandatory_variables != []):
        missing_variable_questions = prepare_missed_param_questions(catalog_item_description, parse_variable_details, missing_mandatory_variables)
        state.conversation.conversationType['verb'] = "MissingViariablesPrompting"
        state.conversation.listOfQuestions = missing_variable_questions
        print(state.conversation.listOfQuestions)
        await context.send_activity(
            MessageFactory.attachment(text_prompt_card("Thanks you for your patience. It's seems like you forgot to mention some information. Don't worry, Please answer the following questions."))
        )
    else:
        state.conversation.conversationType["verb"] = "ValidationStep"
        
async def ITSMService(context: TurnContext, state: AppTurnState):
    query = context.activity.text
    state.conversation.userQuery = query
    similar_catalog_items = await checkSimilarity(query)
    state.conversation.similar_catalog_items = similar_catalog_items
    attachment = generate_similar_results(similar_catalog_items)
    await context.send_activity(attachment)


@app.error
async def on_error(context: TurnContext, error: Exception):
    # This check writes out errors to console log .vs. app insights.
    # NOTE: In production environment, you should consider logging this to Azure
    #       application insights.
    print(f"\n [on_turn_error] unhandled error: {error}", file=sys.stderr)
    traceback.print_exc()

    # Send a message to the user
    await context.send_activity("The bot encountered an error or bug.")