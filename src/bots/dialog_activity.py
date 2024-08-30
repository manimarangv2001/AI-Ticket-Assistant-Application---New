from botbuilder.core import TurnContext

from botbuilder.core import (
    TurnContext,
    MessageFactory,
)
from state import AppTurnState
from .adaptive_card_activity import text_prompt_card

class DialogActivity:

    @staticmethod
    async def fill_out_missing_param(
            turn_context: TurnContext, state: AppTurnState
            ):
        user_input = turn_context.activity.text

        index_count = state.conversation.index_count
        allquestions = state.conversation.listOfQuestions
        resultList = state.conversation.listOfQnA
        result = {}
        questions = [allquestions[i] for i in allquestions]

        if (len(questions) == index_count):
            result = {questions[index_count-1]: user_input}
            resultList.append(result)
            await turn_context.send_activity(
                MessageFactory.attachment(text_prompt_card("Thanks for the Details proceed to create ticket."))
            )
            state.conversation.conversationTypep["verb"] = "MissingPromptCompleted"
            index_count = 0
            state.conversation.missingParam = False
        
        elif index_count == 0:
            resultList = []
            question = questions[index_count]
            await turn_context.send_activity(
                    MessageFactory.attachment(text_prompt_card(question))
                )
            index_count += 1

        else:
            result = {questions[index_count-1]: user_input}
            resultList.append(result)
            question = questions[index_count]
            await turn_context.send_activity(
                    MessageFactory.attachment(text_prompt_card(question))
                )
            index_count += 1

        state.conversation.index_count = index_count
        state.conversation.listOfQnA = resultList

        
            

            

