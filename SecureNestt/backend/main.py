# backend/main.py
# ai chatbot
from fastapi import FastAPI
from pydantic import BaseModel
import asyncio
import json

import time
# from backend.siri.Model import FirstLayerDMM
# from backend.siri.Chatbot import ChatBot
# from backend.siri.RealtimeSearchEngine import realtimesearch
# from backend.siri.Automation import translateandexecute
# doorkeyz 

from backend.routes import support

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from typing import Dict
import uvicorn

from bson import ObjectId
from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends, Body
from fastapi.middleware.cors import CORSMiddleware
from jose import jwt, JWTError
from datetime import datetime, timedelta
from pydantic import BaseModel, EmailStr
from motor.motor_asyncio import AsyncIOMotorClient
import smtplib
from email.mime.text import MIMEText
from typing import List
from fastapi.security import OAuth2PasswordBearer
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from fastapi import FastAPI, WebSocket,WebSocketDisconnect

from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from motor.motor_asyncio import AsyncIOMotorClient
import os
from fastapi import FastAPI, Response, Request, Cookie
import signal
import sys
import uvicorn

from fastapi import APIRouter, Depends
from motor.motor_asyncio import AsyncIOMotorClient
from uuid import uuid4
from fastapi.responses import JSONResponse
from fastapi import FastAPI, Request, Query
from motor.motor_asyncio import AsyncIOMotorClient

import os


from fastapi import FastAPI
# App setup
app = FastAPI()


frontend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend"))
app.mount("/static", StaticFiles(directory=frontend_path), name="static")


# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ENV variables
SECRET = os.getenv("JWT_SECRET", "b6QX9zFJH1w7kVaYelLqZuPTrvNX8c0W")
ALGO = os.getenv("JWT_ALGORITHM", "HS256")
SMTP_USER = os.getenv("SMTP_USER","help.securenestt@gmail.com")
SMTP_PASS = os.getenv("SMTP_PASS","evsusrxbzpmfldup")



# MongoDB
mongo_client = AsyncIOMotorClient("mongodb://localhost:27017")
db = mongo_client["SecureNestt"]
users_collection = db["users"]
orders = db["card_orders"]
 

# Pydantic Models
class UserSignup(BaseModel):
    email: EmailStr
    password: str
    username: str
    flat_number: str = "N/A"
    full_address: str = "N/A"
# 
class UserLogin(BaseModel):
    email: EmailStr
    password: str

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str

class UserInfoUpdate(BaseModel):
    email: EmailStr
    username: str
    flat_number: str
    full_address: str
    emergency_num: str = ""

class CardOrder(BaseModel):
    name: str
    gender: str
    age: int
    phone: str
    email: str
    flat: str
    street: str
    landmark: str
    city: str
    state: str
    pincode: str
    plan: str
    price: str
    payment_status: str = "pending"


class PaymentStatusUpdate(BaseModel):
    order_id: str
    payment_status: str  # e.g. "success", "failed"

@app.get("/healthz")
def health():
    return {"status": "ok"}


def signal_handler(sig, frame):
    print('Gracefully exiting...')
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

def create_token(data: dict, expires_min=60):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=expires_min)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET, algorithm=ALGO)

def decode_token(token: str):
    return jwt.decode(token, SECRET, algorithms=[ALGO])

def send_email(to_email: str, subject: str, body: str):
    smtp_host = "smtp.gmail.com"
    smtp_port = 587

    msg = MIMEText(body, "html")
    msg["Subject"] = subject
    msg["From"] = SMTP_USER
    msg["To"] = to_email

    with smtplib.SMTP(smtp_host, smtp_port) as server:
        server.starttls()
        server.login(SMTP_USER, SMTP_PASS)
        server.send_message(msg)


def get_db():
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    return client["SecureNestt"]  # ya aapka DB naam


# Helper to get user by email
async def get_user(email: str):
    user = await users_collection.find_one({"email": email.lower()})
    return user

# Authenticate user (plain password compare)
async def authenticate_user(email: str, password: str):
    user = await get_user(email)
    if not user:
        return False
    if password != user["password"]:
        return False
    return user

# OAuth2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = decode_token(token)
        email = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid auth token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid auth token")

    user = await get_user(email)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# Routes

@app.post("/signup")
async def signup(user: UserSignup):
    email = user.email.lower()
    existing = await users_collection.find_one({"email": email})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    user_id = f"SecureNest-{uuid4().hex[:8]}"  # Shorter user_id

    new_user = {
        "user_id": user_id,
        "email": email,
        "password": user.password,  # Plain text password
        "username": user.username,
        "flat_number": user.flat_number,
        "plain_password": user.password,
        "full_address": user.full_address,
        "reset_token": None,
        "reset_token_expiry": None,
        }

    await users_collection.insert_one(new_user)
    return {"message": "Signup successful","user_id": user_id, "email": email}

