import os
import urllib.parse
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_community.utilities import SQLDatabase
from langchain_core.output_parsers import StrOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI

# Load environment variables from .env file
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Global variable to hold the database connection
db = None

# Initialize the MySQL Database connection
def init_database() -> SQLDatabase:
    """Initializes and returns an SQLDatabase instance using credentials from the .env file."""
    try:
        user = os.getenv("DB_USER")
        password = os.getenv("DB_PASSWORD")
        host = os.getenv("DB_HOST")
        port = os.getenv("DB_PORT")
        database = os.getenv("DB_DATABASE")
        
        # URL-encode the password to ensure special characters are handled
        encoded_password = urllib.parse.quote_plus(password or '')
        
        # Create the database URI
        db_uri = f"mysql+mysqlconnector://{user}:{encoded_password}@{host}:{port or '3306'}/{database}"
        
        return SQLDatabase.from_uri(db_uri)
    except Exception as e:
        print(f"Error initializing database: {e}")
        return None

# Generate SQL query using conversation context and schema
def get_sql_chain(db, gemini_api_key):
    """Creates a LangChain chain to generate a SQL query from a user's question."""
    template = """
        You are a data analyst at a company. You are interacting with a user who is asking you questions about the company's database.
        Based on the table schema below, write a SQL query that would answer the user's question. Take the conversation history into account.
        
        <SCHEMA>{schema}</SCHEMA>
        
        Conversation History: {chat_history}
        
        Write only the SQL query and nothing else. Do not wrap the SQL query in any other text, not even backticks.
        
        For example:
        Question: which 3 artists have the most tracks?
        SQL Query: SELECT ArtistId, COUNT(*) as track_count FROM Track GROUP BY ArtistId ORDER BY track_count DESC LIMIT 3;
        
        Question: Which artist has the most albums?
        SQL Query: SELECT T2.Name FROM album AS T1 JOIN artist AS T2 ON T1.ArtistId = T2.ArtistId GROUP BY T2.ArtistId ORDER BY COUNT(T1.AlbumId) DESC LIMIT 1;
        
        Question: Name 10 artists
        SQL Query: SELECT Name FROM Artist LIMIT 10;
        
        Your turn:
        
        Question: {question}
        SQL Query:
    """
    prompt = ChatPromptTemplate.from_template(template)
    
    # Initialize the Gemini LLM with the working model
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0, google_api_key=gemini_api_key)
    
    def get_schema(_):
        return db.get_table_info()
    
    return (
        RunnablePassthrough.assign(schema=get_schema)
        | prompt
        | llm
        | StrOutputParser()
    )

def get_sql_query_result(vars):
    """
    A helper function to get the SQL query from the chain's variables,
    print it for debugging purposes, and then run it against the database.
    """
    query = vars["query"]
    print("Generated SQL Query:", query)
    
    try:
        db_response = db.run(query)
        print("SQL Response:", db_response)
        return db_response
    except Exception as e:
        print(f"Error executing SQL query: {e}")
        return f"Error executing SQL query: {e}"

# Get the response from the SQL query
def get_response_chain(db, gemini_api_key):
    """Creates a LangChain chain to generate a natural language response from a SQL query result."""
    sql_chain = get_sql_chain(db, gemini_api_key)
    
    template = """
        You are a data analyst at a company. You are interacting with a user who is asking you questions about the company's database.
        Based on the table schema below, question, sql query, and sql response, write a natural language response.
        <SCHEMA>{schema}</SCHEMA>

        Conversation History: {chat_history}
        SQL Query: <SQL>{query}</SQL>
        User question: {question}
        SQL Response: {response}
    """
    prompt = ChatPromptTemplate.from_template(template)
    
    # Initialize the Gemini LLM with the working model
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0, google_api_key=gemini_api_key)
    
    chain = (
        RunnablePassthrough.assign(query=sql_chain).assign(
            schema=lambda _: db.get_table_info(),
            # Use the helper function to print the query and then execute it
            response=get_sql_query_result,
        )
        | prompt
        | llm
        | StrOutputParser()
    )
    
    return chain

# === Flask Routes ===
@app.route('/')
def home():
    """Serves the main HTML page for the chatbot."""
    return render_template('index.html')

@app.route('/connect', methods=['POST'])
def connect():
    """Endpoint to handle database connection."""
    global db
    db = init_database()
    if db:
        # Initial message for the chat history
        initial_message = "Hello! I'm a SQL assistant. Ask me anything about your database."
        return jsonify({"status": "success", "message": "Connected to database!", "initial_message": initial_message})
    else:
        return jsonify({"status": "error", "message": "Failed to connect to database."}), 500

@app.route('/chat', methods=['POST'])
def chat():
    """Endpoint to handle user chat messages and generate responses."""
    if db is None:
        return jsonify({"status": "error", "message": "Please connect to the database first."}), 400
    
    try:
        data = request.json
        user_query = data.get("message")
        chat_history_data = data.get("history", [])

        chat_history = []
        for msg in chat_history_data:
            if msg["sender"] == "user":
                chat_history.append(HumanMessage(content=msg["message"]))
            else:
                chat_history.append(AIMessage(content=msg["message"]))

        gemini_api_key = os.getenv("GEMINI_API_KEY")
        if not gemini_api_key:
            return jsonify({"status": "error", "message": "GEMINI_API_KEY not found in .env file."}), 500

        response_chain = get_response_chain(db, gemini_api_key)
        response = response_chain.invoke({
            "question": user_query,
            "chat_history": chat_history,
        })
        
        return jsonify({"status": "success", "message": response})
        
    except Exception as e:
        # Catch any unexpected errors and return a descriptive message
        print(f"An error occurred: {e}")
        return jsonify({"status": "error", "message": f"An internal server error occurred: {e}"}), 500

if __name__ == '__main__':
    app.run(debug=True)
