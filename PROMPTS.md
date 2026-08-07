# Prompt Engineering

## Objective

The goal of this project was to build an AI customer support assistant that provides accurate, policy-grounded responses while dynamically using tools for order retrieval, policy lookup, and support ticket creation.

During development, the prompts were refined through multiple iterations to improve response quality, reduce hallucinations, and make conversations feel more natural.

---

# Iteration 1 – Basic Assistant

### Initial Prompt

The assistant was initially instructed to behave as a customer support chatbot and answer customer queries.

### Problems Observed

- Responses were too verbose.
- Generated Markdown formatting such as **bold** and bullet lists.
- Sometimes answered policy questions from its own knowledge instead of using the policy database.
- Occasionally invented information.

### Improvement

The prompt was updated to keep responses shorter and rely more on tool outputs.

---

# Iteration 2 – Tool Usage

### Problem

Gemini sometimes answered directly without calling the appropriate tool.

For example:

- Return policy questions
- Shipping policy
- Refund eligibility

### Improvement

The tool descriptions were rewritten to clearly specify when each tool should be used.

For example:

- Order Tool → Customer order information
- Policy Tool → Company policies
- Support Ticket Tool → Manual escalation

This resulted in much more consistent function calling.

---

# Iteration 3 – Reducing Hallucinations

### Problem

When asked questions like:

> Can I get a discount?

The assistant generated responses about:

- Newsletters
- Coupons
- Promotions

Even though none of these existed in the official Trendly policy.

### Improvement

The prompt was updated with instructions such as:

- Always use the Policy Tool for policy-related questions.
- Never invent company policies.
- If information is unavailable, clearly state that it is not present in the official policy.

This significantly reduced hallucinations.

---

# Iteration 4 – Conversation Style

### Problem

Responses looked like documentation instead of a real customer support chat.

Example:

- Long paragraphs
- Markdown formatting
- Excessive explanations

### Improvement

Formatting instructions were added:

- Do NOT use Markdown.
- Respond in plain text.
- Keep responses short.
- Use conversational language.
- Use short paragraphs.

This produced a cleaner chat experience.

---

# Iteration 5 – Support Ticket Handling

### Problem

When a customer requested an action that was not allowed by policy, the assistant simply refused the request.

Example:

Customer:

> Create the return anyway.

Assistant:

> I can't do that.

### Improvement

The Support Ticket Tool description was refined to instruct Gemini to escalate appropriate cases instead of ending the conversation.

The assistant now creates a support ticket whenever manual review is appropriate.

---

# Iteration 6 – Return Eligibility

### Problem

The assistant initially relied only on policy text to determine return eligibility.

### Improvement

The Order Tool was enhanced to calculate return eligibility dynamically using the current date and the order's delivery date.

This ensured accurate responses instead of relying on fixed dates.

---

# Final Prompt Design

The final system prompt focuses on:

- Acting as a helpful customer support assistant.
- Using tools whenever additional information is required.
- Answering policy questions only using retrieved company policies.
- Keeping responses concise and conversational.
- Avoiding Markdown formatting.
- Avoiding hallucinations.
- Escalating to human support when appropriate.

---

# Key Learnings

Through prompt iteration, I learned that:

- Well-written tool descriptions are just as important as the system prompt.
- RAG significantly reduces hallucinations for company-specific policies.
- Small formatting instructions greatly improve the user experience.
- Clear escalation rules help the assistant handle edge cases more naturally.
- Iterative prompt refinement leads to more reliable and predictable AI behavior.