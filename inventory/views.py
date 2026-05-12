from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db.models import Q, F
from drf_spectacular.utils import extend_schema
from core.schema import schema_view
from .models import (
    Warehouse, Stock, Supplier, PurchaseOrder,
    StockTransfer, Inventory, WriteOff,
)
from .serializers import (
    WarehouseSerializer, StockSerializer, SupplierSerializer,
    PurchaseOrderSerializer, StockTransferSerializer,
    InventorySerializer, WriteOffSerializer,
)


@schema_view(
    "Warehouses",
    list="Omborxonalar ro'yxati",
    create="Yangi omborxona yaratish",
    retrieve="Omborxona ma'lumotlari",
    update="Omborxonani yangilash",
    partial_update="Omborxonani qisman yangilash",
    destroy="Omborxonani o'chirish",
)
class WarehouseViewSet(viewsets.ModelViewSet):
    queryset = Warehouse.objects.filter(is_deleted=False).select_related("branch")
    serializer_class = WarehouseSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        branch = self.request.query_params.get("branch")
        if branch:
            qs = qs.filter(branch_id=branch)
        is_active = self.request.query_params.get("is_active")
        if is_active is not None:
            qs = qs.filter(is_active=is_active.lower() == "true")
        return qs

    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.save()


@schema_view(
    "Stock",
    list="Tovar qoldiqlari ro'yxati",
    retrieve="Tovar qoldig'i ma'lumotlari",
)
class StockViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = (
        Stock.objects.filter(is_deleted=False)
        .select_related("warehouse", "variant__product")
    )
    serializer_class = StockSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        warehouse = self.request.query_params.get("warehouse")
        if warehouse:
            qs = qs.filter(warehouse_id=warehouse)
        variant = self.request.query_params.get("variant")
        if variant:
            qs = qs.filter(variant_id=variant)
        search = self.request.query_params.get("search")
        if search:
            qs = qs.filter(
                Q(variant__sku__icontains=search)
                | Q(variant__barcode__icontains=search)
                | Q(variant__product__name__icontains=search)
            )
        return qs

    @extend_schema(tags=["Stock"], summary="Minimal zaxiradan kam tovarlar")
    @action(detail=False, methods=["get"], url_path="low-stock")
    def low_stock(self, request):
        qs = self.get_queryset().filter(
            quantity__lte=F("variant__product__min_stock_level"),
            quantity__gt=0,
        )
        return Response(self.get_serializer(qs, many=True).data)

    @extend_schema(tags=["Stock"], summary="Tugagan (nol) tovarlar")
    @action(detail=False, methods=["get"], url_path="out-of-stock")
    def out_of_stock(self, request):
        qs = self.get_queryset().filter(quantity__lte=0)
        return Response(self.get_serializer(qs, many=True).data)


@schema_view(
    "Suppliers",
    list="Yetkazib beruvchilar ro'yxati",
    create="Yangi yetkazib beruvchi qo'shish",
    retrieve="Yetkazib beruvchi ma'lumotlari",
    update="Yetkazib beruvchini yangilash",
    partial_update="Yetkazib beruvchini qisman yangilash",
    destroy="Yetkazib beruvchini o'chirish",
)
class SupplierViewSet(viewsets.ModelViewSet):
    queryset = Supplier.objects.filter(is_deleted=False)
    serializer_class = SupplierSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        search = self.request.query_params.get("search")
        if search:
            qs = qs.filter(
                Q(name__icontains=search)
                | Q(phone__icontains=search)
                | Q(contact_person__icontains=search)
            )
        return qs

    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.save()


