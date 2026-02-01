from fastapi import FastAPI
import psycopg2
import os

app = FastAPI(title="Product Service")

DB_HOST = os.getenv("DB_HOST", "product-postgres")
DB_NAME = os.getenv("DB_NAME", "productsdb")
DB_USER = os.getenv("DB_USER", "productapp")
DB_PASSWORD = os.getenv("DB_PASSWORD", "productpass")

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
        CREATE TABLE IF NOT EXISTS products (
            id SERIAL PRIMARY KEY,
            name TEXT,
            price INT
        )
    """)
    conn.commit()
    cur.close()
    conn.close()

@app.get("/health")
def health():
    return {"status": "UP"}

@app.post("/products")
def create_product(name: str, price: int):
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO products (name, price) VALUES (%s, %s) RETURNING id",
        (name, price)
    )
    product_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()

    return {
        "id": product_id,
        "name": name,
        "price": price
    }

@app.get("/products")
def list_products():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT id, name, price FROM products")
    rows = cur.fetchall()
    cur.close()
    conn.close()

    return [
        {"id": r[0], "name": r[1], "price": r[2]}
        for r in rows
    ]

@app.get("/products/{product_id}")
def get_product(product_id: int):
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "SELECT id, name, price FROM products WHERE id = %s",
        (product_id,)
    )
    row = cur.fetchone()
    cur.close()
    conn.close()

    if not row:
        return {"error": "Product not found"}

    return {
        "id": row[0],
        "name": row[1],
        "price": row[2]
    }
