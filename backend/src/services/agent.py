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
        
    class CreateReturnInput(BaseModel):
        orderId: str = Field(description="Order ID like TR-4522.")
        reason: str = Field(description="The customer's reason for the return.")
        
    @tool("create_return", args_schema=CreateReturnInput)
    async def create_return_tool(orderId: str, reason: str) -> dict:
        """Process a return request for an order the customer wants to return.
        
This tool runs the full return pipeline: it plans the steps, looks up the order
(retrying up to 3 times on timeout), checks the official return policy, verifies
eligibility (30-day window, non-returnable categories, final sale items), reflects
on the decision, computes the refund, and creates the return record.
If the refund amount exceeds the approval threshold (Rs. 20,000), the return is
submitted for human approval instead of being processed automatically.

Use this tool whenever the customer asks to return or exchange an item, wants a
refund, or asks "can I return" an order. Do NOT use it for general policy questions."""
        from src.services.return_flow import process_return_request
        return await process_return_request(orderId, customer_id, reason)
        
    return [get_order_tool, search_policy_tool, create_support_ticket_tool, create_return_tool]

def create_tools_for_admin(admin_email: str):
    from src.tools.admin_tool import (
        get_pending_returns,
        get_all_returns,
        approve_return_by_id,
        reject_return_by_id
    )
    from src.tools.order_tool import get_order
    from src.tools.policy_tool import search_policy

    class ListPendingReturnsInput(BaseModel):
        filter_high_value: Optional[bool] = Field(default=False, description="Set to true to only view high-value returns above Rs. 20,000.")

    @tool("list_pending_returns", args_schema=ListPendingReturnsInput)
    def list_pending_returns_tool(filter_high_value: bool = False) -> dict:
        """List all returns that are currently pending human/admin review and approval, especially high-value refunds (> Rs. 20,000)."""
        return get_pending_returns(filter_high_value=filter_high_value)

    class ListAllReturnsInput(BaseModel):
        status: Optional[str] = Field(default=None, description="Optional filter by status: PENDING_APPROVAL, APPROVED, REJECTED, RAISED.")

    @tool("list_all_returns", args_schema=ListAllReturnsInput)
    def list_all_returns_tool(status: Optional[str] = None) -> dict:
        """List all customer returns across the system, optionally filtered by status."""
        return get_all_returns(status=status)

    class ApproveReturnInput(BaseModel):
        returnId: str = Field(description="The return ID like RET-88201 to approve.")
        note: Optional[str] = Field(default=None, description="Optional admin note for approval.")

    @tool("approve_return", args_schema=ApproveReturnInput)
    def approve_return_tool(returnId: str, note: Optional[str] = None) -> dict:
        """Approve a pending return and authorize the refund."""
        return approve_return_by_id(returnId, admin_email=admin_email, note=note)

    class RejectReturnInput(BaseModel):
        returnId: str = Field(description="The return ID like RET-88201 to reject.")
        reason: str = Field(description="Reason for rejecting the return request.")

    @tool("reject_return", args_schema=RejectReturnInput)
    def reject_return_tool(returnId: str, reason: str = "Rejected by Admin") -> dict:
        """Reject a pending return request."""
        return reject_return_by_id(returnId, admin_email=admin_email, reason=reason)

    class GetAdminOrderInput(BaseModel):
        orderId: str = Field(description="Order ID like TR-4522 or TR-4524 to view.")

    @tool("get_order", args_schema=GetAdminOrderInput)
    def get_admin_order_tool(orderId: str) -> dict:
        """Retrieve full details for any order in the system."""
        return get_order(orderId, customer_id="ADMIN")

    class SearchPolicyInput(BaseModel):
        query: str = Field(description="Policy query.")

    @tool("search_policy", args_schema=SearchPolicyInput)
    async def search_policy_tool(query: str) -> dict:
        """Search company policies."""
        return await search_policy(query)

    return [
        list_pending_returns_tool,
        list_all_returns_tool,
        approve_return_tool,
        reject_return_tool,
        get_admin_order_tool,
        search_policy_tool
    ]

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
- Do not summarize away important identifiers returned by tools.

