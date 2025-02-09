# pip install -U autogen-agentchat autogen-ext[openai,web-surfer]
# playwright install
import json
import os
from funcs.searchOnGoogle import search_with_keyword
import dotenv
import asyncio
from autogen_agentchat.agents import AssistantAgent, UserProxyAgent
from autogen_agentchat.conditions import TextMentionTermination
import os
from autogen import ConversableAgent
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.ui import Console
from autogen_ext.models.openai import OpenAIChatCompletionClient
from adapters.twitterSelected import search_tweets_by_user
dotenv.load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))
os.environ["OPENAI_API_KEY"] = "sk-QgmAi4cJM9KY9DF9MOglTSfgjjpZBaTQ5Yfh5zgiuSsCdAJP"
os.environ["OPENAI_BASE_URL"] = "https://ai.tzpro.xyz/v1"

model_client = OpenAIChatCompletionClient(model="gpt-4o",
                                          api_key="sk-QgmAi4cJM9KY9DF9MOglTSfgjjpZBaTQ5Yfh5zgiuSsCdAJP",
                                          base_url="https://ai.tzpro.xyz/v1")

newsSelector = ConversableAgent(
    name="newsSelector",
    llm_config={"config_list": [{"model": "gpt-4o", "temperature": 0.9, "api_key": "QgmAi4cJM9KY9DF9MOglTSfgjjpZBaTQ5Yfh5zgiuSsCdAJP", "base_url": "https://ai.tzpro.xyz/v1/"}]},
    description="""
    You are News Selector, a helpful agent. Please react as follows:
    Feature Description:
    News Selector is responsible for selecting information related to the most recent seven days of cryptocurrency quotes from the provided text and filtering out adverts and distracting information.
    ALL THE THINGS YOU NEED TO CHECK HAS BEEN PROVIDED IN THE CONTEXT!!
    DO NOT ASK ME FOR follow trusted cryptocurrency news sources or consult with a financial professional whatever.
    Screening criteria:
    1. the information must be related to cryptocurrency (e.g. bitcoin, ethereum, torrents, etc.) market dynamics, price fluctuations, industry news, etc.
    2. Timeframe: only news or information from the last seven days.
    3. Exclude adverts, promotional information, duplicate content or other irrelevant information.
    ...  
    Reply format:
    
    @{user1's username}: [Related information  
    @{user2's username}: [Related information1]  
    @{user3's username}: [Related information2]  
    ...  
     
    Other notes:
    - Information needs to be accurate and timely, avoiding misleading content.
    - Language should be clear and concise, highlighting key information.
    """)

debateAdviser = ConversableAgent(
    name="Debate_Adviser",
    llm_config={"config_list": [{"model": "gpt-4o", "temperature": 0.9,"base_url": "https://ai.tzpro.xyz/v1", "api_key": os.environ.get("OPENAI_API_KEY")}]},
    system_message="""
    You are Debate Adviser, a helpful agent. Your task is to analyze a series of user comments and separate them into two debate sides: the affirmative (正方) and the negative (反方).
    you are working for a crypto company and you are asked to record the daily updates on the crypto market by handling debates.
    Feature Description:
    Debate Adviser is responsible for processing user comments by retaining each comment's user id and content, then categorizing the comment based on its stance into one of two groups.

    Screening Criteria:
    1. Each comment must express a clear stance that can be identified as either affirmative or negative.
    2. Preserve the original user id and comment content.
    3. Exclude any comments that do not clearly fall into either category.

    Reply Format:
    Your output must strictly adhere to the following JSON schema:

    {
      "positive": [
         {"user_id": "<user id>", "content": "<comment content>"},
         ...
      ],
      "negative": [
         {"user_id": "<user id>", "content": "<comment content>"},
         ...
      ]
    }

    Other Notes:
    - Use clear, concise language in your analysis.
    - Invoke OpenAI as necessary to support your processing.
    - Ensure that the output is valid JSON strictly following the provided schema.
    """
)

