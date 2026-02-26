from sqlalchemy import Column, Integer, String, BigInteger, ForeignKey, DateTime, DECIMAL, Enum, Text, Boolean
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.sql import func
import enum

Base = declarative_base()

class UserRole(enum.Enum):
    super_admin = "super_admin"
    admin = "admin"
    client = "client"
    deliverer = "deliverer"

class OrderStatus(enum.Enum):
    pending = "pending"
    paid = "paid"
    shipping = "shipping"
    delivered = "delivered"

class CartStatus(enum.Enum):
    active = "active"
    ordered = "ordered"
    abandoned = "abandoned"

class User(Base):
    __tablename__ = "users"
    telegram_id = Column(BigInteger, primary_key=True)
    fullname = Column(String(255))
    registered_at = Column(DateTime(timezone=True), server_default=func.now())

    roles = relationship("UserRoleMapping", back_populates="user")
    admin_profile = relationship("AdminProfile", back_populates="user", uselist=False)
    client_profile = relationship("ClientProfile", back_populates="user", uselist=False)
    deliverer_profile = relationship("DelivererProfile",
                                   back_populates="user",
                                   uselist=False,
                                   foreign_keys="DelivererProfile.user_id")

class UserRoleMapping(Base):
    __tablename__ = "user_roles"
    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, ForeignKey("users.telegram_id", ondelete="CASCADE"))
    role = Column(Enum(UserRole), nullable=False)

    user = relationship("User", back_populates="roles")

class AdminProfile(Base):
    __tablename__ = "admin_profiles"
    user_id = Column(BigInteger, ForeignKey("users.telegram_id", ondelete="CASCADE"), primary_key=True)
    manage_catalogs = Column(Boolean, default=False)
    manage_products = Column(Boolean, default=False)
    manage_deliverers = Column(Boolean, default=False)
    assign_orders = Column(Boolean, default=False)
    manage_histories = Column(Boolean, default=False)
    see_statistics = Column(Boolean, default=False)

    user = relationship("User", back_populates="admin_profile")

class ClientProfile(Base):
    __tablename__ = "clients"
    user_id = Column(BigInteger, ForeignKey("users.telegram_id", ondelete="CASCADE"), primary_key=True)
    phone_number = Column(String(20))
    address = Column(Text)

    user = relationship("User", back_populates="client_profile")

class DelivererProfile(Base):
    __tablename__ = "deliverers"
    user_id = Column(BigInteger, ForeignKey("users.telegram_id", ondelete="CASCADE"), primary_key=True)
    phone_number = Column(String(20))
    added_by = Column(BigInteger, ForeignKey("users.telegram_id"))

    user = relationship("User", back_populates="deliverer_profile", foreign_keys=[user_id])
    adder = relationship("User", foreign_keys=[added_by])

class Catalog(Base):
    __tablename__ = "catalogs"
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    father_id = Column(Integer, ForeignKey("catalogs.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by = Column(BigInteger, ForeignKey("users.telegram_id"))

    subcategories = relationship("Catalog", backref="parent", remote_side=[id])
    products = relationship("Product", back_populates="catalog")

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    price = Column(DECIMAL(12, 2), nullable=False)
    catalog_id = Column(Integer, ForeignKey("catalogs.id", ondelete="CASCADE"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by = Column(BigInteger, ForeignKey("users.telegram_id"))

    catalog = relationship("Catalog", back_populates="products")
    stock = relationship("ProductStock", back_populates="product", uselist=False)

class ProductStock(Base):
    __tablename__ = "product_stocks"
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), primary_key=True)
    count = Column(Integer, default=0)

    product = relationship("Product", back_populates="stock")

class ClientCart(Base):
    __tablename__ = "client_carts"
    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, ForeignKey("users.telegram_id", ondelete="CASCADE"))
    status = Column(Enum(CartStatus), default=CartStatus.active)

    items = relationship("CartItem", back_populates="cart")
    order = relationship("Order", back_populates="cart", uselist=False)

class CartItem(Base):
    __tablename__ = "cart_items"
    id = Column(Integer, primary_key=True)
    cart_id = Column(Integer, ForeignKey("client_carts.id", ondelete="CASCADE"))
    product_id = Column(Integer, ForeignKey("products.id"))
    quantity = Column(Integer, default=1)
    price = Column(DECIMAL(12, 2))

    cart = relationship("ClientCart", back_populates="items")
    product = relationship("Product")

class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True)
    cart_id = Column(Integer, ForeignKey("client_carts.id"), unique=True)
    total_amount = Column(DECIMAL(12, 2))
    status = Column(Enum(OrderStatus), default=OrderStatus.pending)
    deliverer_id = Column(BigInteger, ForeignKey("deliverers.user_id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    cart = relationship("ClientCart", back_populates="order")
    deliverer = relationship("DelivererProfile")
