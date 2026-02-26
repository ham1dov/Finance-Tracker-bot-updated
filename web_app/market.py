from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List, Optional
from database.db_setup import get_db
from database.models import Catalog, Product, ProductStock, ClientCart, CartItem, Order, OrderStatus, CartStatus
from pydantic import BaseModel
from decimal import Decimal

router = APIRouter(prefix="/market", tags=["market"])

# --- Schemas ---

class CategoryBase(BaseModel):
    name: str
    father_id: Optional[int] = None

class CategoryResponse(CategoryBase):
    id: int
    class Config:
        from_attributes = True

class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: Decimal
    catalog_id: int

class ProductResponse(ProductBase):
    id: int
    stock_count: Optional[int] = None
    class Config:
        from_attributes = True

class CartItemBase(BaseModel):
    product_id: int
    quantity: int

class CartItemResponse(CartItemBase):
    id: int
    price: Decimal
    class Config:
        from_attributes = True

class CartResponse(BaseModel):
    id: int
    user_id: int
    status: CartStatus
    items: List[CartItemResponse]
    class Config:
        from_attributes = True

class OrderCreate(BaseModel):
    cart_id: int
    total_amount: Decimal

class OrderResponse(BaseModel):
    id: int
    cart_id: int
    total_amount: Decimal
    status: OrderStatus
    class Config:
        from_attributes = True

# --- Endpoints ---

@router.get("/categories", response_model=List[CategoryResponse])
async def get_categories(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Catalog))
    return result.scalars().all()

@router.get("/products", response_model=List[ProductResponse])
async def get_products(catalog_id: Optional[int] = None, db: AsyncSession = Depends(get_db)):
    query = select(Product)
    if catalog_id:
        query = query.where(Product.catalog_id == catalog_id)

    result = await db.execute(query)
    products = result.scalars().all()

    response = []
    for p in products:
        stock_result = await db.execute(select(ProductStock).where(ProductStock.product_id == p.id))
        stock = stock_result.scalar_one_or_none()

        p_data = ProductResponse.model_validate(p)
        p_data.stock_count = stock.count if stock else 0
        response.append(p_data)

    return response

@router.post("/cart/{user_id}/add", response_model=CartResponse)
async def add_to_cart(user_id: int, item: CartItemBase, db: AsyncSession = Depends(get_db)):
    # Get active cart or create one
    result = await db.execute(
        select(ClientCart)
        .options(selectinload(ClientCart.items))
        .where(ClientCart.user_id == user_id, ClientCart.status == CartStatus.active)
    )
    cart = result.scalar_one_or_none()

    if not cart:
        cart = ClientCart(user_id=user_id, status=CartStatus.active)
        db.add(cart)
        await db.flush()

    # Get product price
    prod_result = await db.execute(select(Product).where(Product.id == item.product_id))
    product = prod_result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Check if item exists in cart
    item_result = await db.execute(select(CartItem).where(CartItem.cart_id == cart.id, CartItem.product_id == item.product_id))
    existing_item = item_result.scalar_one_or_none()

    if existing_item:
        existing_item.quantity += item.quantity
    else:
        new_item = CartItem(cart_id=cart.id, product_id=item.product_id, quantity=item.quantity, price=product.price)
        db.add(new_item)

    await db.commit()

    # Reload with items
    result = await db.execute(
        select(ClientCart)
        .options(selectinload(ClientCart.items))
        .where(ClientCart.id == cart.id)
    )
    cart = result.scalar_one_or_none()
    return cart

from utils.notifications import notify_admin_new_order
from web_app.bot.engine import bot

@router.post("/orders", response_model=OrderResponse)
async def create_order(order_data: OrderCreate, db: AsyncSession = Depends(get_db)):
    # Check cart
    cart_result = await db.execute(select(ClientCart).where(ClientCart.id == order_data.cart_id))
    cart = cart_result.scalar_one_or_none()
    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found")

    # Create order
    new_order = Order(cart_id=cart.id, total_amount=order_data.total_amount, status=OrderStatus.pending)
    db.add(new_order)

    # Update cart status
    cart.status = CartStatus.ordered

    await db.commit()
    await db.refresh(new_order)

    # Trigger notification
    await notify_admin_new_order(bot, new_order.id, db)

    return new_order
