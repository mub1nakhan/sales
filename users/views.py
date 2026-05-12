from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from drf_spectacular.utils import extend_schema, extend_schema_view
from core.schema import schema_view
from .models import User, Role, Branch, SalesTarget
from .serializers import (
    UserSerializer, RoleSerializer,
    BranchSerializer, SalesTargetSerializer,
)


@schema_view(
    "Branches",
    list="Filiallar ro'yxati",
    create="Yangi filial yaratish",
    retrieve="Filial ma'lumotlari",
    update="Filialni yangilash",
    partial_update="Filialni qisman yangilash",
    destroy="Filialni o'chirish",
)
class BranchViewSet(viewsets.ModelViewSet):
    queryset = Branch.objects.filter(is_deleted=False)
    serializer_class = BranchSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        is_active = self.request.query_params.get("is_active")
        if is_active is not None:
            qs = qs.filter(is_active=is_active.lower() == "true")
        search = self.request.query_params.get("search")
        if search:
            qs = qs.filter(Q(name__icontains=search) | Q(address__icontains=search))
        return qs

    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.save()


@schema_view(
    "Roles",
    list="Rollar ro'yxati",
    create="Yangi rol yaratish",
    retrieve="Rol ma'lumotlari",
    update="Rolni yangilash",
    partial_update="Rolni qisman yangilash",
    destroy="Rolni o'chirish",
)
class RoleViewSet(viewsets.ModelViewSet):
    queryset = Role.objects.filter(is_deleted=False)
    serializer_class = RoleSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        role_type = self.request.query_params.get("role_type")
        if role_type:
            qs = qs.filter(role_type=role_type)
        return qs

    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.save()


@schema_view(
    "Users",
    list="Foydalanuvchilar ro'yxati",
    create="Yangi foydalanuvchi yaratish",
    retrieve="Foydalanuvchi ma'lumotlari",
    update="Foydalanuvchini yangilash",
    partial_update="Foydalanuvchini qisman yangilash",
    destroy="Foydalanuvchini o'chirish",
)
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.filter(is_deleted=False).select_related("role", "branch")
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        branch = self.request.query_params.get("branch")
        if branch:
            qs = qs.filter(branch_id=branch)
        role = self.request.query_params.get("role")
        if role:
            qs = qs.filter(role_id=role)
        is_active = self.request.query_params.get("is_active")
        if is_active is not None:
            qs = qs.filter(is_active=is_active.lower() == "true")
        search = self.request.query_params.get("search")
        if search:
            qs = qs.filter(
                Q(first_name__icontains=search)
                | Q(last_name__icontains=search)
                | Q(username__icontains=search)
                | Q(phone__icontains=search)
            )
        return qs

    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.save()

    @extend_schema(tags=["Users"], summary="Joriy foydalanuvchi ma'lumotlari")
    @action(detail=False, methods=["get"], url_path="me")
    def me(self, request):
        return Response(self.get_serializer(request.user).data)

    @extend_schema(
        tags=["Users"],
        summary="Parol o'zgartirish",
        request={"application/json": {"type": "object", "properties": {
            "old_password": {"type": "string"},
            "new_password": {"type": "string"},
        }}},
    )
    @action(detail=True, methods=["post"], url_path="change-password")
    def change_password(self, request, pk=None):
        user = self.get_object()
        old_password = request.data.get("old_password")
        new_password = request.data.get("new_password")
        if not old_password or not new_password:
            return Response(
                {"detail": "Eski va yangi parol talab qilinadi."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not user.check_password(old_password):
            return Response(
                {"detail": "Eski parol noto'g'ri."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        user.set_password(new_password)
        user.save()
        return Response({"detail": "Parol muvaffaqiyatli o'zgartirildi."})


@schema_view(
    "Sales Targets",
    list="Savdo rejalari ro'yxati",
    create="Yangi savdo rejasi",
    retrieve="Savdo rejasi tafsilotlari",
    update="Savdo rejasini yangilash",
    partial_update="Savdo rejasini qisman yangilash",
    destroy="Savdo rejasini o'chirish",
)
class SalesTargetViewSet(viewsets.ModelViewSet):
    queryset = SalesTarget.objects.filter(is_deleted=False).select_related("user", "branch")
    serializer_class = SalesTargetSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.query_params.get("user")
        if user:
            qs = qs.filter(user_id=user)
        branch = self.request.query_params.get("branch")
        if branch:
            qs = qs.filter(branch_id=branch)
        period_type = self.request.query_params.get("period_type")
        if period_type:
            qs = qs.filter(period_type=period_type)
        return qs

    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.save()
