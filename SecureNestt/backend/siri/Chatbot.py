from groq import Groq
from json import load, dump
import os
import datetime
import time
from dotenv import dotenv_values

env_vars = dotenv_values(".env")

# Load environment variables
username = env_vars.get("username")
Assistant = env_vars.get("Assistantname")
GroqAPIKey = env_vars.get("GroqAPIKey")

# Initialize client
client = Groq(api_key=GroqAPIKey)

message = []

# Proper system prompt
System = f"""Hello, I am {username}, You are a very accurate and advanced AI chatbot named {Assistant} which also has real-time up-to-date information from the internet.
*** Do not tell time until I ask, do not talk too much, just answer the question.***
*** Reply in only English, even if the question is in Hindi, reply in English.***
*** Do not provide notes in the output, just answer the question and never mention your training data. ***
"""

# System message list
systemChatBot = [
    {"role": "system", "content": System}
]

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
        dump(message, f, indent=4)

# Clean answer formatting
def AnswerModifier(answer):
    lines = answer.split("\n")
    non_empty_lines = [line for line in lines if line.strip()]
    return "\n".join(non_empty_lines)

def information():
    data=""
    current_data_time=datetime.datetime.now()
    day=current_data_time.strftime("%A")
    date=current_data_time.strftime("%d")
    month=current_data_time.strftime("%B")
    year=current_data_time.strftime("%Y")
    hour=current_data_time.strftime("%H")
    minute=current_data_time.strftime("%M")
    second=current_data_time.strftime("%S")
    data+=f"use this real-time information if needed:\n"
    data+=f"today is {day}, {date} of {month}, {year}, the time is {hour}:{minute}:{second}.\n"
    return data

# Function to handle retry mechanism for rate limits
def handle_rate_limit():
    while True:
        try:
            return True
        except Exception as e:
            if "Rate limit reached" in str(e):
                print("Rate limit exceeded. Waiting before retrying...")
                time.sleep(120)  # wait for 2 minutes before retrying
            else:
                raise e

# Main chatbot function
def ChatBot(Query):
    message.append({"role": "user", "content": Query})
    message.append({"role": "user", "content": information()})

    try:
        completion = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=systemChatBot + message,
            temperature=0.5,
            max_tokens=1024,
            top_p=1,
            stream=True,
            stop=None
        )

        answer = ""
        for chunk in completion:
            if chunk.choices[0].delta.content:
                answer += chunk.choices[0].delta.content

        answer = answer.replace("<s>", "")
        message.append({"role": "assistant", "content": answer})

        # Save chat history
        with open(chatlog_path, "w") as f:
            dump(message, f, indent=4)

        return AnswerModifier(answer)

    except Exception as e:
        if "Rate limit reached" in str(e):
            handle_rate_limit()  # Retry if rate limit is exceeded
            return ChatBot(Query)
        else:
            print(f"Error: {str(e)}")
            return "Sorry, something went wrong."

if __name__ == "__main__":
    while True:
        user_input = input(">>> ")
        print(ChatBot(user_input))