Return flow rules:
- Whenever the customer asks to return or exchange an item, or asks whether they can return an order, call the create_return tool with the order ID and the customer's reason.
- If create_return returns requiresApproval: true, tell the customer the return has been submitted and that a human agent will review it because the refund exceeds the approval threshold. Include the return ID.
- If create_return succeeds and no approval is needed, confirm the return is created, include the return ID, and state the refund amount and that it is processed after inspection.
- If create_return fails, clearly explain the reason (e.g. expired window, non-returnable category, final sale item, or order not found) using the issues returned by the tool."""

ADMIN_SYSTEM_INSTRUCTION = """You are Trendly's AI Administrative & Operations Assistant.

You are assisting an authorized administrator / support manager.

Your primary capabilities:
- Managing and approving customer returns, especially high-value refunds (> Rs. 20,000) that require human authorization.
- Checking pending returns and refund statuses using list_pending_returns and list_all_returns.
- Approving returns using approve_return and rejecting returns with reasons using reject_return.
- Inspecting any customer order in the system using get_order.
- Verifying company policies using search_policy.

Guidelines:
- When the admin asks whether there are returns left to approve or asks for pending returns, immediately call list_pending_returns. Clearly summarize each pending return with its Return ID, Order ID, Customer, Refund Amount (in Rs.), and Reason.
- Note which returns exceed the Rs. 20,000 threshold requiring manual sign-off.
- When instructed to approve or reject a return (e.g. "approve RET-88201" or "reject RET-91044"), call the corresponding tool and confirm the result clearly.
- Keep responses professional, clear, and action-oriented in plain text."""

# We will implement an orchestration loop similar to the JS version.
def _is_rate_limited(e: Exception) -> bool:
    msg = str(e).lower()
    return "429" in msg or "resource_exhausted" in msg or "quota" in msg or "rate limit" in msg

async def _invoke_with_fallback(primary, fallback, messages: list, state: dict):
    """Call Gemini first; switch to Groq fallback on any primary error / rate limit."""
    if state.get("use_fallback"):
        return await fallback.ainvoke(messages)
    try:
        return await primary.ainvoke(messages)
    except Exception as e:
        print(f"\n[LLM Orchestrator] Primary LLM failed ({e}), falling back to Groq: {str(e)[:120]}")
        state["use_fallback"] = True
        try:
            return await fallback.ainvoke(messages)
        except Exception as e_fb:
            print(f"\n[LLM Orchestrator] Fallback LLM failed as well ({e_fb})")
            raise e_fb


async def run_orchestrator(message: str, customer_id: str, chat_history: list, user_role: str = "customer", user_email: str = ""):
    from src.config.llm import get_llm, get_fallback_llm
    from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, ToolMessage
    
    llm = get_llm()
    fallback_llm = get_fallback_llm()
    
    is_admin = (user_role == "admin") or (user_email == "admin@trendly.com")
    
    if is_admin:
        tools = create_tools_for_admin(user_email or "admin@trendly.com")
        system_prompt = ADMIN_SYSTEM_INSTRUCTION
    else:
        tools = create_tools_for_customer(customer_id)
        system_prompt = SYSTEM_INSTRUCTION

    llm_with_tools = llm.bind_tools(tools)
    fallback_with_tools = fallback_llm.bind_tools(tools)
    state = {"use_fallback": False}
    
    # Construct conversation
    messages = [SystemMessage(content=system_prompt)] + chat_history
    messages.append(HumanMessage(content=message))
    
    while True:
        response = await _invoke_with_fallback(llm_with_tools, fallback_with_tools, messages, state)
        messages.append(response)
        
        if not response.tool_calls:
            # LLM finished reasoning. Ensure we return a plain string for the UI.
            if isinstance(response.content, str):
                reply = response.content
            elif isinstance(response.content, dict):
                reply = response.content.get("text") or response.content.get("answer") or str(response.content)
            elif isinstance(response.content, list):
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
                if tool_call["name"] in ["search_policy", "create_support_ticket", "create_return"]:
                    result = await tool_func.ainvoke(tool_call["args"])
                else:
                    result = tool_func.invoke(tool_call["args"])
                
                print(f"Tool Result: {result}")
                messages.append(ToolMessage(content=str(result), tool_call_id=tool_call["id"], name=tool_call["name"]))
            else:
                messages.append(ToolMessage(content="Tool not found.", tool_call_id=tool_call["id"], name=tool_call["name"]))