@schema_view(
    "Purchase Orders",
    list="Kirim buyurtmalari ro'yxati",
    create="Yangi kirim buyurtmasi yaratish",
    retrieve="Kirim buyurtmasi tafsilotlari",
    update="Kirim buyurtmasini yangilash",
    partial_update="Kirim buyurtmasini qisman yangilash",
    destroy="Kirim buyurtmasini o'chirish",
)
class PurchaseOrderViewSet(viewsets.ModelViewSet):
    queryset = (
        PurchaseOrder.objects.filter(is_deleted=False)
        .select_related("supplier", "warehouse", "created_by")
        .prefetch_related("items")
    )
    serializer_class = PurchaseOrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        supplier = self.request.query_params.get("supplier")
        if supplier:
            qs = qs.filter(supplier_id=supplier)
        warehouse = self.request.query_params.get("warehouse")
        if warehouse:
            qs = qs.filter(warehouse_id=warehouse)
        order_status = self.request.query_params.get("status")
        if order_status:
            qs = qs.filter(status=order_status)
        return qs

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.save()

    @extend_schema(tags=["Purchase Orders"], summary="Tovarni qabul qilish va omborga kiritish")
    @action(detail=True, methods=["post"], url_path="receive")
    def receive(self, request, pk=None):
        order = self.get_object()
        if order.status in [PurchaseOrder.Status.RECEIVED, PurchaseOrder.Status.CANCELLED]:
            return Response(
                {"detail": "Bu buyurtma allaqachon yakunlangan yoki bekor qilingan."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        order.status = PurchaseOrder.Status.RECEIVED
        order.received_date = timezone.now().date()
        order.save()
        return Response(self.get_serializer(order).data)

    @extend_schema(tags=["Purchase Orders"], summary="Kirim buyurtmasini bekor qilish")
    @action(detail=True, methods=["post"], url_path="cancel")
    def cancel(self, request, pk=None):
        order = self.get_object()
        if order.status == PurchaseOrder.Status.RECEIVED:
            return Response(
                {"detail": "Qabul qilingan buyurtmani bekor qilib bo'lmaydi."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        order.status = PurchaseOrder.Status.CANCELLED
        order.save()
        return Response(self.get_serializer(order).data)


@schema_view(
    "Stock Transfers",
    list="Tovar ko'chirishlar ro'yxati",
    create="Yangi tovar ko'chirish yaratish",
    retrieve="Tovar ko'chirish tafsilotlari",
    update="Tovar ko'chirishni yangilash",
    partial_update="Tovar ko'chirishni qisman yangilash",
    destroy="Tovar ko'chirishni o'chirish",
)
class StockTransferViewSet(viewsets.ModelViewSet):
    queryset = (
        StockTransfer.objects.filter(is_deleted=False)
        .select_related("from_warehouse", "to_warehouse", "created_by")
        .prefetch_related("items")
    )
    serializer_class = StockTransferSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        transfer_status = self.request.query_params.get("status")
        if transfer_status:
            qs = qs.filter(status=transfer_status)
        from_wh = self.request.query_params.get("from_warehouse")
        if from_wh:
            qs = qs.filter(from_warehouse_id=from_wh)
        to_wh = self.request.query_params.get("to_warehouse")
        if to_wh:
            qs = qs.filter(to_warehouse_id=to_wh)
        return qs

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.save()

    @extend_schema(tags=["Stock Transfers"], summary="Transferni yakunlash")
    @action(detail=True, methods=["post"], url_path="complete")
    def complete(self, request, pk=None):
        transfer = self.get_object()
        if transfer.status == StockTransfer.Status.COMPLETED:
            return Response(
                {"detail": "Transfer allaqachon yakunlangan."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        transfer.status = StockTransfer.Status.COMPLETED
        transfer.save()
        return Response(self.get_serializer(transfer).data)


@schema_view(
    "Inventory",
    list="Inventarizatsiyalar ro'yxati",
    create="Yangi inventarizatsiya boshlash",
    retrieve="Inventarizatsiya tafsilotlari",
    update="Inventarizatsiyani yangilash",
    partial_update="Inventarizatsiyani qisman yangilash",
    destroy="Inventarizatsiyani o'chirish",
)
class InventoryViewSet(viewsets.ModelViewSet):
    queryset = (
        Inventory.objects.filter(is_deleted=False)
        .select_related("warehouse", "created_by")
        .prefetch_related("items")
    )
    serializer_class = InventorySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        warehouse = self.request.query_params.get("warehouse")
        if warehouse:
            qs = qs.filter(warehouse_id=warehouse)
        inv_status = self.request.query_params.get("status")
        if inv_status:
            qs = qs.filter(status=inv_status)
        return qs

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.save()

    @extend_schema(tags=["Inventory"], summary="Inventarizatsiyani yakunlash")
    @action(detail=True, methods=["post"], url_path="complete")
    def complete(self, request, pk=None):
        inventory = self.get_object()
        if inventory.status == Inventory.Status.COMPLETED:
            return Response(
                {"detail": "Inventarizatsiya allaqachon yakunlangan."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        inventory.status = Inventory.Status.COMPLETED
        inventory.completed_at = timezone.now()
        inventory.save()
        return Response(self.get_serializer(inventory).data)


@schema_view(
    "Write-offs",
    list="Hisobdan chiqarishlar ro'yxati",
    create="Yangi hisobdan chiqarish",
    retrieve="Hisobdan chiqarish tafsilotlari",
    update="Hisobdan chiqarishni yangilash",
    partial_update="Hisobdan chiqarishni qisman yangilash",
    destroy="Hisobdan chiqarishni o'chirish",
)
class WriteOffViewSet(viewsets.ModelViewSet):
    queryset = (
        WriteOff.objects.filter(is_deleted=False)
        .select_related("warehouse", "variant__product", "created_by")
    )
    serializer_class = WriteOffSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        warehouse = self.request.query_params.get("warehouse")
        if warehouse:
            qs = qs.filter(warehouse_id=warehouse)
        reason = self.request.query_params.get("reason")
        if reason:
            qs = qs.filter(reason=reason)
        return qs

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.save()
