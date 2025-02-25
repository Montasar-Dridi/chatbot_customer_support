import os
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
from mistralai import Mistral, UserMessage

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Get API key from environment variable
api_key = os.getenv("MISTRAL_API_KEY")
if not api_key:
    api_key = "34YFdh8pzEEUdvMEVD4pxfFrmpLf4oMt"  # Fallback to the key from your notebook
    os.environ["MISTRAL_API_KEY"] = api_key

def mistral_chat(user_message, model="mistral-large-latest"):
    """Function to interact with Mistral AI"""
    client = Mistral(api_key=api_key)
    messages = [
        UserMessage(content=user_message),
    ]
    chat_response = client.chat.complete(
        model=model,
        messages=messages,
    )
    # Return the response content
    return chat_response.choices[0].message.content

# Add a root route for a welcome page
@app.route('/')
def index():
    html = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Customer Support Chatbot API</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }
            h1 { color: #333; }
            .container { max-width: 800px; margin: 0 auto; }
            code { background: #f4f4f4; padding: 2px 5px; border-radius: 3px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Customer Support Chatbot API</h1>
            <p>Welcome to the Customer Support Chatbot API powered by Mistral AI.</p>
            <h2>How to use the API:</h2>
            <p>Send a POST request to <code>/api/chat</code> with the following JSON structure:</p>
            <pre><code>
{
  "message": "Your question here"
}
            </code></pre>
            <h2>Testing the API:</h2>
            <p>You can test the API using curl:</p>
            <pre><code>
curl -X POST http://localhost:5000/api/chat \\
  -H "Content-Type: application/json" \\
  -d '{"message":"What are your business hours?"}'
            </code></pre>
            <h2>Streamlit Frontend</h2>
            <p>To use the chatbot with a nice UI, run the Streamlit frontend:</p>
            <pre><code>streamlit run streamlit_app.py</code></pre>
        </div>
    </body>
    </html>
    '''
    return render_template_string(html)

# Add a simple test endpoint
@app.route('/test', methods=['GET'])
def test():
    return jsonify({"status": "API is working!"})

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('message', '')
    if not user_message:
        return jsonify({"error": "No message provided"}), 400
    
    # This is where we would add the system prompt for customer support
    prompt = f"""
    You are a helpful customer support chatbot. Your task is to assist users with their questions
    and concerns in a friendly, professional manner. If you don't know the answer to a question,
    please say so honestly and suggest that the user contact a human representative.
    
    User query: {user_message}
    """
    
    response = mistral_chat(prompt)
    # Return the response to the client
    return jsonify({"response": response})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 