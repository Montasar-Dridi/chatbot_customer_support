import streamlit as st
import os
from mistralai import Mistral, UserMessage
from dotenv import load_dotenv

# Load environment variables from .env file if available
load_dotenv()

# Set page configuration
st.set_page_config(
    page_title="Customer Support Chatbot",
    page_icon="💬",
    layout="centered"
)

# Get API key from environment variable or Streamlit secrets
def get_api_key():
    # First try to get from streamlit secrets
    if hasattr(st.secrets, "MISTRAL_API_KEY"):
        return st.secrets.MISTRAL_API_KEY
    # Then try to get from environment variables
    api_key = os.getenv("MISTRAL_API_KEY")
    if not api_key:
        st.error("Mistral API key not found. Please set it in Streamlit secrets or as an environment variable.")
    return api_key

# Function to interact with Mistral AI
def mistral_chat(user_message, model="mistral-large-latest"):
    """Function to interact with Mistral AI"""
    api_key = get_api_key()
    if not api_key:
        return "Error: API key not configured. Please contact the administrator."
    
    client = Mistral(api_key=api_key)
    
    # Add customer support system prompt
    prompt = f"""
    You are a helpful customer support chatbot. Your task is to assist users with their questions
    and concerns in a friendly, professional manner. If you don't know the answer to a question,
    please say so honestly and suggest that the user contact a human representative.
    
    User query: {user_message}
    """
    
    messages = [
        UserMessage(content=prompt),
    ]
    
    try:
        chat_response = client.chat.complete(
            model=model,
            messages=messages,
        )
        return chat_response.choices[0].message.content
    except Exception as e:
        return f"Error communicating with Mistral AI: {str(e)}"

# Initialize session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display header
st.title("Customer Support Chatbot 💬")
st.subheader("Powered by Mistral AI")

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("How can I help you today?"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Display assistant thinking indicator
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("Thinking...")
        
        # Get response directly from Mistral AI
        ai_response = mistral_chat(prompt)
        
        message_placeholder.markdown(ai_response)
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": ai_response}) 