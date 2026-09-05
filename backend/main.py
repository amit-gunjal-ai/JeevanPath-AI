from fastapi import FastAPI
from database import get_connection
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import bcrypt

app = FastAPI()

@app.get("/")
def home():
    return {"message": "API is running"}

@app.get("/test-db")
def test_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    return {"users": result}

class SignupData(BaseModel):
    full_name: str
    mobile_number: str
    password: str
    preferred_language: str

@app.post("/signup")
def signup(data: SignupData):
    conn = get_connection()
    cursor = conn.cursor()

    # Hash the password before storing
    hashed_pw = bcrypt.hashpw(data.password.encode('utf-8'), bcrypt.gensalt())

    query = "INSERT INTO users (full_name, mobile_number, password_hash, preferred_language) VALUES (%s, %s, %s, %s)"
    values = (data.full_name, data.mobile_number, hashed_pw.decode('utf-8'), data.preferred_language)

    cursor.execute(query, values)
    conn.commit()

    cursor.close()
    conn.close()

    return {"message": "User created successfully"}


class LoginData(BaseModel):
    mobile_number: str
    password: str

@app.post("/login")
def login(data: LoginData):
    conn = get_connection()
    cursor = conn.cursor()

    query = "SELECT * FROM users WHERE mobile_number = %s"
    cursor.execute(query, (data.mobile_number,))
    user = cursor.fetchone()

    cursor.close()
    conn.close()

    if user is None:
        return {"error": "User not found"}

    stored_hash = user[3].encode('utf-8')
    if not bcrypt.checkpw(data.password.encode('utf-8'), stored_hash):
        return {"error": "Incorrect password"}

    return {"message": "Login successful", "full_name": user[1]}


from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)