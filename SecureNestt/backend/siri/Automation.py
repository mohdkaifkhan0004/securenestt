from webbrowser import open as webopen
# from pywhatkit import search, playonyt
from dotenv import dotenv_values
from bs4 import BeautifulSoup
from rich import print
from groq import Groq
import subprocess

import platform
import os
import requests
import asyncio

# Load environment variables
env_vars = dotenv_values("backend/.env")
GroqAPIKey = env_vars.get("GroqAPIKey")

# Set up Groq client
client = Groq(api_key=GroqAPIKey)

# Optional: Classes used for parsing (can be used later for scraping)
classes = [
    "zCubwf", "hgKElc", "LTKOO SY7ric", "ZOLcW", "gsrt vk_bk FzvW5b YwPhnf", "pclqee",
    "tw-Data-text tw-text-small tw-ta", "IZ6rdc", "05uR6d LTKOO", "vlzY6d",
    "webanswers-webanswers_table_webanswers-table", "dDoNo ikb4Bb gsrt", "sXLa0e",
    "LWkfKe", "VQF4g", "qv3Wpe", "kno-rdesc", "SPZz6b"
]

user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.142.86 Safari/537.36"

# AI Chat setup
message = []
username = os.environ.get("username", "Assistant")

systemChatBot = [
    {
        "role": "system",
        "content": f"Hello, I am {username}. You're a content writer. You have to write high-quality content on the given topic."
    }
]

professional_response = [
    "Your satisfaction is my top priority; feel free to reach out if there's anything else I can help you with.",
    "I'm at your service for any additional questions or support you may need — don't hesitate to ask."
]


messages = []

# Function to perform a Google search
def GoogleSearch(topic):
    url = f"https://www.google.com/search?q={topic}"
    webopen(url)
    return True