assistant = AssistantAgent(
    name="Assistant",
    model_client=model_client,
    description="""
    You are Assistant, a helpful agent. Your task is to assist the user in generating a conversation between two agents.
    """
)

assistantRecorder = ConversableAgent(
    name="Assistant_Recorder",
    llm_config={"config_list": [{"model": "gpt-4o", "temperature": 0.9, "api_key": os.environ.get("OPENAI_API_KEY"), "base_url": os.environ.get("OPENAI_BASE_URL")}]},
    description="""
    You are Assistant Recorder, a helpful agent. Your task is to record and summarize the key points of a conversation between two agents.

    Feature Description:
    Assistant Recorder is responsible for monitoring and recording the conversation between two agents, summarizing the key points, and providing a concise summary of the discussion.
    you are working for a crypto company and you are asked to record the daily updates on the crypto market by handling debates.
    Screening Criteria:
    1. Record the key points and main ideas discussed by the agents.
    2. Summarize the conversation into a concise and coherent summary.
    3. Avoid irrelevant information and focus on the most important aspects.

    Reply Format:
    Your output must strictly adhere to the following format:

    [Summary of the conversation]
    [Agent 1's key points]
    [Agent 2's key points]
    ...

    Other Notes:
    - Summaries should be clear and easy to understand.
    - Language should be concise and to the point.
    """
)

debateParticipantA = ConversableAgent(
    name="Debate_Participant_A",
    llm_config={"config_list": [{"model": "gpt-4o", "temperature": 0.9, "api_key": os.environ.get("OPENAI_API_KEY"), "base_url": os.environ.get("OPENAI_BASE_URL")}]},
    system_message="""
    You are Debate Participant A, a helpful agent. Your task is to present arguments in a debate format.
    you are working for a crypto company and you are asked to provide daily updates on the crypto market by handling debates.
    Feature Description:
    Debate Participant A is responsible for presenting arguments in a debate format, supporting a given topic with clear and concise points.
    
    Screening Criteria:
    1. Present arguments that are relevant to the topic.
    2. Support your arguments with clear and concise points.
    3. Engage in a respectful and constructive debate.
    4. try to make more clear and concise points always use quotes, like as {$username} says "...." if u dont have the username generate a random one
    
    Reply Format:
    Your output must strictly adhere to the following format:
    [Argument 1]
    [Argument 2]
    [Argument 3]
    ...
    
    Other Notes:
    - Use clear, concise language in your arguments.
    - Avoid irrelevant information and focus on the topic.
    - Engage in a respectful and constructive debate.
""",)

debateParticipantB = ConversableAgent(
    name="Debate_Participant_B",
    llm_config={"config_list": [{"model": "gpt-4o", "temperature": 0.9, "api_key": os.environ.get("OPENAI_API_KEY"), "base_url": os.environ.get("OPENAI_BASE_URL")}]},
    system_message="""
    You are Debate Participant B, a helpful agent. Your task is to present arguments in a debate format.
    you are working for a crypto company and you are asked to provide daily updates on the crypto market by handling debates.
    Feature Description:
    Debate Participant B is responsible for presenting arguments in a debate format, supporting a given topic with clear and concise points.
    
    Screening Criteria:
    1. Present arguments that are relevant to the topic.
    2. Support your arguments with clear and concise points.
    3. Engage in a respectful and constructive debate.
    4. try to make more clear and concise points always use quotes, like as @username says "...."
    
    Reply Format:
    Your output must strictly adhere to the following format:
    [Argument 1]
    [Argument 2]
    [Argument 3]
    ...
    
    Other Notes:
    - Use clear, concise language in your arguments.
    - Avoid irrelevant information and focus on the topic.
    - Engage in a respectful and constructive debate.
""",)

