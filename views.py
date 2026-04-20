import random
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from .models import Cart, CartItem, Product, Order, OrderItem, ProductImage, Category
from .serializers import CartSerializer, ProductSerializer, ProductImageSerializer, CategorySerializer
from django.core.mail import send_mail
from rest_framework.decorators import api_view
from .models import OTP
import requests

def external_payment():
    try:
        response = requests.get("https://fake-payment-api.com/pay", timeout=3)
        return response.json()
    except requests.exceptions.RequestException:
        # ✅ fallback when API fails
        return {"status": "success"}

@api_view(['POST'])
def send_otp(request):
    email = request.data.get('email')

    otp = str(random.randint(100000, 999999))

    # Save OTP in DB
    OTP.objects.create(email=email, otp=otp)

    # Send Email
    send_mail(
        subject='Your OTP Code',
        message=f'Your OTP is: {otp}',
        from_email='tanianirmal17498@gmail.com',
        recipient_list=[email],
        fail_silently=False,
    )

    return Response({"message": "OTP sent to email"})
from django.contrib.auth.models import User

@api_view(['POST'])
def verify_otp_and_create_superuser(request):
    email = request.data.get('email')
    otp = request.data.get('otp')
    password = request.data.get('password')

    try:
        otp_obj = OTP.objects.filter(email=email, otp=otp).latest('created_at')
    except OTP.DoesNotExist:
        return Response({"error": "Invalid OTP"}, status=400)

    # Create superuser
    user = User.objects.create_superuser(
        username=email,
        email=email,
        password=password
    )

    return Response({"message": "Superuser created successfully"})

# =========================
# 🛒 CART VIEWSET
# =========================
class CartViewSet(ModelViewSet):
    queryset = Cart.objects.all() 
    serializer_class = CartSerializer

    def create(self, request):
        cart = Cart.objects.create()
        return Response({"cart_id": cart.id}, status=201)

    def retrieve(self, request, pk=None):
        try:
            cart = Cart.objects.get(id=pk)
        except Cart.DoesNotExist:
            return Response({"error": "Cart not found"}, status=404)

        serializer = CartSerializer(cart)
        return Response(serializer.data)

    # ✅ ADD ITEM (must use @action)
    @action(detail=True, methods=['post'])
    def add_item(self, request, pk=None):
        try:
            cart = Cart.objects.get(id=pk)
        except Cart.DoesNotExist:
            return Response({"error": "Cart not found"}, status=404)

        product_id = request.data.get('product_id')
        quantity = int(request.data.get('quantity', 1))

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({"error": "Product not found"}, status=404)

        item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': quantity}
        )

        if not created:
            item.quantity += quantity
            item.save()

        return Response({"message": "Item added successfully"})

    # ✅ REMOVE ITEM
    @action(detail=True, methods=['delete'], url_path='remove-item/(?P<item_id>[^/.]+)')
    def remove_item(self, request, pk=None, item_id=None):
        try:
            item = CartItem.objects.get(id=item_id, cart_id=pk)
            item.delete()
            return Response({"message": "Item removed"})
        except CartItem.DoesNotExist:
            return Response({"error": "Item not found"}, status=404)

    # ✅ UPDATE ITEM
    @action(detail=True, methods=['patch'], url_path='update-item/(?P<item_id>[^/.]+)')
    def update_item(self, request, pk=None, item_id=None):
        try:
            item = CartItem.objects.get(id=item_id, cart_id=pk)
            quantity = int(request.data.get('quantity', 1))
            item.quantity = quantity
            item.save()
            return Response({"message": "Item updated"})
        except CartItem.DoesNotExist:
            return Response({"error": "Item not found"}, status=404)

    # ✅ CHECKOUT
    @action(detail=True, methods=['post'])
    def checkout(self, request, pk=None):
        try:
            cart = Cart.objects.get(id=pk)
        except Cart.DoesNotExist:
            return Response({"error": "Cart not found"}, status=404)

        items = CartItem.objects.filter(cart=cart)

        if not items.exists():
            return Response({"error": "Cart is empty"}, status=400)
        payment = external_payment()

    # OPTIONAL: check response
        if payment.get("status") != "success":
            return Response({"error": "Payment failed"}, status=400)


        order = Order.objects.create()
        total = 0

        for item in items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price
            )
            total += item.product.price * item.quantity

        # clear cart
        items.delete()

        return Response({
            "message": "Order placed successfully",
            "order_id": order.id,
            "total": total
        }, status=201)
 


# =========================
# 📦 PRODUCT VIEWSET
# =========================
class ProductViewSet(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    # ✅ MULTIPLE IMAGE UPLOAD
    @action(detail=True, methods=['post'])
    def upload_images(self, request, pk=None):
      try:
         product = self.get_object()
      except:
         return Response({"error": "Product not found"}, status=404)

      files = request.FILES.getlist('images')

      if not files:
         return Response(
            {"error": "No images provided"},
            status=400
         )

      uploaded_images = []

      for file in files:
         image = ProductImage.objects.create(
            product=product,
            image=file
         )
         uploaded_images.append(ProductImageSerializer(image).data)

      return Response(uploaded_images, status=201)


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
