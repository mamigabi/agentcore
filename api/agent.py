import os
from typing import List, Dict, Any
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from langchain.agents import AgentExecutor, create_react_agent
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory
from .tools import agent_tools
from .database import SupabaseHistory
from dotenv import load_dotenv

load_dotenv()

class AgentCore:
    def __init__(self):
        self.history_db = SupabaseHistory()
        
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
        
        self.llm = main_model.with_fallbacks([fallback_model])
        
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
        self.agent = create_react_agent(self.llm, agent_tools, self.prompt)
        
    def get_executor(self, session_id: str):
        history_data = self.history_db.get_history(session_id)
        
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
            verbose=True,
            handle_parsing_errors=True
        )

    def run(self, session_id: str, message: str) -> str:
        semantic_context = self.history_db.search_semantic_memory(message)
        context_str = ""
        if semantic_context:
            try:
                context_str = "\n\nContexto Semántico Relevante:\n" + "\n".join([f"- {item.get('content')}" for item in semantic_context if isinstance(item, dict) and item.get('content')])
            except Exception as e:
                print(f"Error procesando memoria semantica: {e}")
                
        enhanced_message = message + context_str

        self.history_db.add_message(session_id, "user", message)
        
        executor = self.get_executor(session_id)
        try:
            response = executor.invoke({"input": enhanced_message})
            answer = response["output"]
            
            self.history_db.add_message(session_id, "assistant", answer)
            return answer
        except Exception as e:
            error_msg = f"Agent Error: {str(e)}"
            self.history_db.add_message(session_id, "assistant", error_msg)
            return error_msg

    def run_autonomy(self, objective: str) -> str:
        memory = ConversationBufferMemory(memory_key="chat_history", return_messages=False)
        executor = AgentExecutor(
            agent=self.agent,
            tools=agent_tools,
            memory=memory,
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=15
        )
        
        prompt = f"Tu objetivo principal como agente autónomo es: {objective}. Debes pensar y ejecutar paso a paso hasta que lo logres. Usa las herramientas necesarias."
        self.history_db.add_message("autonomy", "system", f"Empezando autonomía: {objective}")
        
        try:
            response = executor.invoke({"input": prompt})
            answer = response["output"]
            self.history_db.add_message("autonomy", "system", f"Autonomía finalizada: {answer}")
            return answer
        except Exception as e:
            error_msg = f"Autonomy Error: {str(e)}"
            self.history_db.add_message("autonomy", "system", error_msg)
            return error_msg
