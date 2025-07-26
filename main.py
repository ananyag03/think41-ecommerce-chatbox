from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from db import engine, SessionLocal
from models import Base, User, Message
from datetime import datetime
import uuid
import openai  # Using OpenAI/Groq

# === Setup ===
Base.metadata.create_all(bind=engine)
app = FastAPI()

# === CORS ===
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# === Dependency ===
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# === LLM Configuration ===
openai.api_key = "YOUR_GROQ_OR_OPENAI_API_KEY"  # <-- Replace with your actual key
LLM_MODEL = "gpt-3.5-turbo"  # Or 'mixtral-8x7b-32768' for Groq

def generate_ai_response(messages: List[dict]) -> str:
    try:
        response = openai.ChatCompletion.create(
            model=LLM_MODEL,
            messages=messages
        )
        return response.choices[0].message['content']
    except Exception as e:
        return f"LLM Error: {str(e)}"

# === Schemas ===
class UserCreate(BaseModel):
    name: str

class UserOut(BaseModel):
    id: int
    name: str
    class Config:
        orm_mode = True

class MessageCreate(BaseModel):
    user_id: int
    message: str
    conversation_id: Optional[int] = None

class ChatResponse(BaseModel):
    conversation_id: int
    user_message: str
    ai_response: str

class MessageOut(BaseModel):
    id: int
    content: str
    role: str
    timestamp: datetime
    class Config:
        orm_mode = True

# === Routes ===

@app.get("/")
def root():
    return {"message": "Chat API is running!"}

@app.post("/users", response_model=UserOut)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = User(name=user.name)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.get("/users", response_model=List[UserOut])
def get_all_users(db: Session = Depends(get_db)):
    return db.query(User).all()

@app.get("/users/{user_id}", response_model=UserOut)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.get("/users/{user_id}/conversations")
def get_user_conversations(user_id: int, db: Session = Depends(get_db)):
    messages = db.query(Message).filter(Message.user_id == user_id).all()
    history = {}
    for msg in messages:
        history.setdefault(msg.conversation_id, []).append({
            "role": msg.role,
            "content": msg.content,
            "timestamp": msg.timestamp
        })
    return history

@app.post("/api/chat", response_model=ChatResponse)
def chat(msg: MessageCreate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == msg.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Generate or reuse conversation ID
    conversation_id = msg.conversation_id or uuid.uuid4().int >> 64

    # Save user message
    user_msg = Message(
        user_id=msg.user_id,
        content=msg.message,
        role="user",
        timestamp=datetime.utcnow(),
        conversation_id=conversation_id
    )
    db.add(user_msg)
    db.commit()

    # Fetch conversation history
    history = db.query(Message).filter(
        Message.user_id == msg.user_id,
        Message.conversation_id == conversation_id
    ).order_by(Message.timestamp).all()

    formatted_history = [{"role": m.role, "content": m.content} for m in history]

    # AI response
    ai_reply = generate_ai_response(formatted_history)

    # Save AI reply
    ai_msg = Message(
        user_id=msg.user_id,
        content=ai_reply,
        role="assistant",
        timestamp=datetime.utcnow(),
        conversation_id=conversation_id
    )
    db.add(ai_msg)
    db.commit()

    return ChatResponse(
        conversation_id=conversation_id,
        user_message=msg.message,
        ai_response=ai_reply
    )
