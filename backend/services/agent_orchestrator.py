from typing import TypedDict, Annotated
import operator
from langgraph.graph import StateGraph, END
from langchain_aws import ChatBedrock
from langchain_core.prompts import ChatPromptTemplate
from services.graph_service import GraphService

class AgentState(TypedDict):
    messages: Annotated[list, operator.add]
    next_agent: str
    context: dict

class AgentOrchestrator:
    def __init__(self, graph_service: GraphService):
        self.graph_service = graph_service
        
        # FIX: Swapped OpenAI for Amazon Bedrock
        # This uses the IAM Role permissions we verified earlier.
        self.llm = ChatBedrock(
            model_id="anthropic.claude-3-sonnet-20240229-v1:0",
            region_name="us-east-1",
            model_kwargs={"temperature": 0.7}
        )
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
        # Ensure we handle list of messages correctly
        last_message = state["messages"][-1]
        msg_text = last_message.lower() if isinstance(last_message, str) else last_message.content.lower()
        
        if any(word in msg_text for word in ["why", "explain", "how"]):
            return {"next_agent": "tutor"}
        elif any(word in msg_text for word in ["fix", "debug", "run"]):
            return {"next_agent": "debugger"}
        else:
            return {"next_agent": "tutor"}
    
    async def _tutor_node(self, state: AgentState):
        """RAG-enabled tutoring agent"""
        last_message = state["messages"][-1]
        msg_text = last_message if isinstance(last_message, str) else last_message.content
        
        # Extract function name (simplified)
        words = msg_text.split()
        function_name = next((word[:-2] for word in words if word.endswith("()")), None)
        
        context = []
        if function_name:
            context = await self.graph_service.query_context(function_name)
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a patient tutor helping developers learn codebases.
Use the Scaffolding pattern:
1. Observation: What do you notice in the code?
2. Concept: What programming concept is relevant?
3. Action: What could you try next?

Never give the direct answer. Guide with questions.

Context from knowledge graph:
{context}"""),
            ("user", "{message}")
        ])
        
        chain = prompt | self.llm
        result = await chain.ainvoke({
            "message": msg_text,
            "context": str(context)
        })
        
        return {"messages": [result]}

    async def _debugger_node(self, state: AgentState):
        """Debugging agent"""
        last_message = state["messages"][-1]
        msg_text = last_message if isinstance(last_message, str) else last_message.content
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You help debug code by analyzing errors and suggesting fixes."),
            ("user", "{message}")
        ])
        
        chain = prompt | self.llm
        result = await chain.ainvoke({"message": msg_text})
        
        return {"messages": [result]}

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
        # LangGraph returns a list of messages; we want the content of the last one
        last_output = result["messages"][-1]
        return last_output.content if hasattr(last_output, 'content') else str(last_output)
