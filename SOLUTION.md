# Solution Note

## Overview

**Trendly AI Support Assistant** is an agentic customer support system designed for an e-commerce platform. It combines **LangChain**, **FastAPI**, **Google Gemini Function Calling**, **Groq Fallback**, and **MongoDB Atlas Vector Search (RAG)** to provide grounded, real-time customer support for orders, returns, shipping, refunds, and company policies.

Instead of hardcoded decision trees, the system uses an agentic tool-calling architecture: the language model reasons dynamically over customer intents and executes specific backend tools to complete multi-step tasks.

---

## Architecture

```
                 React + Vite + Tailwind Frontend
                               │
                         (JWT Bearer)
                               │
                        FastAPI Backend
                        (/chat endpoint)
                               │
               LangChain Agent Orchestration Loop
                               │
           ┌───────────────────┴───────────────────┐
           │                                       │
  Google Gemini 2.5 Flash            Groq LLaMA 3.3 70B
   (Primary Tool Calling)         (Rate-Limit / Quota Fallback)
           │                                       │
           └───────────────────┬───────────────────┘
                               │
   ┌───────────────┬───────────┴───────────┬───────────────┐
   │               │                       │               │
Order Tool    Policy RAG Tool         Support Tool    Return Flow Tool
(get_order)   (search_policy)        (create_ticket)  (create_return)
   │               │                       │               │
MongoDB /    MongoDB Atlas Vector      Support Ticket   Deterministic
orders.json  Search + Local Fallback     Generator      Multi-Step Flow
```

---

## System Components

### 1. Frontend
- **Framework**: React 19 + Vite + Tailwind CSS v4.
- **State & Auth**: Manages JWT authentication state, role storage (`customer`, `agent`, `admin`), message thread history, and interactive chat interface.
- **Client**: Axios instance with JWT Authorization Bearer interceptors.

### 2. Backend API
- **Framework**: Python 3.10+ with FastAPI and Uvicorn.
- **Authentication**: OAuth2 / JWT authentication (`HS256`) with role extraction and customer account resolution.
- **Data Stores**: MongoDB Atlas with local fallback (`orders.json`, `trendly_policy.md`, `chat_history.json`).

### 3. LangChain Agent Orchestrator
- **Tool Binding**: Tools are defined with `@tool` and explicit Pydantic input schemas (`args_schema`), bound to the model via `llm.bind_tools(tools)`.
- **Reasoning Loop**: Maintains a multi-turn reasoning loop executing requested tools until a final user-facing response is generated.
- **Quota & Rate-Limit Fallback**: Automatically falls back to **Groq (`llama-3.3-70b-versatile`)** when Gemini encounters rate limits or quota exhaustion (`429 / RESOURCE_EXHAUSTED`).

---

## Available Tools & Pipelines

### 1. Order Tool (`get_order`)
- Retrieves customer orders, item details, tracking numbers, shipping carriers, and delivered timestamps.
- Checks if the order belongs to the authenticated customer to prevent cross-account data leaks.

### 2. Policy RAG Tool (`search_policy`)
- Performs vector similarity search on MongoDB Atlas `policy_chunks` collection using `models/text-embedding-004`.
- **Resilient Fallback**: If vector search is offline or unavailable, automatically performs local section-level keyword and relevance retrieval over `trendly_policy.md`.
- Prevents hallucinations by strictly grounding policy answers on official policy documentation.

### 3. Support Ticket Tool (`create_support_ticket`)
- Automatically generates support ticket identifiers (`SUP-XXXX`) for human agent escalation (e.g. lost parcels, damaged products, manual reviews).

### 4. Return Flow Pipeline (`create_return`)
- Executes a deterministic, audited 5-step return pipeline:
  1. **Order Lookup**: Retries up to 3 times on timeout.
  2. **Window Validation**: Verifies delivery date within the 30-day calendar limit.
  3. **Non-Returnable Enforcement**: Rejects non-returnable categories (jewellery, socks, innerwear, beauty, gift cards).
  4. **Refund Calculation**: Evaluates final sale constraints and computes itemized refund totals.
  5. **Human Approval Threshold**: Any refund exceeding **₹20,000** is routed for human approval instead of auto-processing.

---

## Key Design Decisions

### Why LangChain & Function Calling?
Rather than hardcoding rigid conversational flows, LangChain provides a structured abstraction for tool binding, dynamic function calling, message typing, and multi-model fallbacks.

### Why RAG for Policies?
E-commerce policies are subject to precise rules (e.g. 30-day window, ₹300 deduction for missing shoe boxes, ₹250 delayed delivery credit). RAG guarantees that the LLM grounds its answers directly on verified policy text.

### Why Deterministic Code for Return Evaluation?
Financial and business logic (eligibility checks, non-returnable category lists, refund totals, approval thresholds) must be 100% predictable and audited. Wrapping deterministic code in a tool (`create_return`) provides both AI flexibility and business correctness.

---

## Trade-offs & Production Considerations

1. **Authentication**: Implemented via secure JWT tokens with email-based role resolution. In production, this can be linked to SSO / OAuth providers (Auth0, Okta, Firebase Auth).
2. **OMS Integration**: Orders are read from MongoDB Atlas with a local JSON fallback. In production, this connects to an enterprise OMS (Shopify, SAP, Salesforce Commerce).
3. **Ticketing System**: Returns and support tickets generate unique ticket IDs; in production, these integrate directly with Zendesk, Freshdesk, or Jira Service Management.