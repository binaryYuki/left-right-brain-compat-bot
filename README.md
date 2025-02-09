# README
### Hi! Please see readme.log for example output.

### you may found some hard-code API_KEY in codes but don't worry the api is fully managed by myself and have a restriction.
### Feel free to use it!

work.pdf contains brief intro of out works'architecture and the results of the experiments.

#### File Function
This script simulates an AI-driven multi-agent dialogue system using multiple custom ConversableAgents and third-party libraries (e.g., OpenAI's GPT model) to collaboratively process user input for analysis and debate on topics related to the cryptocurrency market.

#### Main Modules and Features
1. **Dependency Importing**
   - Use a variety of external dependency libraries (e.g. `autogen-agentchat`, `autogen-ext[openai,web-surfer]`, `playwright`, etc.).
   - Load the `.env` file to set the API key and model URL configuration.

2. **ConversableAgent Definitions
   - Defines multiple ConversableAgents with a clear division of responsibilities (news selection, debate support, summary logging, etc.):
     - **newsSelector**: Filters and selects news related to the cryptocurrency market for the last seven days, blocking advertisements and irrelevant information.
     - **debateAdviser**: analyses user comments and stores them sorted by pro and con.
     - **assistantRecorder**: Records and summarizes the main points of a two-agent dialogue.
     - **debateParticipantA/B**: Provide clear, relevant arguments as the pro and con sides of the debate.
     - **judge**: Judge the strengths and weaknesses of both sides of the debate and choose a winner.
     - **host**: moderates the flow of the dialogue, forcing the discussion to focus on the given topic. 3.

3. **Dialogue Functions**: Implement the `host.initiate
   - implements the `host.initiate_chats` method, which assigns tasks to agents to simulate debates and analysis around cryptocurrency topics.
   - Each dialogue task has a custom input message, maximum number of rounds, summary strategy, etc.

4. **Data processing**
   - Read the `results.json` file, parse and construct user social media comments from the cryptocurrency market as input context.
   - Inject the parsed content into the user's initial message to provide dialogue context.

5. **Asynchronous main functions**
   - Run the above multi-agent dialogue logic asynchronously using asyncio.
   - Generate dialogue result output at the end of the logic.

#### Core Technical Points
- **Multi-Agent Collaboration**: Define multiple ConversableAgents, each with its own role, to form a complex multi-agent dialogue and collaboration process.
- **API Integration**: Provide language generation and information retrieval capabilities for agents by configuring OpenAI GPT-4 models and tools from Google Search.
- **Dynamic Context Management**: Loads dynamic contexts for analysis by reading external JSON files and environment variables

The file `main.py` implements a multi-intelligence based dialogue and analysis script focused on the cryptocurrency domain. It simulates an efficient information extraction, debate and summary process in the domain through a reasonable division of labour and context injection.

`main.py` implements a multi-intelligence dialogue system that collaboratively generates summaries and decisions through analysis, filtering, and debate around topics related to the cryptocurrency market.


| **Module/Function Points** | **Description** |
| ------------------------|-----------------------------------------------------------------------------------------------------|
| **Dependency Import** | Introduces external libraries (e.g. `autogen-ext` and OpenAI API) and tools (e.g. `dotenv` and `playwright`) for functionality extensions.    | **Conversable
| **ConversableAgent Definition** | Define multiple agents (e.g., news filtering, comment analysis, debate participation, etc.) to implement different business logic responsibilities.                         | **ConversableAgent
| **Conversation Functionality** | Use `host` to moderate agent conversations, simulating the process of debating and analyzing cryptocurrency market topics.                                        | | **Data Processing** | `host'
| | **Data Processing** | Read external JSON files as dialogue context to dynamically load and analyze user comments.                                      | **Output Generation
| **Output Generation** | Aggregate the results of the dialogue to generate a final summary and key points of the market-related debate.                                                 | **Output generation** | Asynchronous main function
| **Asynchronous main function** | Uses `asyncio` to drive the entire dialogue logic asynchronously, efficiently scheduling agent tasks for collaborative processing.                                    | **Recommendation**: Use `asyncio` to drive the entire dialogue logic asynchronously.

**Recommendation**: Add exception handling and logging to each module to improve robustness.

Translated with DeepL.com (free version)

## **TF-IDF Score Formula**

$$text{TF-IDF Score} = \sum_{i = 1}^{N} \text{TF-IDF}(w_{i})$$


### **Definition of Variables**
$( N )$ = Total number of words in the document (tweet).  
$( w_{i} ) = The ( i )-th word in the document.  $
$( text{TF-IDF}(w_{i})) = The TF-IDF score of word ( w_{i} ), $ calculated as:

$\text{TF-IDF}(w_{i}) = \text{TF}(w_{i}) \times \text{IDF}(w_{i})$

where:
- **Term Frequency (TF)**: The frequency of word $( w_{i} ) $in the document:
  
$text{TF}(w_{i}) = \frac{\text{Number of times } w_{i} \text{ appears in the document}}{\text{Total number of words in the document}}$

- **Inverse Document Frequency (IDF)**: A measure of how unique the word is across the entire corpus:

$text{IDF}(w_{i}) = \log \left(\frac{\text{Total number of documents}}{\text{Number of documents containing } w_{i}} + 1\right)$

### **Interpretation**
- **Higher TF-IDF scores** indicate that a word is **important** in the document (tweet) but **not common** across all documents.
- Words that appear **frequently** in one document but **rarely** in others will have **higher importance scores**.

## **Normalize Engagement Metrics**

Each engagement metric is normalized using **Min-Max Scaling with 95th Percentile Clipping**:

### **1. Normalized Reply Count**
$\text{Norm Reply} = \frac{\min(\text{tweet reply count}, Q_{95}^{\text{reply}}) - \min(\text{tweet reply count})}{Q_{95}^{\text{reply}} - \min(\text{tweet reply count}) + 1e^{-8}}$

### **2. Normalized Quote Count**

$text{Norm Quote} = \frac{\min(\text{tweet quote count}, Q_{95}^{\text{quote}}) - \min(\text{tweet quote count})}{Q_{95}^{\text{quote}} - \min(\text{tweet quote count}) + 1e^{-8}}$

### **3. Normalized Conflict Ratio**
$text{Conflict Ratio} = \frac{\text{tweet reply count} + \text{tweet quote count}}{\text{tweet like count} + \text{tweet retweet count} + 1}$

$text{Norm Ratio} = \frac{\min(\text{Conflict Ratio}, Q_{95}^{\text{ratio}}) - \min(\text{Conflict Ratio})}{Q_{95}^{\text{ratio}} - \min(\text{Conflict Ratio}) + 1e^{-8}}$

### **Explanation of Variables**
$( Q_{95}^{\text{reply}}, Q_{95}^{\text{quote}}, Q_{95}^{\text{ratio}} ) $= **95th percentile values** for each metric.
- **Clipping** ensures outliers don’t dominate the scores.
$( 1e^{-8} )$ prevents division by zero.

### **Interpretation**
- Each metric is **scaled between 0 and 1**.
- Values are **adjusted to reduce the impact of outliers**.
- Higher values indicate **greater engagement relative to the dataset**.

## **Compute Engagement Score**

The **Engagement Score** is calculated as the sum of various engagement metrics:

$E = \text{tweet reply count} + \text{tweet retweet count} + \text{tweet like count} + \text{tweet quote count} + \text{tweet bookmark count}$

### **Explanation of Variables**
( E ) = **Engagement Score** (total interactions on a tweet).
$( \text{tweet reply count} ) = Number of replies to the tweet.$
$( \text{tweet retweet count} ) = Number of retweets.$
$( \text{tweet like count} ) = Number of likes.$
$( \text{tweet quote count} ) = Number of quote tweets.$
$( \text{tweet bookmark count} ) = Number of times the tweet was bookmarked.$

### **Interpretation**
- Higher engagement scores indicate **higher user interaction** with the tweet.
- The score considers **all forms of engagement**, not just likes or retweets.
- **Tweets with high engagement scores** are more likely to be **influential or viral**.

## **Compute Raw Importance Score**

The **raw importance score** is calculated as the product of the **TF-IDF Score** and the **Engagement Score**:

$\text{Importance Score} = \text{TF-IDF Score} \times \text{Engagement Score}$


### **Explanation of Variables**
$( \text{Importance Score} ) = The raw measure of a tweet’s importance.$
$( \text{TF-IDF Score} ) $= The importance of words in the tweet based on **Term Frequency-Inverse Document Frequency (TF-IDF)**:
  

$text{TF-IDF Score} = \sum_{i=1}^{N} \text{TF-IDF}(w_i)$

  where:
  $( N ) = Total number of words in the tweet.$
  $( w_i ) = The ( i )-th word in the tweet.$
  $( \text{TF-IDF}(w_i) ) = The TF-IDF value of word ( w_i ).$

$( \text{Engagement Score} ) = The total interaction with a tweet:$

$\text E = {tweet reply count} + \text{tweet retweet count} + \text{tweet like count} + \text{tweet quote count} + \text{tweet bookmark count} $

### **Interpretation**
- The **TF-IDF Score** captures **textual importance** based on how unique and relevant the words are.
- The **Engagement Score** captures **user interaction** with the tweet.
- **Multiplication** ensures that **only highly engaged tweets with important textual content** receive **higher importance scores**.
- This raw score will later be **normalized** to a **0-100 scale** for better interpretability.




