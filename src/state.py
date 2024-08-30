"""
Copyright (c) Microsoft Corporation. All rights reserved.
Licensed under the MIT License.
"""

from typing import Optional, List, Dict

from botbuilder.core import Storage, TurnContext
from teams.state import ConversationState, TempState, TurnState, UserState

class AppUserState(UserState):
    userMail: str = ""

    @classmethod
    async def load(cls, context: TurnContext, storage: Optional[Storage] = None) -> "AppUserState":
        state = await super().load(context, storage)
        return cls(**state)


class AppConversationState(ConversationState):
    missingParam: bool = False
    listOfQnA: List[Dict[str, str]] = []
    listOfQuestions: Dict[str, str] = {}
    index_count: int = 0
    catalog_item = {}
    
    conversationType: Dict[str, str] = {}
    userQuery = ""

    @classmethod
    async def load(cls, context: TurnContext, storage: Optional[Storage] = None) -> "AppConversationState":
        state = await super().load(context, storage)
        return cls(**state)

class AppTempState(TempState):
    catalog_item_descriptions = []

    @classmethod
    async def load(cls, context: TurnContext, storage: Optional[Storage] = None) -> "AppTempState":
        state = await super().load(context, storage)
        return cls(**state)



class AppTurnState(TurnState[AppConversationState, AppUserState, AppTempState]):
    conversation: AppConversationState
    user: AppUserState
    temp: AppTempState

    @classmethod
    async def load(cls, context: TurnContext, storage: Optional[Storage] = None) -> "AppTurnState":
        return cls(
            conversation=await AppConversationState.load(context, storage),
            user=await AppUserState.load(context, storage),
            temp=await AppTempState.load(context, storage),
        )
