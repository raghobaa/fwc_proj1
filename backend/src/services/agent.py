from langchain_core.tools import tool
from typing import Optional
from pydantic import BaseModel, Field

# We will use Pydantic models for explicit schema definition
class GetOrderInput(BaseModel):
    orderId: str = Field(description="Order ID like TR-4522")

@tool("get_order", args_schema=GetOrderInput)
def get_order_tool(orderId: str) -> dict:
    """Retrieve an order belonging to the authenticated customer. Use this whenever the customer asks about order status, tracking, delivery, returns, exchanges, refunds, cancellations, or refers to a previously discussed order."""
    from src.tools.order_tool import get_order
    # Note: the customer_id will need to be injected or accessed from context.
    # In langchain, tool execution doesn't easily have access to request context out of the box unless passed or bound.
    # We will pass a dummy or inject it dynamically later.
    # Actually, we can use a class-based tool or a factory function to inject the customer_id.
    pass

def create_tools_for_customer(customer_id: str):
    
    @tool("get_order", args_schema=GetOrderInput)
    def get_order_tool(orderId: str) -> dict:
        """Retrieve an order belonging to the authenticated customer. Use this whenever the customer asks about order status, tracking, delivery, returns, exchanges, refunds, cancellations, or refers to a previously discussed order."""
        from src.tools.order_tool import get_order
        return get_order(orderId, customer_id)
        
    class SearchPolicyInput(BaseModel):
        query: str = Field(description="The customer's policy-related question.")
        
    @tool("search_policy", args_schema=SearchPolicyInput)
    async def search_policy_tool(query: str) -> dict:
        """Search the official Trendly policy knowledge base.
        
This tool is the ONLY source of truth for company policies.
Always use this tool whenever answering questions about returns, refunds, shipping, delivery delays, lost parcels, etc.
Do NOT answer policy questions from general knowledge.
If the tool does not return relevant policy information, do NOT invent an answer."""
        from src.tools.policy_tool import search_policy
        return await search_policy(query)
        
    class CreateSupportTicketInput(BaseModel):
        reason: str = Field(description="Short reason for creating the support ticket.")
        
    @tool("create_support_ticket", args_schema=CreateSupportTicketInput)
    async def create_support_ticket_tool(reason: str) -> dict:
        """Create a support ticket for a human support agent.
        
Use this tool ONLY when:
- Company policy explicitly requires human intervention.
- Manual review is required.
- Lost parcel, damaged item, payment dispute, etc.
Do NOT use this tool for general policy questions or tracking requests."""
        from src.tools.support_tool import create_support_ticket
        return await create_support_ticket(reason, customer_id)
        
    return [get_order_tool, search_policy_tool, create_support_ticket_tool]

SYSTEM_INSTRUCTION = """You are Trendly's AI customer support assistant.

Your primary goal is to resolve the customer's issue accurately using the available tools.

Guidelines:
- Keep responses concise (usually 2-4 sentences).
- Answer the customer's question directly.
- Do not repeat information already provided unless necessary.
- If the customer asks a follow-up question, continue naturally instead of restating previous answers.
- Sound like a professional customer support agent.

Formatting:
- Respond in plain text.
- Do NOT use Markdown.
- Do NOT use **bold**, *italic*, headings, or unnecessary bullet lists.
- Avoid phrases like "Here are the tracking details".
- Write naturally as if chatting with a customer.

Knowledge rules:
- The official Trendly policy is the ONLY source of truth for company policies.
- Never invent discounts, coupons, newsletters, promotions, price matching, goodwill credits, or offers that are not explicitly present in the policy.
- If the policy does not mention something, clearly state that the information is not available in the official policy.
- Do not answer company policy questions using general knowledge.

Tool response rules:
- When a support ticket is created, always include the ticket ID in your response.
- If a tool returns an order ID, tracking number, or support ticket number, never omit those identifiers.
- Do not summarize away important identifiers returned by tools."""

# We will implement an orchestration loop similar to the JS version.
async def run_orchestrator(message: str, customer_id: str, chat_history: list):
    from src.config.llm import get_llm
    from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, ToolMessage
    
    llm = get_llm()
    tools = create_tools_for_customer(customer_id)
    llm_with_tools = llm.bind_tools(tools)
    
    # Construct conversation
    messages = [SystemMessage(content=SYSTEM_INSTRUCTION)] + chat_history
    messages.append(HumanMessage(content=message))
    
    while True:
        response = await llm_with_tools.ainvoke(messages)
        messages.append(response)
        
        if not response.tool_calls:
            # LLM finished reasoning. Ensure we return a plain string for the UI.
            if isinstance(response.content, str):
                reply = response.content
            elif isinstance(response.content, dict):
                # Try common keys
                reply = response.content.get("text") or response.content.get("answer") or str(response.content)
            elif isinstance(response.content, list):
                # Assume list of message dicts; extract first text field
                first = response.content[0] if response.content else ""
                if isinstance(first, dict):
                    reply = first.get("text") or str(first)
                else:
                    reply = str(first)
            else:
                reply = str(response.content)
            return reply, messages
            
        # Execute tools
        for tool_call in response.tool_calls:
            print(f"\n==============================")
            print(f"Tool Selected: {tool_call['name']}")
            print(f"Arguments: {tool_call['args']}")
            
            tool_func = next((t for t in tools if t.name == tool_call["name"]), None)
            if tool_func:
                if tool_call["name"] in ["search_policy", "create_support_ticket"]:
                    result = await tool_func.ainvoke(tool_call["args"])
                else:
                    result = tool_func.invoke(tool_call["args"])
                
                print(f"Tool Result: {result}")
                messages.append(ToolMessage(content=str(result), tool_call_id=tool_call["id"], name=tool_call["name"]))
            else:
                messages.append(ToolMessage(content="Tool not found.", tool_call_id=tool_call["id"], name=tool_call["name"]))
