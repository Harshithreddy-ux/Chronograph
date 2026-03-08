from typing import TypedDict, Annotated
import operator
from langgraph.graph import StateGraph, END
from services.graph_service import GraphService
import os

class AgentState(TypedDict):
    messages: Annotated[list, operator.add]
    next_agent: str
    context: dict

class AgentOrchestrator:
    def __init__(self, graph_service: GraphService, aws_service=None):
        self.graph_service = graph_service
        self.aws_service = aws_service
        
        # Try Gemini first (FREE!)
        gemini_key = os.getenv("GEMINI_API_KEY")
        
        if gemini_key and not gemini_key.startswith("your_"):
            try:
                from google import genai
                self.client = genai.Client(api_key=gemini_key)
                self.model = "gemini-flash-latest"  # Latest flash model with best performance
                self.use_ai = True
                print("✓ Using Google Gemini Flash (Latest) for AI")
            except Exception as e:
                print(f"⚠ Gemini error: {e}")
                self.use_ai = False
                self.client = None
        else:
            print("⚠ No AI configured. Add GEMINI_API_KEY to .env")
            print("⚠ Get FREE key at https://makersuite.google.com/app/apikey")
            self.use_ai = False
            self.client = None
        
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
        msg_text = last_message.lower() if isinstance(last_message, str) else last_message.content.lower()
        
        if any(word in msg_text for word in ["why", "explain", "how", "what"]):
            return {"next_agent": "tutor"}
        elif any(word in msg_text for word in ["fix", "debug", "run", "error"]):
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
        
        if not self.use_ai:
            return {"messages": ["⚠️ AI not configured. Get FREE Gemini API key at https://makersuite.google.com/app/apikey and add to .env as GEMINI_API_KEY"]}
        
        from google.genai import types
        
        system_prompt = """You are a friendly code tutor who has FULL knowledge of the user's codebase.

Your teaching style:
1. **Ask clarifying questions** before explaining everything
2. **Guide discovery** - help them understand step by step
3. **Be conversational** - like a helpful colleague, not a documentation bot
4. **Suggest next steps** - "Want me to explain X?" or "Should we look at Y?"

Use markdown formatting:
- **bold** for important terms
- *italic* for emphasis  
- `code` for inline code
- ## Headings for sections
- • Bullet points for lists

Example good response:
"I see this function validates `.jkr` files. **Quick question:** Are you trying to understand why it excludes `version.jkr` specifically, or how the validation works overall? 🤔"

Keep responses SHORT (3-5 sentences). Make it a conversation, not a lecture."""
        
        # Add context if available
        context_text = ""
        if context:
            context_text = f"\n\nCode context:\n{context}"
        
        contents = [
            types.Content(
                role="user",
                parts=[types.Part.from_text(text=msg_text + context_text)]
            )
        ]
        
        config = types.GenerateContentConfig(
            system_instruction=[types.Part.from_text(text=system_prompt)],
            temperature=0.7
        )
        
        response = self.client.models.generate_content(
            model=self.model,
            contents=contents,
            config=config
        )
        
        return {"messages": [response.text]}

    async def _debugger_node(self, state: AgentState):
        """Debugging agent"""
        last_message = state["messages"][-1]
        msg_text = last_message if isinstance(last_message, str) else last_message.content
        
        if not self.use_ai:
            return {"messages": ["⚠️ AI not configured. Get FREE Gemini API key at https://makersuite.google.com/app/apikey"]}
        
        from google.genai import types
        
        system_prompt = """You are a debugging expert who knows the full codebase.

Your approach:
1. **Ask what they're trying to fix** before suggesting solutions
2. **Narrow down the issue** with targeted questions
3. **Suggest specific fixes** with code examples
4. **Explain WHY** the bug happens

Keep it conversational and helpful. Guide them to the solution."""
        
        contents = [
            types.Content(
                role="user",
                parts=[types.Part.from_text(text=msg_text)]
            )
        ]
        
        config = types.GenerateContentConfig(
            system_instruction=[types.Part.from_text(text=system_prompt)],
            temperature=0.7
        )
        
        response = self.client.models.generate_content(
            model=self.model,
            contents=contents,
            config=config
        )
        
        return {"messages": [response.text]}

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
        last_output = result["messages"][-1]
        return str(last_output)