@app.post("/login")
async def login(user: UserLogin):
    auth_user = await authenticate_user(user.email, user.password)
    if not auth_user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_token({"sub": user.email.lower()}, expires_min=60*24)
    return {"access_token": token, "token_type": "bearer"}


@app.post("/forgot-password")
async def forgot_password(request: ForgotPasswordRequest, background_tasks: BackgroundTasks):
    email = request.email.lower()
    user = await get_user(email)
    if not user:
        return {"message": "If the email exists, the password has been sent."}

    plain_password = user.get("plain_password", None)
    if not plain_password:
        plain_password = "Password not available (signup ke time par password field nahi tha)"

    body = f"""
    <p>Hi {user['username']},</p>
    <p>We received a request to retrieve your password for your SecureNestt account.</p>
    <p><strong>Your current password is:</strong> <code>{plain_password}</code></p>
    <p>If you didn't request this, please ignore this email. Your account remains secure.</p>
    <br>
    <p>Thanks,<br>The SecureNestt Team</p>
    """

    background_tasks.add_task(send_email, to_email=email, subject="Your SecureNestt Password", body=body)
    return {"message": "If the email exists, the password has been sent."}

@app.post("/reset-password")
async def reset_password(data: ResetPasswordRequest):
    try:
        payload = decode_token(data.token)
        email = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=400, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=400, detail="Invalid or expired token")

    user = await get_user(email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Update plain password as well
    await users_collection.update_one(
        {"email": email},
        {"$set": {"password": data.new_password, "plain_password": data.new_password}}
    )

    return {"message": "Password updated successfully"}

@app.post("/submit-info")
async def submit_info(info: UserInfoUpdate):
    result = await users_collection.update_one(
        {"email": info.email.lower()},
        {
            "$set": {
                "username": info.username,
                "flat_number": info.flat_number,
                "full_address": info.full_address,
                "emergency_num": info.emergency_num
            }
        },
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User info updated successfully"}

# ----------- USER INFO ENDPOINT (QR STATUS INCLUDED) -----------
@app.get("/userinfo")
async def user_info(current_user: dict = Depends(get_current_user)):
    return {
        "email": current_user["email"],
        "username": current_user["username"],
        "flat_number": current_user.get("flat_number", "N/A"),
        "full_address": current_user.get("full_address", "N/A"),
        "emergency_num": current_user.get("emergency_num", ""),
        "qr_active": current_user.get("qr_active", False),
        "user_id": current_user.get("user_id", f"SecureNest-{current_user['_id']}")    }

@app.get("/userinfo-by-email")
async def userinfo_by_email(email: str):
    user = await get_user(email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {
        "email": user.get("email", ""),
        "username": user.get("username", ""),
        "flat_number": user.get("flat_number", "N/A"),
        "full_address": user.get("full_address", "N/A"),
        "emergency_num": user.get("emergency_num", ""),
        "qr_active": user.get("qr_active", False)
    }


@app.post("/api/buy-card")
async def buy_card(order: CardOrder, db=Depends(get_db)):
    orders = db["card_orders"]
    order_dict = order.dict()
    order_dict["payment_status"] = "pending"
    result = await orders.insert_one(order_dict)
    return {"message": "Order received", "order_id": str(result.inserted_id)}




@app.post("/api/update-payment-status")
async def update_payment_status(data: PaymentStatusUpdate, db=Depends(get_db)):
    orders = db["card_orders"]
    result = await orders.update_one(
        {"_id": ObjectId(data.order_id)},
        {"$set": {"payment_status": data.payment_status}}
    )
    if result.modified_count:
        return {"message": "Payment status updated"}
    else:
        return {"message": "Order not found or status unchanged"}



# Add support router
app.include_router(support.router)



# MongoDB Dependency
# def get_db():
#     client = AsyncIOMotorClient("mongodb://localhost:27017")
#     return client["SecureNest"]  # Change to your DB name



@app.get("/api/get-call-link")
async def get_call_link(user_id: str, db=Depends(get_db)):
    users = db["users"]

    user = await users.find_one({"user_id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    room_id = user.get("room_id", str(uuid4()))

    await users.update_one(
        {"user_id": user_id},
        {"$set": {"room_id": room_id}},
        upsert=True
    )

    # Only uid param for QR/visitor.html
    link = f"http://127.0.0.1:5500/frontend/visitor.html?uid={user_id}"
    return {"link": link}
from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict

# Store connected clients
active_users: Dict[str, WebSocket] = {}
active_visitors: Dict[str, WebSocket] = {}
active_connections: Dict[str, WebSocket] = {}
# ...existing code...
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    user_id = None
    visitor_id = None

    try:
        while True:
            data = await websocket.receive_json()
            print("Received:", data)

            if data.get("role") == "user":
                user_id = data.get("user_id")
                active_connections[user_id] = websocket
                print(f"User connected: {user_id}")
                print("Active connections:", active_connections.keys())
            
            elif data.get("role") == "visitor":
                visitor_id = data.get("visitor_id")
                active_connections[visitor_id] = websocket
                print(f"Visitor connected: {visitor_id}")
                print("Active connections:", active_connections.keys())
            elif data.get("type") == "call_request":
                target = data.get("target_user")
                if target in active_connections:
                    await active_connections[target].send_json(data)
                    print(f"Forwarded call to user: {target}")
                else:
                    print(f"User {target} not connected")
 
            elif data.get("type") == "call_response":
                target = data.get("target_user")  # visitor_id
                if target in active_connections:
                    await active_connections[target].send_json(data)
                    print(f"Forwarded call_response to visitor: {target}")
                else:
                    print(f"Visitor {target} not connected")

            # --- ADD THIS BLOCK ---
            elif data.get("type") == "offer":
                target = data.get("target_user")
                if target in active_connections:
                    await active_connections[target].send_json(data)
                    print(f"Forwarded offer to user: {target}")
                else:
                    print(f"User {target} not connected for offer")

            elif data.get("type") in ("answer", "ice"):
                target = data.get("target_user")
                if target in active_connections:
                    await active_connections[target].send_json(data)

    except WebSocketDisconnect:
        print(f"Client disconnected: {user_id or visitor_id}")

        if user_id and user_id in active_connections:
            del active_connections[user_id]
        if visitor_id and visitor_id in active_connections:
            del active_connections[visitor_id]
    except WebSocketDisconnect:
        print(f"Client disconnected: {user_id or visitor_id}")
        if user_id and user_id in active_connections:
            del active_connections[user_id]
        if visitor_id and visitor_id in active_connections:
            del active_connections[visitor_id]

            
# CHAT_HISTORY_FILE = "chat_history.json"

# # Ensure history file exists
# if not os.path.exists(CHAT_HISTORY_FILE):
#     with open(CHAT_HISTORY_FILE, "w") as f:
#         json.dump([], f)

# class UserRequest(BaseModel):
#     message: str

# async def save_history(history):
#     with open(CHAT_HISTORY_FILE, "w") as file:
#         json.dump(history, file)

# # Core response handler
# async def handle_user_input(user_input):
#     try:
#         classification = FirstLayerDMM(user_input)
#         print(f"[Classification] {classification}")
#         if not classification:
#             return "Sorry, I couldn't understand that."

#         first_tag = classification[0]

#         if first_tag.startswith("general"):
#             response = await asyncio.to_thread(ChatBot, user_input)
#             return response or "No relevant response found."

#         elif first_tag.startswith("realtime"):
#             response = await asyncio.to_thread(realtimesearch, user_input)
#             return response

#         else:
#             response = ""
#             async for res in translateandexecute([user_input]):
#                 response += f"{res}\n"
#             return response.strip()

#     except Exception as e:
#         return f"Error: {str(e)}"

# @app.post("/chat")
# async def chat_endpoint(user_request: UserRequest):
#     user_input = user_request.message
#     print(f"[Request Received] {user_input}")
#     start = time.time()

#     result = await handle_user_input(user_input)

#     duration = time.time() - start
#     print(f"[Response Time] {duration:.2f} seconds")

#     # Load chat history
#     try:
#         with open(CHAT_HISTORY_FILE, "r") as file:
#             chat_history = json.load(file)
#     except (json.JSONDecodeError, FileNotFoundError):
#         chat_history = []

#     chat_history.append({"user": True, "text": user_input})
#     chat_history.append({"user": False, "text": result})

#     # Save chat history without blocking response
#     asyncio.create_task(save_history(chat_history))

#     return {"response": result}

# @app.get("/get_chat_history")
# async def get_chat_history():
#     try:
#         with open(CHAT_HISTORY_FILE, "r") as file:
#             chat_history = json.load(file)
#     except (json.JSONDecodeError, FileNotFoundError):
#         chat_history = []
#     return {"chat_history": chat_history}

# @app.post("/clear_chat_history")
# async def clear_chat_history():
#     if os.path.exists(CHAT_HISTORY_FILE):
#         os.remove(CHAT_HISTORY_FILE)
#     return {"status": "Chat history cleared"}


















