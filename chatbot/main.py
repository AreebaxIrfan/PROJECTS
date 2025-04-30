import streamlit as st
import google.generativeai as genai
import os
import json
from dotenv import load_dotenv

class ChatBot:
    def __init__(self, api_key):
        """Initialize the chatbot with Google Gemini API."""
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-pro')  # Use gemini-1.5-pro or another available model
        self.chat_history = []

    def get_response(self, user_input):
        """Generate a response using the Gemini model."""
        try:
            # Append user input to chat history
            self.chat_history.append({"role": "user", "content": user_input})
            
            # Prepare the conversation context
            conversation = "\n".join([f"{msg['role']}: {msg['content']}" for msg in self.chat_history])
            
            # Generate response
            response = self.model.generate_content(conversation)
            
            # Append bot response to chat history
            bot_response = response.text
            self.chat_history.append({"role": "bot", "content": bot_response})
            
            return bot_response
        except Exception as e:
            return f"Error: {str(e)}"

    def get_history(self):
        """Return the chat history."""
        return self.chat_history

class ChatInterface:
    def __init__(self, chatbot):
        """Initialize the Streamlit interface."""
        self.chatbot = chatbot
        self.history_file = "chat_history.json"  # For optional persistent history
        self.load_history()  # Load history from file (if exists)
        self.setup_ui()

    def load_history(self):
        """Load chat history from a file (optional)."""
        if os.path.exists(self.history_file):
            with open(self.history_file, "r") as f:
                st.session_state.history = json.load(f)
            # Sync AI context with loaded history
            self.chatbot.chat_history = st.session_state.history.copy()
        else:
            st.session_state.history = []

    def save_history(self):
        """Save chat history to a file (optional)."""
        with open(self.history_file, "w") as f:
            json.dump(st.session_state.history, f)

    def setup_ui(self):
        """Set up the Streamlit UI using native components."""
        # Set page config for a centered layout
        st.set_page_config(page_title="AI Chatbot", page_icon="🤖", layout="centered")

        # Title
        st.title("🤖 Amazing AI Chatbot")

        # Sidebar with clear history button
        with st.sidebar:
            if st.button("Clear Chat History"):
                st.session_state.history = []
                self.chatbot.chat_history = []
                if os.path.exists(self.history_file):
                    os.remove(self.history_file)
                st.rerun()

        # Create a container for chat messages
        chat_container = st.container()

        # Display chat history
        with chat_container:
            for message in st.session_state.history:
                with st.chat_message(message["role"], avatar="🧑" if message["role"] == "user" else "🤖"):
                    st.markdown(message["content"])

        # Chat input for user
        user_input = st.chat_input("Type your message here...")

        if user_input:
            # Append user message to history
            st.session_state.history.append({"role": "user", "content": user_input})
            
            # Display user message immediately
            with chat_container:
                with st.chat_message("user", avatar="🧑"):
                    st.markdown(user_input)
            
            # Get and display bot response
            with st.spinner("Thinking..."):
                response = self.chatbot.get_response(user_input)
                st.session_state.history.append({"role": "bot", "content": response})
                
                # Display bot message
                with chat_container:
                    with st.chat_message("assistant", avatar="🤖"):
                        st.markdown(response)
            
            # Save history to file (optional)
            self.save_history()

def main():
    # Load environment variables
    load_dotenv()
    
    # Retrieve the API key
    API_KEY = os.getenv("GEMINI_API_KEY")
    
    if not API_KEY:
        st.error("Error: GEMINI_API_KEY not found in .env file or environment variables.")
        return
    
    # Initialize chatbot and interface
    chatbot = ChatBot(API_KEY)
    interface = ChatInterface(chatbot)

if __name__ == "__main__":
    main()