import os
from typing import List, Dict, Any
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from langchain.agents import AgentExecutor, create_react_agent
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory
from tools import agent_tools
from database import SupabaseHistory
from dotenv import load_dotenv

load_dotenv()

class AgentCore:
    def __init__(self):
        self.history_db = SupabaseHistory()
        
        # Models configuration
        # Note: 'gemini-2.5-flash-preview-04-17' as requested. 
        # Falls back to Groq Llama 3.3 70b.
        main_model = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash", 
            google_api_key=os.environ.get("GEMINI_API_KEY"),
            temperature=0
        )
        
        fallback_model = ChatGroq(
            model="llama-3.3-70b-versatile",
            groq_api_key=os.environ.get("GROQ_API_KEY"),
            temperature=0
        )
        
        # Model with automatic fallback
        self.llm = main_model.with_fallbacks([fallback_model])
        
        # ReAct Prompt template
        template = """Answer the following questions as best you can. You have access to the following tools:

{tools}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Begin!

Context History:
{chat_history}

Question: {input}
Thought: {agent_scratchpad}"""

        self.prompt = PromptTemplate.from_template(template)
        
        # Agent initialization
        self.agent = create_react_agent(self.llm, agent_tools, self.prompt)
        
    def get_executor(self, session_id: str):
        # We load history manually and pass it to the prompt if we want, 
        # or use LangChain's memory. For better control with Supabase, 
        # let's map history to a memory object.
        history_data = self.history_db.get_history(session_id)
        
        # Create memory prepopulated with history
        memory = ConversationBufferMemory(memory_key="chat_history", return_messages=False)
        for msg in history_data:
            if msg['role'] == 'user':
                memory.chat_memory.add_user_message(msg['content'])
            else:
                memory.chat_memory.add_ai_message(msg['content'])
        
        return AgentExecutor(
            agent=self.agent,
            tools=agent_tools,
            memory=memory,
            verbose=True, # Reasoning in voice as requested
            handle_parsing_errors=True
        )

    def run(self, session_id: str, message: str) -> str:
        # 1. Save user message
        self.history_db.add_message(session_id, "user", message)
        
        # 2. Run agent
        executor = self.get_executor(session_id)
        try:
            response = executor.invoke({"input": message})
            answer = response["output"]
            
            # 3. Save assistant response
            self.history_db.add_message(session_id, "assistant", answer)
            return answer
        except Exception as e:
            error_msg = f"Agent Error: {str(e)}"
            self.history_db.add_message(session_id, "assistant", error_msg)
            return error_msg
