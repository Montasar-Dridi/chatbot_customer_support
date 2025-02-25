import streamlit as st
import os
import json
from mistralai import Mistral, UserMessage
from dotenv import load_dotenv

# Load environment variables from .env file if available
load_dotenv()

# Set page configuration
st.set_page_config(
    page_title="Multi-Purpose AI Assistant",
    page_icon="🤖",
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
def mistral_chat(user_message, category, model="mistral-large-latest"):
    """Function to interact with Mistral AI"""
    api_key = get_api_key()
    if not api_key:
        return "Error: API key not configured. Please contact the administrator."
    
    client = Mistral(api_key=api_key)
    
    # Create appropriate prompt based on selected category
    if category == "Customer Support":
        prompt = f"""
        You are a helpful customer support chatbot. Your task is to assist users with their questions
        and concerns in a friendly, professional manner. If you don't know the answer to a question,
        please say so honestly and suggest that the user contact a human representative.
        
        User query: {user_message}
        """
    
    elif category == "Bank Inquiry Categorizer":
        prompt = f"""
        You are a bank customer service bot.
        Your task is to assess customer intent and categorize the customer inquiry into one of the following predefined categories:
        - card arrival
        - change pin
        - exchange rate
        - country support
        - cancel transfer
        - charge dispute

        If the text doesn't fit into any of the above categories, classify it as:
        - customer service

        You will respond with the predefined category first, and then provide a helpful response to the user's inquiry.
        
        User inquiry: {user_message}
        """
    
    elif category == "Medical Information Extractor":
        prompt = f"""
        Extract information from the following medical notes:
        {user_message}
        
        Return a well-formatted analysis with the following information if present:
        - Patient age
        - Patient gender
        - Diagnosis
        - Weight
        - Smoking status
        - Medications
        
        Present the information in a clear, organized format.
        """
    
    elif category == "Mortgage Advisor":
        prompt = f"""
        You are a mortgage lender customer service bot, and your task is to create personalized responses to address customer questions.
        
        Use the following facts in your response:
        - 30-year fixed-rate: interest rate 6.403%, APR 6.484%
        - 20-year fixed-rate: interest rate 6.329%, APR 6.429%
        - 15-year fixed-rate: interest rate 5.705%, APR 5.848%
        - 10-year fixed-rate: interest rate 5.500%, APR 5.720%
        - 7-year ARM: interest rate 7.011%, APR 7.660%
        - 5-year ARM: interest rate 6.880%, APR 7.754%
        - 3-year ARM: interest rate 6.125%, APR 7.204%
        - 30-year fixed-rate FHA: interest rate 5.527%, APR 6.316%
        - 30-year fixed-rate VA: interest rate 5.684%, APR 6.062%
        
        Customer inquiry: {user_message}
        """
    
    elif category == "Content Analyst":
        prompt = f"""
        You are a content analyst. Your task is to analyze the following text:
        
        {user_message}
        
        Please provide:
        1. A brief summary of the key points
        2. Three interesting questions about the content with your answers
        3. A comprehensive analysis of the content
        
        Format your response in a clear, well-organized manner.
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

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
    
if "category" not in st.session_state:
    st.session_state.category = "Customer Support"

# Display header
st.title("Multi-Purpose AI Assistant 🤖")
st.subheader("Powered by Mistral AI")

# Category selection
category_options = [
    "Customer Support", 
    "Bank Inquiry Categorizer", 
    "Medical Information Extractor", 
    "Mortgage Advisor", 
    "Content Analyst"
]

# Create a sidebar for category selection
with st.sidebar:
    st.title("Select Assistant Type")
    selected_category = st.radio(
        "Choose the type of assistant you need:",
        category_options,
        index=category_options.index(st.session_state.category)
    )
    
    # Display category description
    if selected_category == "Customer Support":
        st.info("A general-purpose customer support assistant that can help with a wide range of questions.")
    elif selected_category == "Bank Inquiry Categorizer":
        st.info("Categorizes banking inquiries and provides relevant information.")
    elif selected_category == "Medical Information Extractor":
        st.info("Extracts and organizes information from medical notes.")
    elif selected_category == "Mortgage Advisor":
        st.info("Provides information about mortgage rates and options.")
    elif selected_category == "Content Analyst":
        st.info("Analyzes content, generates questions, and provides comprehensive reports.")
    
    # Add a clear chat button
    if st.button("Clear Chat History"):
        st.session_state.messages = []
        st.session_state.category = selected_category
        st.experimental_rerun()

# If category has changed, clear the chat history
if selected_category != st.session_state.category:
    st.session_state.messages = []
    st.session_state.category = selected_category
    st.experimental_rerun()

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input(f"Ask the {st.session_state.category}..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Display assistant thinking indicator
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("Thinking...")
        
        # Get response directly from Mistral AI based on category
        ai_response = mistral_chat(prompt, st.session_state.category)
        
        message_placeholder.markdown(ai_response)
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": ai_response}) 