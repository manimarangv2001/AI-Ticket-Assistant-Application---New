import os
import sys
import traceback

from botbuilder.core import MemoryStorage, TurnContext, MessageFactory
from teams import Application, ApplicationOptions, TeamsAdapter
from teams.state import TurnState

from state import AppTurnState

from config import Config

from .dialog_activity import DialogActivity
from .adaptive_card_activity import show_welcome_card, text_prompt_card, generate_similar_results
from Initialization import create_catalog_item_db, create_kb_article_db
from Document_Store.retrive_from_dstore import checkSimilarity
from servicenow.configure_servicenow import prepare_api_request
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
                MessageFactory.attachment(text_prompt_card("Start typing your isuues.."))
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


@app.activity("message")
async def on_message(context: TurnContext, state: AppTurnState):
    # print(context.activity.text)
    print(state.conversation.conversationType)
    if context.activity.text != None:
        if state.conversation.conversationType['verb'] == "ITSMService":
            await ITSMService(context, state)
        elif state.conversation.conversationType['verb'] == "SimilarResultForm":
            await getting_param_from_query(context, state)
        elif state.conversation.conversationType['verb'] == "MissingViariablesPrompting":
            await ask_missing_param_questions(context, state)
        elif state.conversation.conversationType["verb"] == "MissingPromptCompleted":
            pass

    else:
        if(state.conversation.conversationType['verb'] == "MissingViariablesPrompting" and state.conversation.index_count == 0):
            await ask_missing_param_questions(context, state)
        else:
            print("None value")

async def getting_param_from_query(context: TurnContext, state: AppTurnState):
    sys_id = state.conversation.conversationType['sys_id'] 
    user_query = state.conversation.userQuery
    print(state.conversation.conversationType['sys_id'])
    fulldefined_catalog_item, catalog_item_description, parse_variable_details, arranged_api_request, missing_mandatory_variables = prepare_api_request(user_query, sys_id)
    print(arranged_api_request)
    print(missing_mandatory_variables)
    state.conversation.catalog_item = fulldefined_catalog_item
    print(fulldefined_catalog_item)
    if(missing_mandatory_variables != []):
        missing_variable_questions = prepare_missed_param_questions(catalog_item_description, parse_variable_details, missing_mandatory_variables)
        state.conversation.conversationType['verb'] = "MissingViariablesPrompting"
        state.conversation.listOfQuestions = missing_variable_questions
        print(state.conversation.listOfQuestions)
        await context.send_activity(
            MessageFactory.attachment(text_prompt_card("Thanks you for your patience. It's seems like you forgot to mention some information. Don't worry, Please answer the following questions."))
        )
    else:
        state.conversation.conversationType["verb"] = "MissingPromptCompleted"
        
async def ITSMService(context: TurnContext, state: AppTurnState):
    query = context.activity.text
    state.conversation.userQuery = query
    similar_catalog_items = await checkSimilarity(query)
    attachment = generate_similar_results(similar_catalog_items)
    await context.send_activity(attachment)

async def ask_missing_param_questions(context: TurnContext, state: AppTurnState):
    print(state.conversation.index_count)
    print(state.conversation.listOfQnA)
    await DialogActivity.fill_out_missing_param(context, state)
    



@app.error
async def on_error(context: TurnContext, error: Exception):
    # This check writes out errors to console log .vs. app insights.
    # NOTE: In production environment, you should consider logging this to Azure
    #       application insights.
    print(f"\n [on_turn_error] unhandled error: {error}", file=sys.stderr)
    traceback.print_exc()

    # Send a message to the user
    await context.send_activity("The bot encountered an error or bug.")