from rest_framework import serializers
from .models import Product, Category
from .models import Cart, CartItem, Product
from .models import ProductImage

class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = '__all__'

    def validate_image(self, value):
        # File size (max 2MB)
        if value.size > 2 * 1024 * 1024:
            raise serializers.ValidationError("Image too large (max 2MB)")

        # File type
        if value.content_type not in ['image/jpeg', 'image/png']:
            raise serializers.ValidationError("Only JPG and PNG allowed")

        return value

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class ProductSerializer(serializers.ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all()
    )

    class Meta:
        model = Product
        fields = '__all__'
class CartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = '__all__'

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)

    class Meta:
        model = Cart
        fields = '__all__'
class CartSerializer(serializers.ModelSerializer):
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ['id', 'items', 'total_price']

    def get_total_price(self, obj):
        return obj.total_price()
class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = '__all__'

    def validate_image(self, value):
        # File size (max 2MB)
        if value.size > 2 * 1024 * 1024:
            raise serializers.ValidationError("Image too large (max 2MB)")

        # File type
        if value.content_type not in ['image/jpeg', 'image/png']:
            raise serializers.ValidationError("Only JPG and PNG allowed")

        return value