import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from dotenv import load_dotenv

load_dotenv()

# We will instantiate the LLM here.
def get_llm():
    model_name = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")
    
    # Initialize the ChatGoogleGenerativeAI
    llm = ChatGoogleGenerativeAI(
        model=model_name,
        google_api_key=os.getenv("GEMINI_API_KEY"),
        temperature=0.0
    )
    return llm

def get_fallback_llm():
    """Groq-backed LLM used when Gemini hits rate limits / quota exhaustion."""
    load_dotenv(override=True)
    model_name = os.getenv("GROQ_MODEL", "qwen/qwen3.8-27b")
    if not model_name or "llama" in model_name.lower():
        model_name = "qwen/qwen3.8-27b"
    return ChatGroq(
        model=model_name,
        api_key=os.getenv("GROQ_API_KEY"),
        temperature=0.0,
    )



def get_embeddings():
    from langchain_google_genai import GoogleGenerativeAIEmbeddings
    model_name = os.getenv("GEMINI_EMBEDDING_MODEL", "models/text-embedding-004")
    return GoogleGenerativeAIEmbeddings(
        model=model_name,
        google_api_key=os.getenv("GEMINI_API_KEY")
    )


