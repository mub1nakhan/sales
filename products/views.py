from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from drf_spectacular.utils import extend_schema
from core.schema import schema_view
from .models import (
    Category, Brand, Unit, Product, ProductAttribute,
    ProductVariant, PriceList,
)
from .serializers import (
    CategorySerializer, BrandSerializer, UnitSerializer,
    ProductSerializer, ProductAttributeSerializer,
    ProductVariantSerializer, PriceListSerializer,
)


@schema_view(
    "Categories",
    list="Kategoriyalar ro'yxati",
    create="Yangi kategoriya yaratish",
    retrieve="Kategoriya ma'lumotlari",
    update="Kategoriyani yangilash",
    partial_update="Kategoriyani qisman yangilash",
    destroy="Kategoriyani o'chirish",
)
class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.filter(is_deleted=False).select_related("parent")
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        parent = self.request.query_params.get("parent")
        if parent == "root":
            qs = qs.filter(parent__isnull=True)
        elif parent:
            qs = qs.filter(parent_id=parent)
        search = self.request.query_params.get("search")
        if search:
            qs = qs.filter(name__icontains=search)
        return qs.order_by("sort_order", "name")

    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.save()

    @extend_schema(tags=["Categories"], summary="Kategoriya bolalari (ichki kategoriyalar)")
    @action(detail=True, methods=["get"], url_path="children")
    def children(self, request, pk=None):
        category = self.get_object()
        qs = Category.objects.filter(parent=category, is_deleted=False)
        return Response(self.get_serializer(qs, many=True).data)


@schema_view(
    "Brands",
    list="Brendlar ro'yxati",
    create="Yangi brend yaratish",
    retrieve="Brend ma'lumotlari",
    update="Brendni yangilash",
    partial_update="Brendni qisman yangilash",
    destroy="Brendni o'chirish",
)
class BrandViewSet(viewsets.ModelViewSet):
    queryset = Brand.objects.filter(is_deleted=False)
    serializer_class = BrandSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        search = self.request.query_params.get("search")
        if search:
            qs = qs.filter(Q(name__icontains=search) | Q(country__icontains=search))
        return qs

    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.save()


@schema_view(
    "Units",
    list="O'lchov birliklari ro'yxati",
    create="Yangi o'lchov birligi",
    retrieve="O'lchov birligi ma'lumotlari",
    update="O'lchov birligini yangilash",
    partial_update="O'lchov birligini qisman yangilash",
    destroy="O'lchov birligini o'chirish",
)
class UnitViewSet(viewsets.ModelViewSet):
    queryset = Unit.objects.filter(is_deleted=False)
    serializer_class = UnitSerializer
    permission_classes = [IsAuthenticated]

    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.save()


@schema_view(
    "Product Attributes",
    list="Mahsulot xususiyatlari ro'yxati",
    create="Yangi xususiyat turi yaratish",
    retrieve="Xususiyat turi ma'lumotlari",
    update="Xususiyat turini yangilash",
    partial_update="Xususiyat turini qisman yangilash",
    destroy="Xususiyat turini o'chirish",
)
class ProductAttributeViewSet(viewsets.ModelViewSet):
    queryset = ProductAttribute.objects.filter(is_deleted=False).prefetch_related("values")
    serializer_class = ProductAttributeSerializer
    permission_classes = [IsAuthenticated]

    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.save()


@schema_view(
    "Products",
    list="Mahsulotlar ro'yxati",
    create="Yangi mahsulot qo'shish",
    retrieve="Mahsulot tafsilotlari",
    update="Mahsulotni yangilash",
    partial_update="Mahsulotni qisman yangilash",
    destroy="Mahsulotni o'chirish",
)
class ProductViewSet(viewsets.ModelViewSet):
    queryset = (
        Product.objects.filter(is_deleted=False)
        .select_related("category", "brand", "unit")
        .prefetch_related("variants", "images")
    )
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        category = self.request.query_params.get("category")
        if category:
            qs = qs.filter(category_id=category)
        brand = self.request.query_params.get("brand")
        if brand:
            qs = qs.filter(brand_id=brand)
        is_active = self.request.query_params.get("is_active")
        if is_active is not None:
            qs = qs.filter(is_active=is_active.lower() == "true")
        is_service = self.request.query_params.get("is_service")
        if is_service is not None:
            qs = qs.filter(is_service=is_service.lower() == "true")
        search = self.request.query_params.get("search")
        if search:
            qs = qs.filter(
                Q(name__icontains=search)
                | Q(variants__sku__icontains=search)
                | Q(variants__barcode__icontains=search)
            ).distinct()
        return qs

    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.save()

    @extend_schema(tags=["Products"], summary="Mahsulot variantlari ro'yxati")
    @action(detail=True, methods=["get"], url_path="variants")
    def variants(self, request, pk=None):
        product = self.get_object()
        qs = product.variants.filter(is_deleted=False, is_active=True)
        return Response(ProductVariantSerializer(qs, many=True).data)


@schema_view(
    "Product Variants",
    list="Variantlar ro'yxati",
    create="Yangi variant yaratish",
    retrieve="Variant tafsilotlari",
    update="Variantni yangilash",
    partial_update="Variantni qisman yangilash",
    destroy="Variantni o'chirish",
)
class ProductVariantViewSet(viewsets.ModelViewSet):
    queryset = (
        ProductVariant.objects.filter(is_deleted=False)
        .select_related("product")
        .prefetch_related("attributes", "stocks")
    )
    serializer_class = ProductVariantSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        product = self.request.query_params.get("product")
        if product:
            qs = qs.filter(product_id=product)
        barcode = self.request.query_params.get("barcode")
        if barcode:
            qs = qs.filter(barcode=barcode)
        sku = self.request.query_params.get("sku")
        if sku:
            qs = qs.filter(sku__icontains=sku)
        return qs

    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.save()


@schema_view(
    "Price Lists",
    list="Narxlar ro'yxati",
    create="Yangi narxlar ro'yxati yaratish",
    retrieve="Narxlar ro'yxati tafsilotlari",
    update="Narxlar ro'yxatini yangilash",
    partial_update="Narxlar ro'yxatini qisman yangilash",
    destroy="Narxlar ro'yxatini o'chirish",
)
class PriceListViewSet(viewsets.ModelViewSet):
    queryset = PriceList.objects.filter(is_deleted=False).prefetch_related("items")
    serializer_class = PriceListSerializer
    permission_classes = [IsAuthenticated]

    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.save()
