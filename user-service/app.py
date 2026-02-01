from fastapi import FastAPI
import psycopg2
import os

app = FastAPI(title="User Service")

DB_HOST = os.getenv("DB_HOST", "user-postgres")
DB_NAME = os.getenv("DB_NAME", "usersdb")
DB_USER = os.getenv("DB_USER", "userapp")
DB_PASSWORD = os.getenv("DB_PASSWORD", "userpass")

def get_db():
    return psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )

@app.on_event("startup")
def startup():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            name TEXT,
            email TEXT
        )
    """)
    conn.commit()
    cur.close()
    conn.close()

@app.get("/health")
def health():
    return {"status": "UP"}

@app.post("/users")
def create_user(name: str, email: str):
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO users (name, email) VALUES (%s, %s) RETURNING id",
        (name, email)
    )
    user_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()

    return {
        "id": user_id,
        "name": name,
        "email": email
    }

@app.get("/users")
def list_users():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT id, name, email FROM users")
    rows = cur.fetchall()
    cur.close()
    conn.close()

    return [
        {"id": r[0], "name": r[1], "email": r[2]}
        for r in rows
    ]

@app.get("/users/{user_id}")
def get_user(user_id: int):
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "SELECT id, name, email FROM users WHERE id = %s",
        (user_id,)
    )
    row = cur.fetchone()
    cur.close()
    conn.close()

    if not row:
        return {"error": "User not found"}

    return {
        "id": row[0],
        "name": row[1],
        "email": row[2]
    }
