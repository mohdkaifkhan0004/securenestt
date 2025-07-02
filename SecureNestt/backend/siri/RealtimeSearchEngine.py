from googlesearch import search
from groq import Groq
from json import load, dump
import datetime
import os
from dotenv import dotenv_values
import time


# Load environment variables
env_vars = dotenv_values(".env")
username = env_vars.get("username")
Assistant = env_vars.get("Assistantname")
GroqAPIKey = env_vars.get("GroqAPIKey")

# Initialize client
client = Groq(api_key=GroqAPIKey)

# Proper system prompt
System = f"""Hello, I am {username}, You are a very accurate and advanced AI chatbot named {Assistant}, which has real-time up-to-date information from the internet.
*** Provide Answers In a Professional Way, make sure to add full stops, commas, question marks, and use proper grammar.***
*** Just answer the question from the provided data in a professional way. ***"""

# Create folder if not exists
os.makedirs("Data", exist_ok=True)

# Load existing chat history if available
chatlog_path = "Data/ChatLog.json"
try:
    with open(chatlog_path, "r") as f:
        message = load(f)
except (FileNotFoundError, ValueError):
    message = []
    with open(chatlog_path, "w") as f:
        dump([], f)


def googlesearch(query):
    try:
        results = list(search(query, num_results=5, advanced=True))
        answer = f"The search results for '{query}' are:\n[start]\n"
        
        for i in results:
            answer += f"{i}\n"
        answer += "[end]"
        return answer
    except Exception as e:
        return f"Error performing Google search: {str(e)}"


# Clean answer formatting
def AnswerModifier(answer):
    lines = answer.split("\n")
    non_empty_lines = [line for line in lines if line.strip()]
    return "\n".join(non_empty_lines)


# Function to get real-time information
def information():
    data = ""
    current_data_time = datetime.datetime.now()
    day = current_data_time.strftime("%A")
    date = current_data_time.strftime("%d")
    month = current_data_time.strftime("%B")
    year = current_data_time.strftime("%Y")
    hour = current_data_time.strftime("%H")
    minute = current_data_time.strftime("%M")
    second = current_data_time.strftime("%S")
    data += f"use this real-time information if needed:\n"
    data += f"today is {day}, {date} of {month}, {year}, the time is {hour}:{minute}:{second}.\n"
    return data


# Function to handle real-time search and chatbot interaction
def realtimesearch(Query):
    global message
    
    # Append user query to the chat history
    message.append({"role": "user", "content": Query})

    # Fetch Google search results and append them to the system prompt
    search_results = googlesearch(Query)
    message.append({"role": "system", "content": search_results})

    # Get current real-time information
    realtime_info = information()

    # Perform completion using Groq API
    try:
        completion = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[{"role": "system", "content": System}] + message + [{"role": "system", "content": realtime_info}],
            temperature=0.7,
            max_tokens=1024,
            top_p=1,
            stream=True,
            stop=None
        )

        answer = ""
        for chunk in completion:
            if chunk.choices[0].delta.content:
                answer += chunk.choices[0].delta.content

        answer = answer.strip().replace("</s>", "")
        message.append({"role": "assistant", "content": answer})

        # Save updated chat history
        with open(chatlog_path, "w") as f:
            dump(message, f, indent=4)

        return AnswerModifier(answer)

    except Exception as e:
        print(f"Error: {str(e)}")
        return "Sorry, something went wrong."


if __name__ == "__main__":
    print("Chatbot is ready! Type 'exit' or 'quit' to stop.")
    
    while True:
        user_input = input(">>> ")
        if user_input.lower() in ["exit", "quit"]:
            print("Exiting the chatbot.")
            break
        print(realtimesearch(user_input))
