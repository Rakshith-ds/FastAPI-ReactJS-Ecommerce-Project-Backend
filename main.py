from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from connection import SessionLocal, engine
from models import Base, User, CartItem, Product
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import signup, login_token
from login_token import get_current_user
from sqlalchemy import func
from recommendations import store_product_embeddings, recommend_similar_products

app = FastAPI()

# Ensure the table is created
Base.metadata.create_all(bind=engine)

origins = [
    "http://localhost",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# Pydantic models
class LogInUser(BaseModel):
    email: str
    password: str


class SignUpUser(BaseModel):
    fname: str
    lname: str
    email: str
    password: str
    repassword: str


class Token(BaseModel):
    access_token: str
    token_type: str
    user_id: int


class AddCart(BaseModel):
    user_id: int
    product_id: int
    quantity: int


class DeleteCart(BaseModel):
    product_id: int


class Search(BaseModel):
    search: str


@app.post("/signup/")
def read_users(user_data: SignUpUser, db: Session = Depends(get_db)):
    return signup.signupfunction(user_data, db)


@app.post("/token/", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    return login_token.create_access_token(form_data, db)


@app.post("/cart/")
async def add_to_cart(
    add_cart: AddCart,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Check if product exists
    product = db.query(Product).filter(Product.id == add_cart.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Check if the item is already in the cart
    cart_item = (
        db.query(CartItem)
        .filter(
            CartItem.user_id == current_user.id,
            CartItem.product_id == add_cart.product_id,
        )
        .first()
    )
    if cart_item:
        cart_item.quantity += add_cart.quantity
    else:
        cart_item = CartItem(
            user_id=current_user.id,
            product_id=add_cart.product_id,
            quantity=add_cart.quantity,
        )
        db.add(cart_item)

    db.commit()
    db.refresh(cart_item)
    return {"message": "Item added to cart", "cart_item": "cart_item"}


@app.get("/cart/")
def view_cart(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    cart_items = (
        db.query(CartItem, Product)
        .join(Product, CartItem.product_id == Product.id)
        .filter(CartItem.user_id == current_user.id)
        .all()
    )
    result = []
    for cart_item, product in cart_items:
        result.append(
            {
                "id": product.id,
                "title": product.title,
                "price": product.price,
                "images": product.image_url,
                "quantity": cart_item.quantity,
            }
        )
    total_quantity = (
        db.query(func.sum(CartItem.quantity))
        .filter(CartItem.user_id == current_user.id)
        .scalar()
    )

    total_price = (
        db.query(func.sum(CartItem.quantity * Product.price))
        .join(Product, CartItem.product_id == Product.id)
        .filter(CartItem.user_id == current_user.id)
        .scalar()
    )
    return {
        "cart_items": result,
        "quantity": total_quantity,
        "total_price": total_price,
    }


@app.delete("/cart/{item_id}")
def remove_cart_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    cart_item = (
        db.query(CartItem)
        .filter(CartItem.product_id == item_id, CartItem.user_id == current_user.id)
        .first()
    )
    if not cart_item:
        raise HTTPException(status_code=404, detail="Cart item not found")

    if cart_item.quantity > 1:
        cart_item.quantity -= 1
    else:
        db.delete(cart_item)

    db.commit()


@app.get("/products/")
async def refresh_token(category: str, db: Session = Depends(get_db)):
    if category == "All":
        products = db.query(Product).all()
    else:
        products = db.query(Product).filter(Product.name == category).all()
    return products


@app.get("/products/{product_id}")
async def refresh_token(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    return product


@app.post("/load-product-embeddings/")
def load_product_embeddings(db: Session = Depends(get_db)):
    product_embeddings = store_product_embeddings(db)
    return product_embeddings


@app.get("/recommend/{product_title}")
def recommend(product_title: str, db: Session = Depends(get_db)):
    try:
        recommendations = recommend_similar_products(product_title, db)
        return recommendations
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="localhost", port=8000)
