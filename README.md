# Trendly AI Support Assistant

An AI-powered customer support assistant built for Trendly that uses Google Gemini Function Calling and MongoDB Atlas Vector Search (RAG) to provide intelligent, context-aware customer support.

The assistant can dynamically retrieve order information, answer policy-related questions using official company documentation, and create support tickets whenever manual intervention is required.

---

## Demo

 **Demo Video:** **
 **Live Demo:** **

---

# Features

- AI-powered customer support using Google Gemini
- Dynamic Function Calling
- Retrieval-Augmented Generation (RAG)
- Customer-specific conversation memory
- Customer isolation between chat sessions
- Order tracking
- Return eligibility checks
- Company policy retrieval
- Automatic support ticket generation
- Reduced hallucinations using official company policies

---

# Architecture

![Architecture](architecture.png)

### Request Flow

```
React + Tailwind Frontend
          │
       Axios
          │
Express Backend (/chat)
          │
  Agent Orchestrator
          │
Google Gemini
(Function Calling)
          │
 ┌────────┼────────┐
 │        │        │
Order   Policy   Support
 Tool     Tool     Tool
 │         │        │
orders  MongoDB   Ticket
.json    Atlas    Generator
```

---

# Agent Orchestrator

The Agent Orchestrator is the core component of the application.

It connects Google Gemini with the available tools.

Whenever a customer sends a message, Gemini decides which tool is required based on the request. The orchestrator executes that tool, returns the result to Gemini, and continues this process until Gemini generates the final response.

This approach enables dynamic tool selection without hardcoded workflows.

---

# Available Tools

### Order Tool

Retrieves customer order information including:

- Order status
- Tracking details
- Delivery information
- Return eligibility

---

### Policy Tool

Searches the official Trendly policy stored in MongoDB Atlas Vector Search.

Used for answering questions related to:

- Returns
- Refunds
- Exchanges
- Shipping
- Lost parcels
- Cancellation

---

### Support Ticket Tool

Creates support tickets whenever:

- Manual review is required
- Customer requests a human agent
- Lost parcel
- Payment dispute
- Damaged item
- Customer insists after policy rejection

---

# Tech Stack

### Frontend

- React
- Tailwind CSS
- Axios

### Backend

- Node.js
- Express.js

### AI

- Google Gemini
- Gemini Function Calling

### Database

- MongoDB Atlas Vector Search

### Other

- REST APIs
- Git
- GitHub

---

# Project Structure

```
trendly-ai-support/
│
├── backend/
│   ├── config/
│   ├── controllers/
│   ├── services/
│   ├── tools/
│   └── data/
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── services/
│   │   └── assets/
│
├── README.md
├── SOLUTION.md
├── PROMPT_ENGINEERING.md
└── architecture.png
```

---

# Running Locally

## Clone the repository

```bash
git clone <repository-url>
cd trendly-agentic-support-v2
```

---

## Backend

```bash
cd backend
npm install
npm run dev
```

---

## Frontend

```bash
cd frontend
npm install
npm run dev
```

The frontend will run on:

```
http://localhost:5173
```

The backend will run on:

```
http://localhost:3000
```

---

# Environment Variables

## Backend (`backend/.env`)

```env
PORT=3000

GEMINI_API_KEY=

GEMINI_MODEL=

MONGODB_URI=
```

---

## Frontend (`frontend/.env`)

```env
VITE_API_URL=http://localhost:3000
```

---

# Key Capabilities

- Dynamic Function Calling
- Multi-tool reasoning
- Retrieval-Augmented Generation (RAG)
- Customer-specific conversation memory
- Customer isolation
- Automatic support ticket generation
- Hallucination reduction
- Policy-grounded responses

---

# Demo Scenarios

### Happy Path

- Track an order
- Check return eligibility
- Create a return request
- Generate a support ticket

### Edge Cases

- Return window expired
- Jewellery is non-returnable
- Final sale item
- Lost parcel
- Partial shipment
- Discount (hallucination prevention)

---

# Future Improvements

- Real customer authentication
- Production Order Management System integration
- Live support platform integration (Zendesk/Freshdesk)
- Streaming AI responses
- Retry logic and fallback models
- Conversation persistence
- Admin analytics dashboard

---

# Documentation

- **README.md** – Project overview and setup
- **SOLUTION.md** – Architecture, design decisions, trade-offs and limitations
- **PROMPT_ENGINEERING.md** – Prompt iterations and prompt engineering decisions

---

# Author

**Chandana KN**

Submission for the **Yellow.ai Forward Deployed Engineer Internship Assignment**.