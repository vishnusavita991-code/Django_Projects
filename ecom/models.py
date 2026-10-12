from django.db import models
from django.contrib.auth.models import User
# Create your models here.
class Customer(models.Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE)
    profile_pic= models.ImageField(upload_to='profile_pic/CustomerProfilePic/',null=True,blank=True)
    address = models.CharField(max_length=40)
    mobile = models.CharField(max_length=20,null=False)
    @property
    def get_name(self):
        return self.user.first_name+" "+self.user.last_name
    @property
    def get_id(self):
        return self.user.id
    def __str__(self):
        return self.user.first_name


class Product(models.Model):
    CATEGORIES = (
        ('Electronics', 'Electronics'),
        ('Fashion', 'Fashion'),
        ('Home & Living', 'Home & Living'),
        ('Accessories', 'Accessories'),
        ('Gadgets', 'Gadgets'),
    )
    name=models.CharField(max_length=100)
    product_image= models.ImageField(upload_to='product_image/',null=True,blank=True)
    price = models.PositiveIntegerField()
    original_price = models.PositiveIntegerField(null=True, blank=True)
    category = models.CharField(max_length=50, choices=CATEGORIES, default='Electronics')
    stock = models.PositiveIntegerField(default=25)
    rating = models.FloatField(default=4.5)
    reviews_count = models.PositiveIntegerField(default=18)
    description=models.TextField(max_length=500, blank=True, default='')

    @property
    def discount_percent(self):
        if self.original_price and self.original_price > self.price:
            return round(((self.original_price - self.price) / self.original_price) * 100)
        return 0

    def __str__(self):
        return self.name


class Orders(models.Model):
    STATUS =(
        ('Pending','Pending'),
        ('Order Confirmed','Order Confirmed'),
        ('Out for Delivery','Out for Delivery'),
        ('Delivered','Delivered'),
    )
    PAYMENT_CHOICES = (
        ('Card / Online', 'Card / Online'),
        ('UPI / QR', 'UPI / QR'),
        ('Cash on Delivery', 'Cash on Delivery'),
    )
    customer=models.ForeignKey('Customer', on_delete=models.CASCADE,null=True)
    product=models.ForeignKey('Product',on_delete=models.CASCADE,null=True)
    email = models.CharField(max_length=50,null=True)
    address = models.CharField(max_length=500,null=True)
    mobile = models.CharField(max_length=20,null=True)
    order_date= models.DateField(auto_now_add=True,null=True)
    status=models.CharField(max_length=50,null=True,choices=STATUS, default='Pending')
    quantity = models.PositiveIntegerField(default=1)
    total_price = models.PositiveIntegerField(null=True, blank=True)
    payment_method = models.CharField(max_length=50, choices=PAYMENT_CHOICES, default='Card / Online')


class Feedback(models.Model):
    name=models.CharField(max_length=40)
    feedback=models.CharField(max_length=500)
    date= models.DateField(auto_now_add=True,null=True)
    def __str__(self):
        return self.name
