# Trendly AI Support Assistant

An AI-powered, agentic customer support assistant built for **Trendly** using **LangChain**, **FastAPI**, **Google Gemini Function Calling**, **Groq Fallback**, and **MongoDB Atlas Vector Search (RAG)** with deterministic return pipelines and JWT-based authentication.

---

## 🔐 Login Credentials

You can sign in using any of the following accounts:

### 1. Administrative & Support Roles
| Role | Email Address | Access Level / Description |
|---|---|---|
| **Admin** | `admin@trendly.com` | Full system & administrative access |
| **Support Agent** | `agent@trendly.com` | Human support agent dashboard access |

### 2. Customer Accounts (With Preloaded Test Orders)
| Customer Name | Email Address | Customer ID | Preloaded Test Scenarios |
|---|---|---|---|
| **Marcus Bell** | `marcus.bell@example.com` | `C-101` | • Order `TR-4522`: Delivered within 30 days (Cotton Tee & Socks)<br>• Order `TR-4524`: Delivered High-Value Headphones (₹14,999) |
| **Ananya Rao** | `ananya.rao@example.com` | `C-100` | • Order `TR-4521`: Active shipment in transit via BlueDart (`BD8871209341`) |
| **Priya Nair** | `priya.nair@example.com` | `C-102` | • Order `TR-4523`: Delivered Jewellery / Earrings (Non-returnable category test) |
| **Diego Ramos** | `diego.ramos@example.com` | `C-103` | • Order `TR-4525`: Cancelled order<br>• Order `TR-4526`: Lost in transit (Lost parcel claim escalation) |

---

## ⚙️ How It Works (System Workflow)

```
                       React + Vite + Tailwind Frontend
                                      │
                                (JWT Bearer)
                                      │
                       FastAPI Backend (/chat endpoint)
                                      │
                   LangChain Agent Orchestration Loop
                                      │
                 ┌────────────────────┴────────────────────┐
                 │                                         │
        Google Gemini 2.5 Flash              Groq LLaMA 3.3 70B
         (Primary Model + Tools)          (Rate Limit / Quota Fallback)
                 │                                         │
                 └────────────────────┬────────────────────┘
                                      │
      ┌──────────────────┬────────────┴───────┬──────────────────┐
      │                  │                    │                  │
  Order Tool       Policy RAG Tool      Support Tool       Return Flow
(get_order)       (search_policy)     (create_ticket)    (create_return)
      │                  │                    │                  │
 MongoDB /      MongoDB Vector Search     Generated        Multi-step Return
orders.json     + Local Policy RAG        Ticket ID         Pipeline & Approval
```

### 1. User Authentication & Customer Isolation
- When a user signs in, the FastAPI backend verifies the credentials and returns a signed **JWT token** containing the subject (email) and role.
- Every chat request passes this token in the `Authorization: Bearer <token>` header.
- The backend decodes the token and resolves the `customer_id` via `get_customer_id_by_email()`, ensuring complete tenant isolation between customer conversations.

### 2. LangChain Agent Orchestrator
- The backend orchestrates conversations using **LangChain** (`langchain`, `langchain-core`, `langchain-google-genai`, `langchain-groq`).
- Tools are declared using LangChain's `@tool` decorator with strict Pydantic argument schemas (`args_schema`).
- **Dynamic Tool Calling**: The agent dynamically reasons about which tool to call based on the customer's intent:
  - Order status / tracking → `get_order`
  - Policy questions (shipping, returns, refunds, cancellations) → `search_policy`
  - Human escalation / lost parcels / disputes → `create_support_ticket`
  - Processing returns & exchanges → `create_return`
- **Fallback Resilience**: If Gemini hits rate limits or quota exhaustion (`429 / RESOURCE_EXHAUSTED`), the system seamlessly switches to **Groq (`llama-3.3-70b-versatile`)** without dropping the session.

