import os
from langchain_google_genai import ChatGoogleGenerativeAI
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

def get_embeddings():
    from langchain_google_genai import GoogleGenerativeAIEmbeddings
    return GoogleGenerativeAIEmbeddings(
        model="models/gemini-embedding-2",
        google_api_key=os.getenv("GEMINI_API_KEY")
    )

