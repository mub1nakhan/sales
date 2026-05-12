from rest_framework import serializers
from .models import (
    Warehouse, Stock, Supplier, PurchaseOrder, PurchaseOrderItem,
    StockTransfer, StockTransferItem, Inventory, InventoryItem, WriteOff,
)


class WarehouseSerializer(serializers.ModelSerializer):
    branch_name = serializers.CharField(source="branch.name", read_only=True)

    class Meta:
        model = Warehouse
        fields = [
            "id", "name", "branch", "branch_name",
            "address", "is_active", "is_main", "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class StockSerializer(serializers.ModelSerializer):
    warehouse_name = serializers.CharField(source="warehouse.name", read_only=True)
    variant_sku = serializers.CharField(source="variant.sku", read_only=True)
    product_name = serializers.CharField(source="variant.product.name", read_only=True)
    available_quantity = serializers.DecimalField(
        max_digits=12, decimal_places=3, read_only=True
    )

    class Meta:
        model = Stock
        fields = [
            "id", "warehouse", "warehouse_name",
            "variant", "variant_sku", "product_name",
            "quantity", "reserved_quantity", "available_quantity",
        ]
        read_only_fields = ["id", "available_quantity"]


class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = [
            "id", "name", "contact_person", "phone", "email",
            "address", "inn", "notes", "balance", "created_at",
        ]
        read_only_fields = ["id", "balance", "created_at"]


class PurchaseOrderItemSerializer(serializers.ModelSerializer):
    variant_name = serializers.SerializerMethodField(read_only=True)
    total_cost = serializers.DecimalField(max_digits=15, decimal_places=2, read_only=True)

    class Meta:
        model = PurchaseOrderItem
        fields = [
            "id", "order", "variant", "variant_name",
            "ordered_quantity", "received_quantity",
            "cost_price", "selling_price", "total_cost",
        ]
        read_only_fields = ["id", "total_cost"]

    def get_variant_name(self, obj):
        return str(obj.variant)


class PurchaseOrderSerializer(serializers.ModelSerializer):
    items = PurchaseOrderItemSerializer(many=True, read_only=True)
    supplier_name = serializers.CharField(source="supplier.name", read_only=True)
    warehouse_name = serializers.CharField(source="warehouse.name", read_only=True)
    debt_amount = serializers.DecimalField(max_digits=15, decimal_places=2, read_only=True)

    class Meta:
        model = PurchaseOrder
        fields = [
            "id", "order_number", "supplier", "supplier_name",
            "warehouse", "warehouse_name",
            "status", "order_date", "expected_date", "received_date",
            "total_amount", "paid_amount", "debt_amount",
            "notes", "created_by", "items", "created_at",
        ]
        read_only_fields = ["id", "debt_amount", "created_at"]


class StockTransferItemSerializer(serializers.ModelSerializer):
    variant_name = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = StockTransferItem
        fields = [
            "id", "transfer", "variant", "variant_name",
            "requested_quantity", "sent_quantity", "received_quantity",
        ]
        read_only_fields = ["id"]

    def get_variant_name(self, obj):
        return str(obj.variant)


class StockTransferSerializer(serializers.ModelSerializer):
    items = StockTransferItemSerializer(many=True, read_only=True)
    from_warehouse_name = serializers.CharField(source="from_warehouse.name", read_only=True)
    to_warehouse_name = serializers.CharField(source="to_warehouse.name", read_only=True)

    class Meta:
        model = StockTransfer
        fields = [
            "id", "transfer_number",
            "from_warehouse", "from_warehouse_name",
            "to_warehouse", "to_warehouse_name",
            "status", "transfer_date", "notes",
            "created_by", "items", "created_at",
        ]
        read_only_fields = ["id", "transfer_number", "created_at"]

    def validate(self, attrs):
        if attrs.get("from_warehouse") == attrs.get("to_warehouse"):
            raise serializers.ValidationError(
                "Qayerdan va qayerga bir xil omborxona bo'lmasligi kerak."
            )
        return attrs


class InventoryItemSerializer(serializers.ModelSerializer):
    variant_name = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = InventoryItem
        fields = [
            "id", "inventory", "variant", "variant_name",
            "system_quantity", "actual_quantity", "difference",
        ]
        read_only_fields = ["id", "difference"]

    def get_variant_name(self, obj):
        return str(obj.variant)


class InventorySerializer(serializers.ModelSerializer):
    items = InventoryItemSerializer(many=True, read_only=True)
    warehouse_name = serializers.CharField(source="warehouse.name", read_only=True)

    class Meta:
        model = Inventory
        fields = [
            "id", "inventory_number", "warehouse", "warehouse_name",
            "status", "started_at", "completed_at", "notes",
            "created_by", "items",
        ]
        read_only_fields = ["id", "inventory_number", "started_at"]


class WriteOffSerializer(serializers.ModelSerializer):
    warehouse_name = serializers.CharField(source="warehouse.name", read_only=True)
    variant_name = serializers.SerializerMethodField(read_only=True)
    created_by_name = serializers.CharField(source="created_by.full_name", read_only=True)

    class Meta:
        model = WriteOff
        fields = [
            "id", "write_off_number", "warehouse", "warehouse_name",
            "variant", "variant_name",
            "quantity", "reason", "description", "total_loss",
            "created_by", "created_by_name", "created_at",
        ]
        read_only_fields = ["id", "write_off_number", "created_at"]

    def get_variant_name(self, obj):
        return str(obj.variant)