judge = ConversableAgent(
    name="Judge",
    llm_config={"config_list": [{"model": "gpt-4o", "temperature": 0.9, "api_key": os.environ.get("OPENAI_API_KEY"), "base_url": os.environ.get("OPENAI_BASE_URL")}]},
    system_message="""
    You are Judge, a helpful agent. Your task is to listen to two agents debate and determine the winner based on the quality of their arguments.
    REMEMBER you have to make sure the debate is on the right topic and the arguments are valid, do let the agents know if they are not following the rules.
    The debate material is from X, a social media platform.
    You stand for a crypto company and was asked to provide daily updates on the crypto market by handling debates.
    Feature Description:
    Judge is responsible for listening to the debate between two agents and evaluating the quality of their arguments to determine the winner based on the strength of their points.
    YOU can search on google with the tool provided to check the facts.
    Screening Criteria:
    1. Evaluate the quality of the arguments presented by each agent.
    2. Determine the winner based on the strength of their points.
    3. Provide constructive feedback to the agents on their arguments.
    
    Reply Format:
    Your output must strictly adhere to the following format:
    [Winner: Agent 1 or Agent 2]
    [The good points that the winner made]
    [The bad points that the winner made]
    [The good points that the loser made]
    [The bad points that the loser made]
    
    REMEMBER: THE TERMINATION CONDITION IS 'exit'
    """
)

# host
host = ConversableAgent(
    name="Host",
    llm_config={"config_list": [{"model": "gpt-4o", "temperature": 0.9, "api_key": os.environ.get("OPENAI_API_KEY"), "base_url": os.environ.get("OPENAI_BASE_URL")}]},
    system_message="""
    You are Host, a helpful agent. Your task is to facilitate a conversation between two agents and ensure that the discussion remains on topic.
    You are the host of the debate and you are working for a crypto company and you are asked to provide daily updates on the crypto market by handling debates.
    MAKE SURE THEY ARE NOT GETTING TO FAR FRO THE DATA PROVIDED.
    """
)
    

# today_data = asyncio.run(search_tweets_by_user())
with open(os.path.join(os.path.dirname(__file__), "results.json")) as file:
    today_data = json.loads(file.read())
str1 = ""
for i in today_data:
    for j in i:
        str1 += "@" + j["user"]["username"] + ": " + j["text"] + "\n"


async def main() -> None:
    # user_proxy = UserProxyAgent("user_proxy")
    judge.register_for_llm(name="search_on_google", description="A simple gogle searching api")(search_with_keyword)
    termination = TextMentionTermination("NICEWORKS!")  # Type 'exit' to end the conversation.
    # team = RoundRobinGroupChat([newsSelector, debateAdviser, assistantRecorder, judge, user_proxy], termination,max_turns=5)
    user_msg = f"how is the crypto market this week? make a prediction with {str1}"
    chat_results = host.initiate_chats(
        [   
            {
                "recipient": newsSelector,
                "message": user_msg,
                "max_turns": 2,
                "summary_method": "last_msg",
            },
            {
                "recipient": debateAdviser,
                "message": "Try to make more clear and concise points always use quotes, like as @username says '....'",
                "max_turns": 2,
                "summary_method": "last_msg",
            },
            {
                "recipient": assistantRecorder,
                "message": "Record the key points and main ideas discussed by the agents",
                "max_turns": 2,
                "summary_method": "last_msg",
            },
            {
                "recipient": judge,
                "message": "Start the debate",
                "max_turns": 2,
                "summary_method": "last_msg",
            },
            {
                "recipient": debateParticipantA,
                "message": "Start the debate, support your arguments with clear and concise points, you are working for a crypto company and you are asked to provide daily updates on the crypto market by handling debates.",
                "max_turns": 2,
                "summary_method": "last_msg",
            },
            {
                "recipient": debateParticipantB,
                "message": "Start the debate, support your arguments with clear and concise points, you are working for a crypto company and you are asked to provide daily updates on the crypto market by handling debates.",
                "max_turns": 2,
                "summary_method": "last_msg",
            },
            # log
            {
                "recipient": assistantRecorder,
                "message": "Log the conservation, do not deviate from the topic and the data provided",
                "max_turns": 1,
                "summary_method": "last_msg",
            }
        ]
    )
    print(chat_results)
    # await Console(team.run_stream(task="how is the crypto market this week? make a prediction" + str1))

asyncio.run(main())