### 3. Retrieval-Augmented Generation (RAG)
- Official policies from `trendly_policy.md` are indexed in MongoDB Atlas Vector Search (`policy_chunks` collection) with embeddings generated via `models/text-embedding-004`.
- A resilient fallback pipeline performs section-aware chunk search locally if vector search is unavailable or offline, preventing server errors while strictly enforcing anti-hallucination policies.

### 4. Deterministic Multi-Step Return Pipeline
When a return is requested, `create_return` runs a 5-step automated workflow:
1. **Find Order**: Looks up the order with retry logic (up to 3 attempts on timeout).
2. **Policy Verification**: Checks the 30-day delivery window.
3. **Category Eligibility**: Enforces non-returnable categories (jewellery, socks, innerwear, beauty, gift cards) and final-sale rules.
4. **Refund Computation**: Calculates refundable totals and deductions (e.g. missing footwear box).
5. **High-Value Approval Threshold**: Any refund exceeding **₹20,000** automatically marks `requiresApproval: true` and flags it for human agent review.

### 5. Persistent Chat Memory
- Chat histories are isolated and persisted per user in `src/data/chat_history.json` and MongoDB, converting LangChain `HumanMessage` and `AIMessage` objects for display and multi-turn context retention.

---

## 🛠️ Tech Stack

### Frontend
- **React 19**
- **Vite**
- **Tailwind CSS v4**
- **Axios**
- **React Markdown**

### Backend
- **Python 3.10+**
- **FastAPI & Uvicorn**
- **LangChain** (`langchain`, `langchain-core`, `langchain-google-genai`, `langchain-groq`)
- **PyJWT & Passlib / Bcrypt**
- **MongoDB Atlas & Motor**
- **Pydantic v2**

---

## 🚀 Running Locally

### 1. Backend Setup

1. Navigate to the `backend` directory:
   ```bash
   cd backend
   ```

2. Create and activate a Python virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install backend dependencies:
   ```bash
   pip install -r requirements.txt pyjwt "passlib[bcrypt]"
   ```

4. Configure environment variables in `backend/.env`:
   ```env
   PORT=8081
   JWT_SECRET=supersecretkey
   JWT_ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=60
   GEMINI_API_KEY=your_google_gemini_api_key
   GEMINI_MODEL=gemini-2.5-flash
   GROQ_API_KEY=your_groq_api_key
   GROQ_MODEL=llama-3.3-70b-versatile
   MONGODB_URI=your_mongodb_atlas_connection_string
   ```

5. (Optional) Seed data:
   ```bash
   python3 -m src.scripts.import_data
   python3 -m src.scripts.embed_policy
   ```

6. Start the FastAPI server:
   ```bash
   python3 -m src.main
   ```
   *Runs on `http://localhost:8081` (Interactive API docs at `http://localhost:8081/docs`).*

---

### 2. Frontend Setup

1. Open another terminal and navigate to `frontend`:
   ```bash
   cd frontend
   ```

2. Install npm packages:
   ```bash
   npm install
   ```

3. Configure `frontend/.env`:
   ```env
   VITE_API_URL=http://localhost:8081
   ```

4. Start the frontend:
   ```bash
   npm run dev
   ```
   *Runs on `http://localhost:5173`.*

---

## 🧪 Demo Scenarios to Test

1. **Policy Grounding & Anti-Hallucination**:
   - *"What is your return policy?"* → Grounded in 30-day delivery window and conditions.
   - *"Can I return jewellery?"* → Strictly refuses based on hygiene and safety policy.
   - *"Can I get a discount code?"* → Confirms no promotions or discounts are offered in the official policy.
2. **Order Status & Follow-up Multi-Turn Context**:
   - *"Where is my order TR-4521?"* → Retrieves live status and BlueDart tracking number.
   - *"When will it arrive?"* → Responds based on previous context without re-asking for order ID.
3. **Deterministic Returns & Escalations**:
   - *"I want to return TR-4522"* → Checks items, calculates refund, creates return record.
   - *"My package TR-4526 never arrived"* → Detects lost in transit status and creates a support ticket (`SUP-XXXX`).