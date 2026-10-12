import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce.settings')
django.setup()

from ecom.models import Product
from PIL import Image, ImageDraw

products_data = [
    {
        'name': 'Sony WH-1000XM Wireless Headphones',
        'category': 'Electronics',
        'price': 2999,
        'original_price': 4999,
        'rating': 4.9,
        'reviews_count': 124,
        'stock': 35,
        'description': 'Industry-leading noise cancelation with premium audio clarity and 30-hour battery life.',
        'file': 'headphones_pro.png',
        'color': (24, 43, 73),
        'accent': (59, 130, 246)
    },
    {
        'name': 'Apple Watch Ultra Pro',
        'category': 'Gadgets',
        'price': 4499,
        'original_price': 6999,
        'rating': 4.8,
        'reviews_count': 98,
        'stock': 20,
        'description': 'Aerospace titanium case with precision dual-frequency GPS and up to 36h battery life.',
        'file': 'smartwatch_ultra.png',
        'color': (15, 23, 42),
        'accent': (249, 115, 22)
    },
    {
        'name': 'Nike Air Zoom Pegasus Sneakers',
        'category': 'Fashion',
        'price': 2199,
        'original_price': 3499,
        'rating': 4.7,
        'reviews_count': 210,
        'stock': 28,
        'description': 'Engineered mesh with dual Zoom Air units for responsive everyday athletic performance.',
        'file': 'sneakers_nike.png',
        'color': (45, 10, 80),
        'accent': (236, 72, 153)
    },
    {
        'name': 'Keychron RGB Mechanical Keyboard',
        'category': 'Electronics',
        'price': 3299,
        'original_price': 4599,
        'rating': 4.9,
        'reviews_count': 76,
        'stock': 15,
        'description': 'Wireless hot-swappable tactile switches with anodized aluminum body and RGB backlighting.',
        'file': 'keyboard_rgb.png',
        'color': (17, 24, 39),
        'accent': (168, 85, 247)
    },
    {
        'name': 'Ergonomic Memory Foam Lumbar Support',
        'category': 'Home & Living',
        'price': 1299,
        'original_price': 1999,
        'rating': 4.6,
        'reviews_count': 54,
        'stock': 42,
        'description': 'Orthopedic contoured memory foam for posture correction and breathable 3D mesh cover.',
        'file': 'lumbar_support.png',
        'color': (19, 78, 74),
        'accent': (20, 184, 166)
    },
    {
        'name': 'Bellroy Slim Leather RFID Wallet',
        'category': 'Accessories',
        'price': 899,
        'original_price': 1499,
        'rating': 4.7,
        'reviews_count': 89,
        'stock': 50,
        'description': 'Premium environmentally certified leather holding 4-11 cards with RFID protection.',
        'file': 'leather_wallet.png',
        'color': (67, 40, 24),
        'accent': (217, 119, 6)
    },
    {
        'name': 'Anker MagGo Magnetic 10,000mAh Powerbank',
        'category': 'Gadgets',
        'price': 1899,
        'original_price': 2699,
        'rating': 4.8,
        'reviews_count': 143,
        'stock': 32,
        'description': 'Qi2 certified 15W ultra-fast wireless charging with smart interactive display.',
        'file': 'powerbank_mag.png',
        'color': (30, 41, 59),
        'accent': (99, 102, 241)
    },
    {
        'name': 'Ray-Ban Wayfarer Classic Polarized',
        'category': 'Fashion',
        'price': 1199,
        'original_price': 1999,
        'rating': 4.6,
        'reviews_count': 67,
        'stock': 38,
        'description': '100% UV protection polarized crystal green lenses with timeless handcrafted acetate frames.',
        'file': 'sunglasses_rayban.png',
        'color': (20, 20, 30),
        'accent': (234, 179, 8)
    }
]

# Delete old products and recreate
Product.objects.all().delete()

for item in products_data:
    path = os.path.join('static', 'product_image', item['file'])
    img = Image.new('RGB', (600, 600), color=item['color'])
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle([25, 25, 575, 575], radius=24, outline=item['accent'], width=4)
    draw.rounded_rectangle([50, 50, 550, 410], radius=16, fill=(item['color'][0]+18, item['color'][1]+18, item['color'][2]+18))
    draw.ellipse([250, 180, 350, 280], fill=item['accent'])
    draw.text((70, 440), item['category'].upper(), fill=item['accent'])
    draw.text((70, 475), item['name'][:35], fill=(255, 255, 255))
    save_amount = item['original_price'] - item['price']
    draw.text((70, 515), f"Rs. {item['price']}  (Original: Rs. {item['original_price']} - Save Rs. {save_amount})", fill=(140, 230, 150))
    img.save(path)

    Product.objects.create(
        name=item['name'],
        category=item['category'],
        price=item['price'],
        original_price=item['original_price'],
        rating=item['rating'],
        reviews_count=item['reviews_count'],
        stock=item['stock'],
        description=item['description'],
        product_image='product_image/' + item['file']
    )

print("Created 8 premium products successfully!")
