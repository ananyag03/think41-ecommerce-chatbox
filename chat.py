# chat.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db import get_db
from models import Message, User
import requests
from groqconfig import GROQ_API_URL, GROQ_API_KEY

router = APIRouter()

@router.post("/chat")
def chat(user_id: int, message: str, db: Session = Depends(get_db)):
    # 1. Save user message
    user = db.query(User).filter(User.id == user_id).first()
    user_message = Message(user_id=user.id, content=message, role='user')
    db.add(user_message)
    db.commit()

    # 2. Fetch chat history
    history = db.query(Message).filter(Message.user_id == user.id).order_by(Message.timestamp).all()
    chat_history = [{"role": msg.role, "content": msg.content} for msg in history]

    # 3. Append current user message
    chat_history.append({"role": "user", "content": message})

    # 4. Send to Groq LLM
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "mixtral-8x7b-32768",  # Or llama3-70b-8192
        "messages": chat_history,
        "temperature": 0.3
    }

    response = requests.post(GROQ_API_URL, headers=headers, json=payload)

    if response.status_code == 200:
        ai_response = response.json()["choices"][0]["message"]["content"]
    else:
        ai_response = "Sorry, there was an issue contacting the AI service."

    # 5. Save AI response
    bot_message = Message(user_id=user.id, content=ai_response, role='assistant')
    db.add(bot_message)
    db.commit()

    return {"response": ai_response}
