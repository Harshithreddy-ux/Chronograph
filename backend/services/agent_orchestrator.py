from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from services.graph_service import GraphService
import operator


class AgentState(TypedDict):
    messages: Annotated[list, operator.add]
    next_agent: str
    context: dict


class AgentOrchestrator:
    def __init__(self, graph_service: GraphService):
        self.graph_service = graph_service
        self.llm = ChatOpenAI(temperature=0.7, model="gpt-4")
        self.workflow = self._build_workflow()
    
    def _build_workflow(self):
        """Build LangGraph workflow"""
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("supervisor", self._supervisor_node)
        workflow.add_node("tutor", self._tutor_node)
        workflow.add_node("debugger", self._debugger_node)
        
        # Add edges
        workflow.add_conditional_edges(
            "supervisor",
            self._route_agent,
            {
                "tutor": "tutor",
                "debugger": "debugger",
                "end": END
            }
        )
        workflow.add_edge("tutor", END)
        workflow.add_edge("debugger", END)
        
        workflow.set_entry_point("supervisor")
        
        return workflow.compile()
    
    def _supervisor_node(self, state: AgentState):
        """Route to appropriate agent"""
        last_message = state["messages"][-1]
        
        # Simple routing logic
        if any(word in last_message.lower() for word in ["why", "explain", "how"]):
            return {"next_agent": "tutor"}
        elif any(word in last_message.lower() for word in ["fix", "debug", "run"]):
            return {"next_agent": "debugger"}
        else:
            return {"next_agent": "tutor"}
    
    async def _tutor_node(self, state: AgentState):
        """RAG-enabled tutoring agent"""
        last_message = state["messages"][-1]
        
        # Extract function name from message (simplified)
        words = last_message.split()
        function_name = None
        for word in words:
            if word.endswith("()"):
                function_name = word[:-2]
                break
        
        # Query graph for context
        context = []
        if function_name:
            context = await self.graph_service.query_context(function_name)
        
        # Scaffolding prompt pattern
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a patient tutor helping developers learn codebases.
Use the Scaffolding pattern:
1. Observation: What do you notice in the code?
2. Concept: What programming concept is relevant?
3. Action: What could you try next?

Never give the direct answer. Guide with questions.

Context from knowledge graph:
{context}
"""),
            ("user", "{message}")
        ])
        
        chain = prompt | self.llm
        result = await chain.ainvoke({
            "message": last_message,
            "context": str(context)
        })
        
        return {"messages": [result.content]}
    
    async def _debugger_node(self, state: AgentState):
        """Debugging agent"""
        last_message = state["messages"][-1]
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You help debug code by analyzing errors and suggesting fixes."),
            ("user", "{message}")
        ])
        
        chain = prompt | self.llm
        result = await chain.ainvoke({"message": last_message})
        
        return {"messages": [result.content]}
    
    def _route_agent(self, state: AgentState):
        """Determine next agent"""
        return state.get("next_agent", "end")
    
    async def process_message(self, message: str, session_id: str):
        """Process user message through agent workflow"""
        initial_state = {
            "messages": [message],
            "next_agent": "",
            "context": {}
        }
        
        result = await self.workflow.ainvoke(initial_state)
        return result["messages"][-1]
