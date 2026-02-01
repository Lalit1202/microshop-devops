from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import requests
import os

app = FastAPI(title="Microshop UI")
templates = Jinja2Templates(directory="templates")

USER_SERVICE = os.getenv("USER_SERVICE_URL", "http://user-service")
PRODUCT_SERVICE = os.getenv("PRODUCT_SERVICE_URL", "http://product-service")
ORDER_SERVICE = os.getenv("ORDER_SERVICE_URL", "http://order-service")

# ------------------------
# LOGIN
# ------------------------
@app.get("/", response_class=HTMLResponse)
def login_page(request: Request):
    users = requests.get(f"{USER_SERVICE}/users").json()
    return templates.TemplateResponse(
        "login.html",
        {"request": request, "users": users}
    )

@app.post("/login")
def login(user_id: int = Form(...)):
    response = RedirectResponse("/products", status_code=302)
    response.set_cookie(key="user_id", value=str(user_id))
    return response

# ------------------------
# REGISTER
# ------------------------
@app.get("/register", response_class=HTMLResponse)
def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.post("/register")
def register(name: str = Form(...), email: str = Form(...)):
    requests.post(
        f"{USER_SERVICE}/users",
        params={"name": name, "email": email}
    )
    return RedirectResponse("/", status_code=302)

# ------------------------
# PRODUCTS
# ------------------------
@app.get("/products", response_class=HTMLResponse)
def products_page(request: Request):
    user_id = request.cookies.get("user_id")
    if not user_id:
        return RedirectResponse("/")

    products = requests.get(f"{PRODUCT_SERVICE}/products").json()
    return templates.TemplateResponse(
        "products.html",
        {"request": request, "products": products, "user_id": user_id}
    )

# ------------------------
# CREATE ORDER
# ------------------------
@app.post("/order")
def create_order(request: Request, product_id: int = Form(...)):
    user_id = request.cookies.get("user_id")
    requests.post(
        f"{ORDER_SERVICE}/orders",
        params={"user_id": user_id, "product_id": product_id}
    )
    return RedirectResponse("/orders", status_code=302)

# ------------------------
# VIEW ORDERS
# ------------------------
@app.get("/orders", response_class=HTMLResponse)
def orders_page(request: Request):
    user_id = request.cookies.get("user_id")
    if not user_id:
        return RedirectResponse("/")

    data = requests.get(
        f"{ORDER_SERVICE}/orders/user/{user_id}"
    ).json()

    return templates.TemplateResponse(
        "orders.html",
        {"request": request, "orders": data["orders"]}
    )
