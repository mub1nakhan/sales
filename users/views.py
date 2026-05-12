from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import User, Role, Branch, SalesTarget
from users.seralizers import (
    UserSerializer, RoleSerializer,
    BranchSerializer, SalesTargetSerializer,
)


class BranchViewSet(viewsets.ModelViewSet):
    queryset = Branch.objects.filter(is_deleted=False)
    serializer_class = BranchSerializer
    permission_classes = [IsAuthenticated]


class RoleViewSet(viewsets.ModelViewSet):
    queryset = Role.objects.filter(is_deleted=False)
    serializer_class = RoleSerializer
    permission_classes = [IsAuthenticated]


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.filter(is_deleted=False).select_related("role", "branch")
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        branch = self.request.query_params.get("branch")
        if branch:
            qs = qs.filter(branch_id=branch)
        search = self.request.query_params.get("search")
        if search:
            qs = qs.filter(first_name__icontains=search) | qs.filter(phone__icontains=search)
        return qs

    @action(detail=False, methods=["get"], url_path="me")
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)


class SalesTargetViewSet(viewsets.ModelViewSet):
    queryset = SalesTarget.objects.filter(is_deleted=False)
    serializer_class = SalesTargetSerializer
    permission_classes = [IsAuthenticated]