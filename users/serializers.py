from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import User, Role, Branch, SalesTarget


class BranchSerializer(serializers.ModelSerializer):
    employee_count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Branch
        fields = [
            "id", "name", "address", "phone", "is_active",
            "latitude", "longitude", "employee_count", "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    def get_employee_count(self, obj):
        return obj.employees.filter(is_active=True, is_deleted=False).count()


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = [
            "id", "name", "role_type",
            "can_view_reports", "can_manage_products", "can_manage_inventory",
            "can_manage_users", "can_view_finance", "can_manage_finance",
            "can_make_sales", "can_give_discount", "can_view_cost_price",
            "can_manage_customers", "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False, validators=[validate_password])
    role_detail = RoleSerializer(source="role", read_only=True)
    branch_detail = BranchSerializer(source="branch", read_only=True)
    full_name = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = [
            "id", "username", "first_name", "last_name", "email",
            "phone", "avatar",
            "role", "role_detail",
            "branch", "branch_detail",
            "salary", "sales_bonus_percent",
            "is_active", "password",
            "full_name", "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    def create(self, validated_data):
        password = validated_data.pop("password", None)
        user = User(**validated_data)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance


class SalesTargetSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source="user.full_name", read_only=True)
    branch_name = serializers.CharField(source="branch.name", read_only=True)

    class Meta:
        model = SalesTarget
        fields = [
            "id", "user", "user_name", "branch", "branch_name",
            "period_type", "target_amount", "start_date", "end_date",
            "notes", "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    def validate(self, attrs):
        if not attrs.get("user") and not attrs.get("branch"):
            raise serializers.ValidationError("Xodim yoki filial ko'rsatilishi shart.")
        if attrs.get("start_date") and attrs.get("end_date"):
            if attrs["start_date"] > attrs["end_date"]:
                raise serializers.ValidationError(
                    "Boshlanish sanasi tugash sanasidan oldin bo'lishi kerak."
                )
        return attrs
