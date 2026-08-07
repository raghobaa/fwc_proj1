# Solution Note

# Overview

Trendly AI Support Assistant is an AI-powered customer support system built for an e-commerce platform. It combines Google Gemini Function Calling with MongoDB Atlas Vector Search (RAG) to answer customer queries related to orders, returns, shipping, refunds, and company policies.

Instead of relying on predefined workflows, the assistant dynamically selects the required tools based on the customer's request. This makes the system flexible, extensible, and capable of handling multi-step conversations naturally.

---

# Architecture

The application follows an agent-based architecture.

```
                 React + Tailwind Frontend
                        │
                     Axios
                        │
                Express Backend
                 (/chat endpoint)
                        │
                Agent Orchestrator
                        │
          Google Gemini (Function Calling)
                        │
      ┌──────────────┬───────────────┬
      │              │               │
 Order Tool     Policy RAG Tool   Support Tool
      │              │               │
 orders.json   MongoDB Atlas     Ticket Generator
```

---

# Components

## Frontend

**Technology**

- React
- Tailwind CSS
- Axios

**Responsibilities**

- Customer selection
- Chat interface
- Display AI responses
- Maintain chat history

---

## Backend

**Technology**

- Node.js
- Express

**Responsibilities**

- Receive chat requests
- Maintain customer chat sessions
- Coordinate Gemini requests
- Execute tools
- Return the final response

---

# Agent Orchestrator

The Agent Orchestrator is the core component of the application.

It acts as the bridge between Google Gemini and the available tools.

Instead of hardcoding workflows, the orchestrator lets Gemini decide which tool is required for each customer request.

The execution flow is:

1. The customer's message is sent to Gemini.
2. Gemini analyzes the request.
3. If additional information is required, Gemini returns a function call instead of a text response.
4. The orchestrator identifies the requested tool.
5. The tool is executed.
6. The tool result is sent back to Gemini.
7. Gemini either:
   - requests another tool, or
   - generates the final response.
8. The response is returned to the frontend.

This loop continues until Gemini has enough information to answer the customer.

Because of this design, the assistant can dynamically combine multiple tools without predefined decision trees.

---

# Available Tools

## 1. Order Tool

Purpose

Retrieve customer order information.

Used for

- Order tracking
- Delivery status
- Return eligibility
- Order details

Data Source

- Local `orders.json`

---

## 2. Policy Tool

Purpose

Retrieve the relevant company policy.

Used for

- Returns
- Refunds
- Exchanges
- Shipping
- Lost parcels
- Cancellation
- Address changes

Data Source

- MongoDB Atlas Vector Search

This tool enables Retrieval-Augmented Generation (RAG), ensuring responses are grounded in official company documentation.

---

## 3. Support Ticket Tool

Purpose

Escalate requests requiring manual intervention.

Triggered when

- Customer requests a human agent
- Lost parcel
- Damaged item
- Payment dispute
- Manual review required
- Customer insists after policy rejection

Output

- Support Ticket ID

---

# Conversation Memory

Each customer has an independent chat session.

This enables the assistant to understand follow-up questions such as:

- "Can I return it?"
- "How long do I have?"
- "Create the return."

without asking for the order ID again.

Customer conversations remain isolated, preventing context leakage between different users.

---

# Key Design Decisions

## Why Google Gemini Function Calling?

Instead of writing separate workflows for every customer scenario, Gemini decides which tool is required based on the customer's request.

This makes the system:

- Easier to extend
- More maintainable
- Capable of multi-step reasoning

---

## Why RAG?

Company-specific policies should always come from official documentation rather than the language model's internal knowledge.

MongoDB Atlas Vector Search retrieves the most relevant policy before Gemini generates the response.

This significantly reduces hallucinations.

---

## Why an Agent Orchestrator?

The orchestrator separates business logic from the language model.

Its responsibilities are:

- Execute requested tools
- Return tool results
- Maintain conversation flow
- Manage customer chat sessions

This makes adding new tools straightforward without changing the overall architecture.

---

## Why Conversation Memory?

Maintaining customer-specific chat sessions creates a more natural user experience by avoiding repeated questions for information already shared.

---

# Trade-offs

## Local Order Dataset

Order information is stored in a local JSON file for simplicity.

In production, this would be replaced with an Order Management System or database.

---

## Simulated Authentication

Customer identity is selected through a dropdown.

A production system would use authenticated customer accounts.

---

## Simulated Support Tickets

Support tickets are generated locally.

A production implementation would integrate with systems such as Zendesk, Freshdesk, or Salesforce.

---

# Known Limitations

- Order data is stored locally rather than in a production database.
- Customer authentication is simulated.
- Support tickets are mock-generated instead of being created in a real ticketing platform.
- The assistant relies on Gemini API availability, so response times may vary during periods of high demand.

---

# Discovery Questions

Before implementing this system in production, I would ask:

1. What is the source of truth for customer orders?
2. Which support platform should tickets be created in?
3. What authentication and authorization mechanism should be used?
4. Which company policies are updated frequently, and how should they be synchronized?
5. Are there response time SLAs or escalation rules that the assistant should follow?
6. Should customer conversations be persisted across devices and sessions?
7. Are there compliance or data privacy requirements for storing customer conversations?