from fastapi import FastAPI, HTTPException
from db import SessionLocal, User, Conversation, Message
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

app = FastAPI()

# --------------------- SCHEMAS ---------------------
class UserSchema(BaseModel):
    id: int
    name: str
    email: str
    created_at: str

    class Config:
        orm_mode = False


class ChatRequest(BaseModel):
    user_id: int
    message: str
    conversation_id: Optional[int] = None


class ChatResponse(BaseModel):
    conversation_id: int
    user_message: str
    ai_response: str

# --------------------- ENDPOINTS ---------------------

# Root endpoint
@app.get("/")
def root():
    return {"message": "Welcome to the E-commerce API!"}

# Get all users
@app.get("/users", response_model=List[UserSchema])
def get_users():
    session = SessionLocal()
    users = session.query(User).all()
    session.close()
    return users

# Get user by ID
@app.get("/users/{user_id}", response_model=UserSchema)
def get_user(user_id: int):
    session = SessionLocal()
    user = session.query(User).filter(User.id == user_id).first()
    session.close()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# --------------------- MILESTONE 4 - CHAT API ---------------------
@app.post("/api/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    session = SessionLocal()

    # Validate user
    user = session.query(User).filter(User.id == request.user_id).first()
    if not user:
        session.close()
        raise HTTPException(status_code=404, detail="User not found")

    # Create new conversation if not provided
    if request.conversation_id:
        conversation = session.query(Conversation).filter(Conversation.id == request.conversation_id).first()
        if not conversation:
            session.close()
            raise HTTPException(status_code=404, detail="Conversation not found")
    else:
        conversation = Conversation(user_id=request.user_id, created_at=datetime.utcnow())
        session.add(conversation)
        session.commit()
        session.refresh(conversation)

    # Save user's message
    user_message = Message(
        conversation_id=conversation.id,
        sender="user",
        message=request.message,
        timestamp=datetime.utcnow()
    )
    session.add(user_message)

    # Simulate AI response
    ai_text = f"Echo: {request.message}"  # TODO: Replace with real model response

    # Save AI's response
    ai_response = Message(
        conversation_id=conversation.id,
        sender="ai",
        message=ai_text,
        timestamp=datetime.utcnow()
    )
    session.add(ai_response)

    # Commit all changes
    session.commit()
    session.close()

    return ChatResponse(
        conversation_id=conversation.id,
        user_message=request.message,
        ai_response=ai_text
    )
