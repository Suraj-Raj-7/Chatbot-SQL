# AI-Powered SQL Chatbot 🤖

A conversational AI-powered chatbot that allows you to interact with a MySQL database using natural language. This project leverages the power of Google's Gemini 1.5 Flash model through LangChain to translate your questions into SQL queries, fetch the results, and provide answers in a human-friendly format.

![Chatbot Interface Screenshot](https://placehold.co/800x400/1e1e1e/e0e0e0?text=Chatbot+UI+Screenshot)

---

## ✨ Features

* **Natural Language to SQL:** Ask complex questions about your data in plain English.
* **Conversation Context:** Remembers previous parts of the conversation to answer follow-up questions accurately.
* **Secure & Read-Only:** Includes a security layer to **block** any SQL commands that could modify or delete data (`UPDATE`, `DELETE`, `INSERT`, `DROP`, etc.), ensuring your database remains safe.
* **User-Friendly Interface:** A clean and simple web interface for a smooth conversational experience.
* **Easy Setup:** Connects to your MySQL database with minimal configuration.
* **Powered by Gemini 1.5 Flash:** Utilizes Google's powerful and efficient language model for high-quality SQL generation.

---

## ⚙️ How It Works

The application follows a simple but powerful architecture to process user requests.

```
+-----------------+      +-----------------+      +---------------------+      +-----------------+      +-----------------+
|   User (Web     |----->|   Flask Backend |----->|   LangChain         |----->|   Gemini 1.5    |----->|   SQL Database  |
|   Interface)    |      |   (app.py)      |      |   (LLM Chain)       |      |   Flash (LLM)   |      |   (MySQL)       |
+-----------------+      +-----------------+      +---------------------+      +-----------------+      +-----------------+
        ^                                                                                                      |
        |                                                                                                      |
        +------------------------------------------------------------------------------------------------------+
                                     (Natural Language Response)
```

1.  **User Input**: The user types a question in the web interface.
2.  **Flask Backend**: The Flask server receives the question.
3.  **LangChain**: LangChain constructs a detailed prompt containing the user's question, conversation history, and the database schema.
4.  **Gemini LLM**: The prompt is sent to the Gemini 1.5 Flash model, which generates the appropriate SQL query.
5.  **Security Check**: The backend validates the generated SQL to ensure it's a read-only query.
6.  **Database Query**: The safe SQL query is executed against the MySQL database.
7.  **Final Response**: The query result is sent back to the LLM to generate a natural language response, which is then displayed to the user.

---

## 🛠️ Technologies Used

| Category      | Technology                                                                                                  |
| ------------- | ----------------------------------------------------------------------------------------------------------- |
| **Backend** | [Python](https://www.python.org/), [Flask](https://flask.palletsprojects.com/)                               |
| **LLM Orchestration** | [LangChain](https://www.langchain.com/)                                                                     |
| **Language Model** | [Google Gemini 1.5 Flash](https://deepmind.google/technologies/gemini/flash/)                               |
| **Database** | [MySQL](https://www.mysql.com/), [SQLAlchemy](https://www.sqlalchemy.org/)                                  |
| **Frontend** | HTML, CSS, JavaScript                                                                                       |

--- 

**Example Questions:**
* "How many artists are there?"
* "Which 3 artists have the most tracks?"
* "Who is the artist for the album 'Let There Be Rock'?"

---

