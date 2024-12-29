
from groq import Groq

# Directly declare your API key here
api_key = "api_key_here"  # Replace with your Groq API key

# Create the Groq client using the API key
client = Groq(api_key=api_key)

# Set the system prompt
system_prompt = {
    "role": "system",
    "content": "You are a helpful assistant. You reply with very short answers."
}

# Initialize the chat history with the system prompt
chat_history = [system_prompt]

# Start the conversation loop
while True:
    # Get user input from the console
    user_input = input("You: ")

    # Check if user wants to exit the conversation
    if user_input.lower() == "exit":
        print("Goodbye!")
        break

    # Append the user input to the chat history
    chat_history.append({"role": "user", "content": user_input})

    # Get the response from the Groq API
    response = client.chat.completions.create(
        model="llama3-70b-8192",  # Replace with the model you are using if different
        messages=chat_history,
        max_tokens=100,
        temperature=1.2
    )

    # Get the assistant's message from the response
    assistant_message = response.choices[0].message.content

    # Append the assistant's response to the chat history
    chat_history.append({"role": "assistant", "content": assistant_message})

    # Print the assistant's response
    print("Assistant:", assistant_message)

