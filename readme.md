# Python and AIML-based Chatbot
It is a terminal-based chatbot, where you can converse with your bot. The bot is currently capable of solving mathematical expressions and can have an introductory chat. More functionalities are under construction.
****
**Technologies used:**
1. Python (3.11.1)
2. AIML (python-aiml)
3. Neo4j (py2neo)
4. Xformers (Xformers will show a warning message for Python version < 3.11.3)
5. NLTK (NLP)
6. ChatGPT
****
__Capabilities:__
1. User Authentication
2. Episodic Memory
3. Storing user chat to train ML model
4. Solving mathematical expressions
5. Sentimental Analysis (using '__nlptown/bert-base-multilingual-uncased-sentiment__' model for sentiment analysis)
****
### User Authentication
The bot will ask for the user's name, if he wants to provide he can, if he doesn't then he's free to move on. But if the user tells the bot his name, the bot will assign a unique id to the user __(make sure to remember it or keep it safe because if it's gone; it's gone)__
****
### User Input Bot Response
At every user input, a bot response will be returned from the aiml file, if there is no response or the bot doesn't know the answer, it'll request the GPT for a response. Whether the response is from the bot or the GPT, all the conversational records are stored in the memory.
****
### Memories
There are 2 types of memories available:
* Long Term
* Short Term

Personal Memory is currently unavailable


**Long Term**

Long Term memory is used to store known users' data and their conversations with a bot. The memory is stored in the form of episodes.

**Short Term**


Short Term memory is used to store unknown users' data and their conversations with the bot. Same, the bot stores the conversation in the form of episodes. 

The difference is, there is only __one__ folder named anonymous and it contains all the anonymous users. While in the case of long-term memory, all the user's data is stored in their respective folders with their id.
****
The sample data is available in the memory folder. Your output should look like this for known users:

![Episodic](https://raw.githubusercontent.com/Athar-Naveed/chatbot-using-aiml-and-neo4j/main/img/Screenshot%202023-06-19%20005135.png)
<br />
And this should be your output for unknown users:

![Anonymous](https://raw.githubusercontent.com/Athar-Naveed/chatbot-using-aiml-and-neo4j/main/img/Screenshot%202023-06-19%20005631.png)
****
### Sentimental Analysis
At every moment of the conversation, the bot is analyzing the user's mood and does a conversation based on it. If the conversation has <= __3 stars__ more than __3 times__ then the bot will assume your mood is __OFF__. So it will switch the conversation. As I am using '__nlptown/bert-base-multilingual-uncased-sentiment__' model for sentiment analysis, your language doesn't matter.
******
#### NOTE: THE PROGRAM EXECUTION SPEED MAY VARY DEPENDING ON YOUR COMPUTER'S SPEED.