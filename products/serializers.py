from rest_framework import serializers
from django.db.models import Sum
from .models import (
    Category, Brand, Unit, Product, ProductAttribute,
    ProductAttributeValue, ProductVariant, ProductImage,
    PriceList, PriceListItem,
)


class CategorySerializer(serializers.ModelSerializer):
    parent_name = serializers.CharField(source="parent.name", read_only=True)
    children_count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Category
        fields = [
            "id", "name", "parent", "parent_name",
            "icon", "sort_order", "children_count", "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    def get_children_count(self, obj):
        return obj.children.filter(is_deleted=False).count()


class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ["id", "name", "logo", "country", "created_at"]
        read_only_fields = ["id", "created_at"]


class UnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Unit
        fields = ["id", "name", "short_name", "created_at"]
        read_only_fields = ["id", "created_at"]


class ProductAttributeValueSerializer(serializers.ModelSerializer):
    attribute_name = serializers.CharField(source="attribute.name", read_only=True)

    class Meta:
        model = ProductAttributeValue
        fields = ["id", "attribute", "attribute_name", "value"]
        read_only_fields = ["id"]


class ProductAttributeSerializer(serializers.ModelSerializer):
    values = ProductAttributeValueSerializer(many=True, read_only=True)

    class Meta:
        model = ProductAttribute
        fields = ["id", "name", "values"]
        read_only_fields = ["id"]


class ProductVariantSerializer(serializers.ModelSerializer):
    attributes = ProductAttributeValueSerializer(many=True, read_only=True)
    effective_selling_price = serializers.SerializerMethodField(read_only=True)
    effective_cost_price = serializers.SerializerMethodField(read_only=True)
    total_stock = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = ProductVariant
        fields = [
            "id", "product", "sku", "barcode", "attributes",
            "cost_price", "selling_price",
            "effective_selling_price", "effective_cost_price",
            "total_stock", "image", "is_active",
        ]
        read_only_fields = ["id"]

    def get_effective_selling_price(self, obj):
        return obj.get_selling_price()

    def get_effective_cost_price(self, obj):
        return obj.get_cost_price()

    def get_total_stock(self, obj):
        result = obj.stocks.filter(is_deleted=False).aggregate(total=Sum("quantity"))
        return result["total"] or 0


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ["id", "product", "image", "is_main", "sort_order"]
        read_only_fields = ["id"]


class ProductSerializer(serializers.ModelSerializer):
    variants = ProductVariantSerializer(many=True, read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    category_name = serializers.CharField(source="category.name", read_only=True)
    brand_name = serializers.CharField(source="brand.name", read_only=True)
    unit_short = serializers.CharField(source="unit.short_name", read_only=True)
    profit_margin = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Product
        fields = [
            "id", "name", "description",
            "category", "category_name",
            "brand", "brand_name",
            "unit", "unit_short",
            "image",
            "cost_price", "selling_price", "min_selling_price", "wholesale_price",
            "min_stock_level", "has_variants", "is_active", "is_service",
            "profit_margin", "variants", "images", "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    def get_profit_margin(self, obj):
        return round(obj.profit_margin, 2)


class PriceListItemSerializer(serializers.ModelSerializer):
    variant_sku = serializers.CharField(source="variant.sku", read_only=True)

    class Meta:
        model = PriceListItem
        fields = ["id", "price_list", "variant", "variant_sku", "price"]
        read_only_fields = ["id"]


class PriceListSerializer(serializers.ModelSerializer):
    items = PriceListItemSerializer(many=True, read_only=True)

    class Meta:
        model = PriceList
        fields = ["id", "name", "description", "is_default", "items", "created_at"]
        read_only_fields = ["id", "created_at"]
