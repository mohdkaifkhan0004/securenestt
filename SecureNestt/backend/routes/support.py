from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from email.message import EmailMessage
import smtplib
import os
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()

class SupportRequest(BaseModel):
    name: str
    email: EmailStr
    message: str

@router.post("/send-support-email")
async def send_support_email(data: SupportRequest):
    smtp_user = os.getenv("SMTP_USER", "help.securenestt@gmail.com")
    smtp_pass = os.getenv("SMTP_PASS", "evsusrxbzpmfldup")

    try:
        msg = EmailMessage()
        msg["Subject"] = f"[SecureNestt Support] Message from {data.name}"
        msg["From"] = smtp_user
        msg["To"] = smtp_user  # Send to yourself
        msg.set_content(f"""
        Name: {data.name}
        Email: {data.email}

        Message:
        {data.message}
        """)

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(smtp_user, smtp_pass)
            smtp.send_message(msg)

        return {"message": "Email sent successfully ✅"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

