from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductViewSet, CartViewSet, CategoryViewSet
from .views import send_otp, verify_otp_and_create_superuser

router = DefaultRouter()
router.register(r'products', ProductViewSet)
router.register(r'carts', CartViewSet)
router.register(r'categories', CategoryViewSet)

urlpatterns = [
    path('', include(router.urls)),   # ✅ include router
    path('send-otp/', send_otp),
    path('verify-otp/', verify_otp_and_create_superuser),
]