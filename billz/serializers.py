from rest_framework import serializers
from .models import (
    CustomerGroup, Customer, CashRegister, CashSession,
    Sale, SaleItem, SaleReturn, SaleReturnItem,
    PaymentMethod, Payment, ExpenseCategory, Expense, CashMovement,
)


class CustomerGroupSerializer(serializers.ModelSerializer):
    customer_count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = CustomerGroup
        fields = [
            "id", "name", "discount_percent", "cashback_percent",
            "price_list", "color", "customer_count", "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    def get_customer_count(self, obj):
        return obj.customers.filter(is_deleted=False, is_active=True).count()


class CustomerSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(read_only=True)
    group_name = serializers.CharField(source="group.name", read_only=True)

    class Meta:
        model = Customer
        fields = [
            "id", "first_name", "last_name", "full_name",
            "phone", "phone2", "email", "birthday", "gender",
            "address", "group", "group_name", "branch",
            "notes", "balance", "total_purchases", "bonus_points",
            "is_active", "created_by", "created_at",
        ]
        read_only_fields = ["id", "balance", "total_purchases", "bonus_points", "created_at"]


class CashRegisterSerializer(serializers.ModelSerializer):
    branch_name = serializers.CharField(source="branch.name", read_only=True)

    class Meta:
        model = CashRegister
        fields = ["id", "name", "branch", "branch_name", "is_active", "created_at"]
        read_only_fields = ["id", "created_at"]


class CashSessionSerializer(serializers.ModelSerializer):
    cashier_name = serializers.CharField(source="cashier.full_name", read_only=True)
    cash_register_name = serializers.CharField(source="cash_register.name", read_only=True)

    class Meta:
        model = CashSession
        fields = [
            "id", "cash_register", "cash_register_name",
            "cashier", "cashier_name",
            "status", "opening_balance", "closing_balance",
            "opened_at", "closed_at", "notes",
        ]
        read_only_fields = ["id", "opened_at"]


class PaymentMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentMethod
        fields = ["id", "name", "is_cash", "is_active", "sort_order", "icon"]
        read_only_fields = ["id"]


class SaleItemSerializer(serializers.ModelSerializer):
    variant_name = serializers.SerializerMethodField(read_only=True)
    profit = serializers.DecimalField(max_digits=15, decimal_places=2, read_only=True)

    class Meta:
        model = SaleItem
        fields = [
            "id", "sale", "variant", "variant_name", "quantity",
            "unit_price", "cost_price", "discount_percent",
            "discount_amount", "total_price", "profit",
        ]
        read_only_fields = ["id", "cost_price", "profit"]

    def get_variant_name(self, obj):
        return str(obj.variant)


class PaymentSerializer(serializers.ModelSerializer):
    payment_method_name = serializers.CharField(source="payment_method.name", read_only=True)

    class Meta:
        model = Payment
        fields = [
            "id", "sale", "payment_method", "payment_method_name",
            "amount", "reference", "notes",
        ]
        read_only_fields = ["id"]


class SaleSerializer(serializers.ModelSerializer):
    items = SaleItemSerializer(many=True, read_only=True)
    payments = PaymentSerializer(many=True, read_only=True)
    customer_name = serializers.CharField(source="customer.full_name", read_only=True)
    seller_name = serializers.CharField(source="seller.full_name", read_only=True)
    debt_amount = serializers.DecimalField(max_digits=15, decimal_places=2, read_only=True)

    class Meta:
        model = Sale
        fields = [
            "id", "receipt_number", "branch", "warehouse", "cash_session",
            "customer", "customer_name", "seller", "seller_name",
            "status", "payment_status",
            "subtotal", "discount_amount", "discount_percent",
            "total_amount", "paid_amount", "change_amount",
            "bonus_used", "bonus_earned", "debt_amount",
            "sale_date", "notes", "is_layaway", "layaway_until",
            "items", "payments",
        ]
        read_only_fields = [
            "id", "receipt_number", "sale_date",
            "subtotal", "total_amount", "paid_amount",
            "change_amount", "bonus_earned", "payment_status", "debt_amount",
        ]


class SaleReturnItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = SaleReturnItem
        fields = ["id", "sale_item", "quantity", "unit_price", "total_price"]
        read_only_fields = ["id", "unit_price", "total_price"]


class SaleReturnSerializer(serializers.ModelSerializer):
    items = SaleReturnItemSerializer(many=True, read_only=True)
    cashier_name = serializers.CharField(source="cashier.full_name", read_only=True)

    class Meta:
        model = SaleReturn
        fields = [
            "id", "sale", "return_number", "cashier", "cashier_name",
            "reason", "total_amount", "refund_method", "items", "created_at",
        ]
        read_only_fields = ["id", "return_number", "total_amount", "created_at"]


class ExpenseCategorySerializer(serializers.ModelSerializer):
    parent_name = serializers.CharField(source="parent.name", read_only=True)

    class Meta:
        model = ExpenseCategory
        fields = ["id", "name", "parent", "parent_name", "icon", "color"]
        read_only_fields = ["id"]


class ExpenseSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name", read_only=True)
    branch_name = serializers.CharField(source="branch.name", read_only=True)
    created_by_name = serializers.CharField(source="created_by.full_name", read_only=True)

    class Meta:
        model = Expense
        fields = [
            "id", "branch", "branch_name", "category", "category_name",
            "cash_session", "amount", "payment_method",
            "description", "expense_date",
            "created_by", "created_by_name", "receipt_image", "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class CashMovementSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source="created_by.full_name", read_only=True)

    class Meta:
        model = CashMovement
        fields = [
            "id", "cash_session", "movement_type", "amount",
            "description", "created_by", "created_by_name", "created_at",
        ]
        read_only_fields = ["id", "created_at"]
