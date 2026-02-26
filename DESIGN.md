# Coffee Market App Design Document

## 1. System Architecture
The application consists of three main components:
- **Telegram Bot (aiogram):** Entry point, notifications, and user registration.
- **FastAPI Backend:** Handles business logic, database operations, and serves the Mini App.
- **PostgreSQL Database:** Stores users, products, categories, orders, and delivery info.
- **Telegram Mini App:** A responsive web interface for users (shopping) and admins (management).

---

## 2. User Side Visualization (Mini App)

### A. Home Screen (Catalog)
```
________________________________________________
| [Logo]  Coffee Market       [Cart: (2) 45k] |
|______________________________________________|
|  [Search products...]                        |
|______________________________________________|
| Categories:                                  |
| (All)  (Coffee)  (Tea)  (Food)  (Soda)       |
|______________________________________________|
|                                              |
|  [ PRODUCT IMAGE ]      [ PRODUCT IMAGE ]    |
|  Cappuccino             Latte                |
|  25,000 UZS             22,000 UZS           |
|  [ Add to Cart ]        [ Add to Cart ]      |
|                                              |
|  [ PRODUCT IMAGE ]      [ PRODUCT IMAGE ]    |
|  Espresso               Americano            |
|  15,000 UZS             18,000 UZS           |
|  [ Add to Cart ]        [ Add to Cart ]      |
|______________________________________________|
| [Home]    [Orders]    [Profile]              |
|______________________________________________|
```

### B. Korzinka (Cart)
```
________________________________________________
| < Back to Catalog          Your Korzinka     |
|______________________________________________|
| 1. Cappuccino (x1) ........... 25,000 UZS    |
|    [-] 1 [+]                                 |
|                                              |
| 2. Latte (x1) ................ 22,000 UZS    |
|    [-] 1 [+]                                 |
|______________________________________________|
| Total: 47,000 UZS                            |
|______________________________________________|
| [   PROCEED TO CHECKOUT   ]                  |
|______________________________________________|
```

### C. Checkout / Personal Info
```
________________________________________________
| < Back to Cart             Checkout          |
|______________________________________________|
| Personal Information:                        |
| Full Name: [ John Doe              ]         |
| Phone:     [ +998 90 123 45 67     ]         |
| Address:   [ 123 Coffee St, Tashkent]         |
|                                              |
| [ ] Deliver to this address                  |
|                                              |
| Payment Method:                              |
| (o) Click    ( ) Payme    ( ) Cash           |
|______________________________________________|
| [   CONFIRM AND PAY   ]                      |
|______________________________________________|
```

---

## 3. Admin Side Visualization (Mini App)

### A. Dashboard (Statistics & Analytics)
```
________________________________________________
| Admin Panel                 [Admin: Alex]    |
|______________________________________________|
| Today's Summary:                             |
| Revenue: 1,250,000 UZS                       |
| Orders: 45                                   |
| New Users: 12                                |
|______________________________________________|
| Sales Analytics (AI Insight):                |
| [ CHART: Daily Sales Trend ]                 |
| * AI Suggestion: "Latte sales are up by 20%. |
|   Consider a morning promo for Cappuccino."  |
|______________________________________________|
| [Orders] [Products] [Deliverers] [Stats]     |
|______________________________________________|
```

### B. Product Management
```
________________________________________________
| < Back                     Product List      |
|______________________________________________|
| [ + Add New Product ] [ + Add Category ]     |
|______________________________________________|
| Drinks > Coffee                              |
| - Cappuccino (25k) [Edit] [Delete]           |
| - Latte (22k)      [Edit] [Delete]           |
|                                              |
| Food > Snacks                                |
| - Croissant (15k)  [Edit] [Delete]           |
|______________________________________________|
```

---

## 4. User Flow
1. **Start:** User starts bot `/start` -> Bot sends greeting and "Open Shop" button.
2. **Catalog:** User browses categories/products in Mini App.
3. **Cart:** User adds items to Korzinka.
4. **Checkout:** User enters/confirms personal info (Phone, Address).
5. **Payment:** User selects Click/Payme -> Redirects to payment provider.
6. **Order Confirmation:** After payment, User gets notification; Admin gets notification.
7. **Delivery:** Admin assigns a deliverer -> Deliverer delivers -> Order marked "Completed".

---

## 5. Database Schema (PostgreSQL)

Based on the provided design (`Database.png`), the system will use the following schema:

#### Core Tables
*   **users**: `user_id` (PK), `telegram_id` (Unique), `fullname`, `registered_at`.
*   **user_roles**: `user_id`, `role` (enum: super_admin, admin, client, deliverer).
*   **admin_profile**: `user_id` (PK), permissions (manage_catalogs, manage_products, manage_deliverers, assign_orders, manage_histories, see_statistics).
*   **clients**: `user_id` (PK), `phone_number`, `address`.
*   **deliverers**: `user_id` (PK), `phone_number`, `added_by` (FK to admin).

#### Catalog & Products
*   **catalogs**: `id` (PK), `name`, `father_id` (Self-reference for nested categories), `created_at`, `created_by`.
*   **products**: `id` (PK), `name`, `description`, `price`, `catalog_id` (FK), `created_at`, `created_by`.
*   **product_count**: `product_id` (FK), `count` (Stock level).

#### Sales & Cart
*   **client_carts**: `id` (PK), `user_id` (FK), `status` (active, ordered, abandoned).
*   **cart_items**: `id` (PK), `cart_id` (FK), `product_id` (FK), `quantity`, `price`.
*   **orders**: `id` (PK), `cart_id` (FK, Unique), `total_amount`, `status` (pending, paid, shipping, delivered), `deliverer_id` (FK to deliverer), `created_at`.

---

## 6. AI/ML Integration Ideas
- **Demand Forecasting:** Predict next day's stock needs based on historical order data.
- **Product Recommendations:** "Users who bought Latte also liked Croissants."
- **Customer Segmentation:** Identify loyal customers for special discounts.
