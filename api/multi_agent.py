import os
from typing import Annotated, Dict, Sequence, TypedDict
import operator

from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, END
from .tools import agent_tools
from .database import SupabaseHistory
from dotenv import load_dotenv

load_dotenv()

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    next: str

def create_agent(llm, tools, system_prompt: str):
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        MessagesPlaceholder(variable_name="messages"),
    ])
    if tools:
        return prompt | llm.bind_tools(tools)
    return prompt | llm

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", google_api_key=os.environ.get("GEMINI_API_KEY"), temperature=0.2)

investigator_prompt = "Eres un Investigador Experto. Buscas información en internet y extraes datos de URLs usando tus herramientas."
investigator_agent = create_agent(llm, agent_tools, investigator_prompt)

def investigator_node(state: AgentState):
    result = investigator_agent.invoke({"messages": state["messages"]})
    return {"messages": [AIMessage(content=f"Investigador: {result.content}")]}

redactor_prompt = "Eres un Redactor Creativo. Creas contenido claro, artículos y textos estructurados basados en los datos recabados."
redactor_agent = create_agent(llm, [], redactor_prompt)

def redactor_node(state: AgentState):
    result = redactor_agent.invoke({"messages": state["messages"]})
    return {"messages": [AIMessage(content=f"Redactor: {result.content}")]}

analyst_prompt = "Eres un Analista de Datos. Revisas la información cruda, encuentras patrones, resúmenes estratégicos y organizas reportes analíticos."
analyst_agent = create_agent(llm, [], analyst_prompt)

def analyst_node(state: AgentState):
    result = analyst_agent.invoke({"messages": state["messages"]})
    return {"messages": [AIMessage(content=f"Analista: {result.content}")]}

publisher_prompt = "Eres el Publicador. Preparas el texto final para redes sociales o para guardarse de manera limpia."
publisher_agent = create_agent(llm, [], publisher_prompt)

def publisher_node(state: AgentState):
    result = publisher_agent.invoke({"messages": state["messages"]})
    return {"messages": [AIMessage(content=f"Publicador: {result.content}")]}

members = ["Investigator", "Redactor", "Analyst", "Publisher"]
options = ["FINISH"] + members

supervisor_prompt = ChatPromptTemplate.from_messages([
    ("system", "Eres el Manager de un equipo de IA. Los miembros son: {members}.\n"
               "Dada la solicitud del usuario, decide quién debe actuar a continuación.\n"
               "Cada miembro aportará avance. Cuando el objetivo esté cumplido y listo para entregarse, responde FINISH."),
    MessagesPlaceholder(variable_name="messages"),
    ("system", "Basado en la conversación, ¿quién debe actuar de forma consecutiva? O escribe FINISH si está listo. Responde sólo con una de estas opciones: {options}")
])

class Router(TypedDict):
    next: str

supervisor_chain = supervisor_prompt | llm.with_structured_output(Router)

def supervisor_node(state: AgentState):
    decision = supervisor_chain.invoke({"messages": state["messages"], "members": ", ".join(members), "options": ", ".join(options)})
    return {"next": decision["next"]}

builder = StateGraph(AgentState)
builder.add_node("supervisor", supervisor_node)
builder.add_node("Investigator", investigator_node)
builder.add_node("Redactor", redactor_node)
builder.add_node("Analyst", analyst_node)
builder.add_node("Publisher", publisher_node)

for member in members:
    builder.add_edge(member, "supervisor")

builder.set_entry_point("supervisor")

edges = {m: m for m in members}
edges["FINISH"] = END
builder.add_conditional_edges("supervisor", lambda state: state["next"], edges)

graph = builder.compile()

class MultiAgentManager:
    def __init__(self):
        self.graph = graph
        self.team_status = {
            "Manager": "Coordinando operaciones globales",
            "Investigator": "Listo (Tavily/Requests)",
            "Redactor": "Listo (Redacción AI)",
            "Analyst": "Listo (Síntesis de Datos)",
            "Publisher": "Listo (Formato Final)"
        }
        self.db = SupabaseHistory()

    def run_manager(self, objective: str, session_id: str = "manager_session") -> str:
        for k in self.team_status:
            if k != "Manager":
                self.team_status[k] = "En misión activa"
                
        initial_state = {"messages": [HumanMessage(content=objective)]}
        try:
            result = self.graph.invoke(initial_state, {"recursion_limit": 20})
            messages = result["messages"]
            final_content = messages[-1].content if messages else "Misión completada sin respuesta de texto final."
            
            self.db.add_message(session_id, "assistant", f"[Manager Final Report]: {final_content}")
            
            for k in self.team_status:
                if k != "Manager":
                    self.team_status[k] = "Listo - Misión Completada"
            return final_content
        except Exception as e:
            error_msg = f"Manager Error en LangGraph: {e}"
            for k in self.team_status:
                self.team_status[k] = "Error en última ejecución"
            return error_msg

    def get_team_status(self):
        return self.team_status