def application(topic):
    def OpenNotepad(file_path):
        subprocess.Popen(["notepad.exe", file_path])

    def content_writer_ai(prompt):
        # Update the prompt for generating better leave applications
        refined_prompt = f"Generate a formal leave application for a student. The application should include the following details: Student's name, class, school name, number of leave days, leave dates, reason for leave, and request for approval."
        message.append({"role": "user", "content": refined_prompt})

        completion = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=systemChatBot + message,
            temperature=0.7,
            max_tokens=1024,
            top_p=1,
            stream=True
        )

        answer = ""
        for chunk in completion:
            if chunk.choices[0].delta.content:
                answer += chunk.choices[0].delta.content

        answer = answer.replace("</s>", "")
        message.append({"role": "assistant", "content": answer})
        return answer

    clean_topic = topic.lower().replace("content", "").strip()
    generated_application = content_writer_ai(clean_topic)

    # Save to file
    filepath = f"Data/{clean_topic.replace(' ', '_')}.txt"
    os.makedirs("Data", exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as file:
        file.write(generated_application)

    # Open in Notepad
    OpenNotepad(filepath)

    return True

def letter(topic):
    def OpenNotepad(file_path):
        subprocess.Popen(["notepad.exe", file_path])

    def content_writer_ai(prompt):
        message.append({"role": "user", "content": prompt})

        completion = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=systemChatBot + message,
            temperature=0.7,
            max_tokens=1024,
            top_p=1,
            stream=True
        )

        answer = ""
        for chunk in completion:
            if chunk.choices[0].delta.content:
                answer += chunk.choices[0].delta.content

        answer = answer.replace("</s>", "")
        message.append({"role": "assistant", "content": answer})
        return answer

    clean_topic = topic.lower().replace("content", "").strip()
    generated_letter = content_writer_ai(clean_topic)

    # Save to file
    filepath = f"Data/{clean_topic.replace(' ', '_')}.txt"
    os.makedirs("Data", exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as file:
        file.write(generated_letter)

    # Open in Notepad
    OpenNotepad(filepath)

    return True

# Content generator function
def content(topic):
    def OpenNotepad(file_path):
        subprocess.Popen(["notepad.exe", file_path])

    def content_writer_ai(prompt):
        message.append({"role": "user", "content": prompt})

        completion = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=systemChatBot + message,
            temperature=0.7,
            max_tokens=1024,
            top_p=1,
            stream=True
        )

        answer = ""
        for chunk in completion:
            if chunk.choices[0].delta.content:
                answer += chunk.choices[0].delta.content

        answer = answer.replace("</s>", "")
        message.append({"role": "assistant", "content": answer})
        return answer

    clean_topic = topic.lower().replace("content", "").strip()
    generated_content = content_writer_ai(clean_topic)

    # Save to file
    filepath = f"Data/{clean_topic.replace(' ', '_')}.txt"
    os.makedirs("Data", exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as file:
        file.write(generated_content)

    # Open in Notepad
    OpenNotepad(filepath)

    return True

def youtubesearch(topic):
    url = f"https://www.youtube.com/results?search_query={topic}"
    webopen(url)
    return True

def playyoutube(topic):
    url = f"https://www.youtube.com/results?search_query={topic}"
    webopen(url)
    return True


def openapp(app, sess=requests.session()):
    try:
        appopen(app, match_closest=True, output=True, throw_error=True)
        return True
    except Exception as e:
        print(f"Failed to open app: {app} — {e}")
        # Fallback to Google search
        query = f"https://www.google.com/search?q={app}"
        webopen(query)
        return False
def closeapp(app):
    if "chrome" in app:
        # Placeholder: you can define chrome-specific logic here if needed
        return False
    try:
        close(app, match_closest=True, output=True, throw_error=True)
        return True
    except:
        return False


def system(command):
    if command == "mute":
        print("System is muted.")
    elif command == "unmute":
        print("System is unmuted.")
    else:
        print(f"Unknown system command: {command}")

async def translateandexecute(commands: list[str]):
    func = []
    for command in commands:
        print(f"Processing command: {command}")  # Debugging print
        if command.startswith("open"):
            if "open it" in command or command == "open file":
                pass
            else:
                fun = asyncio.to_thread(openapp, command.removeprefix("open").strip())
                func.append(fun)

        elif command.startswith("general"):
            pass

        elif command.startswith("realtime"):
            pass

        elif command.startswith("close"):
            fun = asyncio.to_thread(closeapp, command.removeprefix("close").strip())
            func.append(fun)

        elif command.startswith("play"):
            fun = asyncio.to_thread(playyoutube, command.removeprefix("play").strip())
            func.append(fun)

        elif command.startswith("content"):
            fun = asyncio.to_thread(content, command.removeprefix("content").strip())
            func.append(fun)
        elif command.startswith("application"):
            fun = asyncio.to_thread(application, command.removeprefix("application").strip())
            func.append(fun)
        elif command.startswith("letter"):
            fun = asyncio.to_thread(letter, command.removeprefix("letter").strip())
            func.append(fun)    

        elif command.startswith("googlesearch"):
            fun = asyncio.to_thread(GoogleSearch, command.removeprefix("googlesearch").strip())
            func.append(fun)

        elif command.startswith("system"):
            fun = asyncio.to_thread(system, command.removeprefix("system").strip())
            func.append(fun)

        else:
            print(f"No function found for command: {command}")

    results = await asyncio.gather(*func)

    for result in results:
        if isinstance(result, str):
            yield result
        else:
            yield str(result)

# Wrap the generator consumption inside a coroutine.
async def execute_commands():
    user_input = input(">>> ").strip()  # Capture user input from the console
    commands = [user_input]  # Put input in a list, since translateandexecute expects a list of commands.
    async for result in translateandexecute(commands):
        print(result)


if platform.system() == "Windows":
    from AppOpener import open as appopen, close
else:
    def appopen(*args, **kwargs):
        print("AppOpener not supported on non-Windows.")
    def close(*args, **kwargs):
        print("AppOpener not supported on non-Windows.")

if __name__ == "__main__":
    while True:
         asyncio.run(execute_commands())
