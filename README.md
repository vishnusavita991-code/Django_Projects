# NEXUS E-Commerce Platform
![developer](https://img.shields.io/badge/Developed%20By-Vishnu%20Savita%20%26%20Shaksham%20Kushwaha-blueviolet)
![django](https://img.shields.io/badge/Framework-Django%205.x-green)
![python](https://img.shields.io/badge/Python-3.13-blue)
![license](https://img.shields.io/badge/License-MIT-yellow)

---

## 📸 Screenshots

### Admin Dashboard
![dashboard snap](https://github.com/sumitkumar1503/ecommerce/blob/master/static/screenshots/adminHomepage.png?raw=true)

### Customer Homepage
![homepage snap](https://github.com/sumitkumar1503/ecommerce/blob/master/static/screenshots/customerhomepage.png?raw=true)

### Cart
![cart snap](https://github.com/sumitkumar1503/ecommerce/blob/master/static/screenshots/cart.png?raw=true)

### Track Orders
![orders snap](https://github.com/sumitkumar1503/ecommerce/blob/master/static/screenshots/orderspage.png?raw=true)

---

## ✨ Features

### 🛍️ Customer Features
- Browse and search products with category filters, sort by price/rating/newest — **no login required**
- Add/remove products from cart using cookies — **no login required**
- Quick View modal: product details, rating, stock, discount badge
- Wishlist toggle (per session) for saving favourite items
- Login/Signup with profile picture upload
- **Checkout flow** with address autofill, coupon codes, and multiple payment methods
  - Coupon `SAVE10` → 10% off
  - Coupon `WELCOME20` → 20% off
  - Free shipping on orders above ₹999
- View order history with real-time status tracking (Pending → Confirmed → Out for Delivery → Delivered)
- **Download PDF invoice** for each order
- Edit profile (name, email, mobile, address, profile picture)
- Send feedback to admin (no login required)
- About Us and Contact Us pages

### 🔐 Admin Features
- Secure admin login (separate from customer login)
- **Live Dashboard** showing: total customers, products, orders, revenue, pending/confirmed/delivered breakdown
- Recent orders table on the dashboard
- **Manage Products**: Add, Edit, Delete — with category, price, original price, stock, rating, image
- **Manage Customers**: View, Edit, Delete
- **Manage Orders**: View all, filter by status, update status, delete
- Quick status update buttons: Pending → Confirmed → Out for Delivery → Delivered
- View all customer feedbacks

### 🧰 Advanced Features Added
| Feature | Details |
|---|---|
| **Category filter chips** | Clickable category pills with icons for Electronics, Fashion, Home & Living, Accessories, Gadgets |
| **Sort & Search** | Sort by price asc/desc, rating, newest; full-text search across name, description, category |
| **Quick View Modal** | Glassmorphism modal with product image, discount %, in-stock badge, add-to-cart |
| **Coupon System** | Cookie-based coupon system validating SAVE10 / WELCOME20 |
| **Revenue Tracker** | Admin dashboard displays total revenue calculated from all orders |
| **Multiple Payment Methods** | Card/Online, UPI/QR, Cash on Delivery — with animated UI tabs |
| **Toast Notifications** | Elegant, auto-dismissing toast popups for cart, wishlist actions |
| **Invoice PDF Download** | xhtml2pdf-powered downloadable invoice with full order details |
| **Flash Messages** | Styled success/error/info inline messages with dismiss button |
| **Discount Badges** | Auto-computed discount % displayed as badges on product cards |

---

## 🚀 How to Run This Project

### Requirements
- Python 3.10+ (tested on Python 3.13)
- pip

### Setup Steps

```bash
# 1. Extract or clone the project and navigate into it
cd ecommerce

# 2. Create a virtual environment
python -m venv venv

# 3. Activate the virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# 4. Install dependencies
pip install "django>=4.2" pillow xhtml2pdf django-widget-tweaks

# 5. Apply database migrations
python manage.py makemigrations
python manage.py migrate

# 6. (Optional) Create an admin superuser
python manage.py createsuperuser

# 7. Start the development server
python manage.py runserver
```

Open your browser and visit:
```
http://127.0.0.1:8000/
```

---

## 📧 Contact Us Email Setup

To enable email sending via the Contact Us form, edit `ecommerce/settings.py`:

```python
EMAIL_HOST_USER = 'youremail@gmail.com'         # Sender Gmail address
EMAIL_HOST_PASSWORD = 'your_app_password'        # Gmail App Password (not your account password)
EMAIL_RECEIVING_USER = ['youremail@gmail.com']   # Where you want to receive messages
```

> **Note:** Use a [Gmail App Password](https://myaccount.google.com/apppasswords) for `EMAIL_HOST_PASSWORD`. Regular account passwords will not work due to Google security policy.

---

## 🗄️ Available Coupon Codes

| Code | Discount |
|---|---|
| `SAVE10` | 10% off the total cart value |
| `WELCOME20` | 20% off the total cart value |

Free shipping is automatically applied on orders above ₹999.

---

## ⚠️ Known Limitations
- After editing profile, the customer must log in again (credentials are updated in DB).
- Wishlist is client-side only (JS/cookie) and does not persist across devices or sessions.
- Payment page is for **demo purposes only** — do NOT enter real card/UPI details.
- Email setup requires a valid Gmail App Password in `settings.py`.

---

## 📋 Disclaimer
This project is developed for **educational and demo purposes only** and is not intended for production use without proper security review.

---

## 👨‍💻 Developers

| Name | Role |
|---|---|
| **Vishnu Savita** | Full Stack Developer |
| **Shaksham Kushwaha** | Full Stack Developer |

---

## 📬 Feedback
Any suggestions and feedback are welcome. Feel free to open an issue or submit a pull request.
