from django.db import models
from django.contrib.auth.models import User
from PIL import Image, UnidentifiedImageError
from io import BytesIO
from django.core.files.base import ContentFile


class Category(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Cart(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)

    def total_price(self):
        return sum(item.product.price * item.quantity for item in self.items.all())

    def __str__(self):
        return str(self.id)


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.product.name} ({self.quantity})"


class Order(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order {self.id}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)


# ✅ FIXED PRODUCT IMAGE MODEL
class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='products/')
    thumbnail = models.ImageField(upload_to='products/thumbnails/', null=True, blank=True)

def save(self, *args, **kwargs):
    super().save(*args, **kwargs)

    if self.image:
        try:
            img = Image.open(self.image)

            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")

            img.thumbnail((200, 200))

            thumb_io = BytesIO()
            img.save(thumb_io, format='JPEG', quality=85)

            thumb_name = f"thumb_{self.image.name}"

            self.thumbnail.save(
                thumb_name,
                ContentFile(thumb_io.getvalue()),
                save=False
            )

            super().save(*args, **kwargs)

        except UnidentifiedImageError:
            # ✅ Skip thumbnail if invalid image (important for tests)
            pass
import random

class OTP(models.Model):
    email = models.EmailField()
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email