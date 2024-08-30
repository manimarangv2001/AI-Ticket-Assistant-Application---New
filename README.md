# Overview of the Basic AI Chatbot template

This app template is built on top of [Teams AI library](https://aka.ms/teams-ai-library).
This template showcases a bot app that responds to user questions like an AI assistant. This enables your users to talk with the AI assistant in Teams to find information.


## Get started with the template

> **Prerequisites**
>
> To run the template in your local dev machine, you will need:
>
> - [Python](https://www.python.org/), version 3.8 to 3.11.
> - [Python extension](https://code.visualstudio.com/docs/languages/python), version v2024.0.1 or higher.
> - [Teams Toolkit Visual Studio Code Extension](https://aka.ms/teams-toolkit) latest version or [Teams Toolkit CLI](https://aka.ms/teams-toolkit-cli).
> - An account with [Azure OpenAI](https://aka.ms/oai/access).
> - [Node.js](https://nodejs.org/) (supported versions: 16, 18) for local debug in Test Tool.

### Configurations
1. Open the command box and enter `Python: Create Environment` to create and activate your desired virtual environment. Remember to select `src/requirements.txt` as dependencies to install when creating the virtual environment.
1. In file *env/.env.testtool.user*, fill in your Azure OpenAI key `SECRET_AZURE_OPENAI_API_KEY`, deployment name `AZURE_OPENAI_MODEL_DEPLOYMENT_NAME` and endpoint `AZURE_OPENAI_ENDPOINT`.

### Conversation with bot
1. Select the Teams Toolkit icon on the left in the VS Code toolbar.
1. Press F5 to start debugging which launches your app in Teams App Test Tool using a web browser. Select `Debug in Test Tool`.
1. You will receive a welcome message from the bot, or send any message to get a response.

**Congratulations**! You are running an application that can now interact with users in Teams:

> For local debugging using Teams Toolkit CLI, you need to do some extra steps described in [Set up your Teams Toolkit CLI for local debugging](https://aka.ms/teamsfx-cli-debugging).

![ai chat bot](https://github.com/OfficeDev/TeamsFx/assets/9698542/9bd22201-8fda-4252-a0b3-79531c963e5e)

## What's included in the template

| Folder       | Contents                                            |
| - | - |
| `.vscode`    | VSCode files for debugging                          |
| `appPackage` | Templates for the Teams application manifest        |
| `env`        | Environment files                                   |
| `infra`      | Templates for provisioning Azure resources          |
| `src`        | The source code for the application                 |

The following files can be customized and demonstrate an example implementation to get you started.

| File                                 | Contents                                           |
| - | - |
|`src/app.py`| Hosts an aiohttp api server and exports an app module.|
|`src/bot.py`| Handles business logics for the Basic AI Chatbot.|
|`src/config.py`| Defines the environment variables.|
|`src/prompts/chat/skprompt.txt`| Defines the prompt.|
|`src/prompts/chat/config.json`| Configures the prompt.|

The following are Teams Toolkit specific project files. You can [visit a complete guide on Github](https://github.com/OfficeDev/TeamsFx/wiki/Teams-Toolkit-Visual-Studio-Code-v5-Guide#overview) to understand how Teams Toolkit works.

| File                                 | Contents                                           |
| - | - |
|`teamsapp.yml`|This is the main Teams Toolkit project file. The project file defines two primary things:  Properties and configuration Stage definitions. |
|`teamsapp.local.yml`|This overrides `teamsapp.yml` with actions that enable local execution and debugging.|
|`teamsapp.testtool.yml`|This overrides `teamsapp.yml` with actions that enable local execution and debugging in Teams App Test Tool.|

## Extend the template

You can follow [Build a Basic AI Chatbot in Teams](https://aka.ms/teamsfx-basic-ai-chatbot) to extend the Basic AI Chatbot template with more AI capabilities, like:
- [Customize prompt](https://aka.ms/teamsfx-basic-ai-chatbot#customize-prompt)
- [Customize user input](https://aka.ms/teamsfx-basic-ai-chatbot#customize-user-input)
- [Customize conversation history](https://aka.ms/teamsfx-basic-ai-chatbot#customize-conversation-history)
- [Customize model type](https://aka.ms/teamsfx-basic-ai-chatbot#customize-model-type)
- [Customize model parameters](https://aka.ms/teamsfx-basic-ai-chatbot#customize-model-parameters)
- [Handle messages with image](https://aka.ms/teamsfx-basic-ai-chatbot#handle-messages-with-image)

## Additional information and references

- [Teams Toolkit Documentations](https://docs.microsoft.com/microsoftteams/platform/toolkit/teams-toolkit-fundamentals)
- [Teams Toolkit CLI](https://aka.ms/teamsfx-toolkit-cli)
- [Teams Toolkit Samples](https://github.com/OfficeDev/TeamsFx-Samples)

## Known issue
- If you use `Debug in Test Tool` to local debug, you might get an error `InternalServiceError: connect ECONNREFUSED 127.0.0.1:3978` in Test Tool log. You can wait for Python launch console ready and then refresh the front end web page. 
- When you use `Launch Remote in Teams` to remote debug after deployment, you might loose interaction with your bot. This is because the remote service needs to restart. Please wait for several minutes to retry it. 











## TODO

- Create a tool that return servicenow catalog item description. In the tool's description add the catalog item names. and give the proper decription.
- Create a tool that return the knowledge base article. In the tool's description add the Knowledge article names. and give the proper decription.(if the user query is questionary )
- Create a ReAct that choose which tool to use based on the user query






Stage 1

    - Open AI should take only servicedesk related queries and normal converstions only other than it will say "I am not capable of it"

        - If your query is questionary then it check that your asked for ticket status 
        - If not about ticket status then search in knowledge base and show him the related articles
        - If not available in knowledge base then 

Stage 2

    - Finding Correct form from Servicenow based on User Query

        - getting the user query via teams bot
        - compare that query with embedded catalog item descriptions
        - Set the similarity threshold  
        - compare the query with every catalog item
        - if it is reach the threshold then fetch that catalog item
        - if it is not reach the threshold then get some extra details about user requirement and compare it again till reach the threshold.
        - return the sys_id of that catalog item

Stage 3

    - Prepare the API request body to Add catalog item values to cart.

        - Getting the missing variables from user via bot
        - Validating the details once with the User
        - Send it
        - If failed to submit the request then return the Instructions to create request or incident from Knowledge base articles.

Stage 4

    - Submit it

        - If failed to submit the request then return the Instructions to create request or incident from Knowledge base articles.

Stage 5

    - After the Submittion User will get the every change Activity details in Bot.