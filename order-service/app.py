from fastapi import FastAPI
import requests
import psycopg2
import os

app = FastAPI(title="Order Service")

# Service URLs
USER_SERVICE_URL = os.getenv(
    "USER_SERVICE_URL",
    "http://user-service.microshop.svc.cluster.local"
)

PRODUCT_SERVICE_URL = os.getenv(
    "PRODUCT_SERVICE_URL",
    "http://product-service.microshop.svc.cluster.local"
)

# Database config
DB_HOST = os.getenv("DB_HOST", "postgres")
DB_NAME = os.getenv("DB_NAME", "ordersdb")
DB_USER = os.getenv("DB_USER", "orderuser")
DB_PASSWORD = os.getenv("DB_PASSWORD", "orderpass")

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
        CREATE TABLE IF NOT EXISTS orders (
            id SERIAL PRIMARY KEY,
            user_id INT,
            product_id INT,
            status TEXT
        )
    """)
    conn.commit()
    cur.close()
    conn.close()

@app.get("/health")
def health():
    return {"status": "UP"}

# -------------------------
# CREATE ORDER
# -------------------------
@app.post("/orders")
def create_order(user_id: int, product_id: int):

    user_resp = requests.get(f"{USER_SERVICE_URL}/users/{user_id}")
    if user_resp.status_code != 200 or "error" in user_resp.json():
        return {"error": "User does not exist"}

    product_resp = requests.get(f"{PRODUCT_SERVICE_URL}/products/{product_id}")
    if product_resp.status_code != 200 or "error" in product_resp.json():
        return {"error": "Product does not exist"}

    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO orders (user_id, product_id, status) VALUES (%s, %s, %s) RETURNING id",
        (user_id, product_id, "CREATED")
    )
    order_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()

    return {
        "order_id": order_id,
        "user": user_resp.json(),
        "product": product_resp.json(),
        "status": "CREATED"
    }

# -------------------------
# LIST ALL ORDERS
# -------------------------
@app.get("/orders")
def list_orders():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT id, user_id, product_id, status FROM orders")
    rows = cur.fetchall()
    cur.close()
    conn.close()

    return [
        {
            "order_id": r[0],
            "user_id": r[1],
            "product_id": r[2],
            "status": r[3]
        }
        for r in rows
    ]

# -------------------------
# LIST ORDERS BY USER
# -------------------------
@app.get("/orders/user/{user_id}")
def list_orders_by_user(user_id: int):
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "SELECT id, product_id, status FROM orders WHERE user_id = %s",
        (user_id,)
    )
    rows = cur.fetchall()
    cur.close()
    conn.close()

    orders = []
    for r in rows:
        product_resp = requests.get(
            f"{PRODUCT_SERVICE_URL}/products/{r[1]}"
        )
        product = product_resp.json() if product_resp.status_code == 200 else {}

        orders.append({
            "order_id": r[0],
            "product": product,
            "status": r[2]
        })

    return {
        "user_id": user_id,
        "orders": orders
    }
