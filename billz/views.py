from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db.models import Q, Sum
from drf_spectacular.utils import extend_schema
from core.schema import schema_view
from .models import (
    CustomerGroup, Customer, CashRegister, CashSession,
    Sale, SaleReturn, PaymentMethod,
    ExpenseCategory, Expense, CashMovement,
)
from .serializers import (
    CustomerGroupSerializer, CustomerSerializer,
    CashRegisterSerializer, CashSessionSerializer,
    SaleSerializer, SaleReturnSerializer,
    PaymentMethodSerializer,
    ExpenseCategorySerializer, ExpenseSerializer,
    CashMovementSerializer,
)


@schema_view(
    "Customer Groups",
    list="Mijoz guruhlari ro'yxati",
    create="Yangi mijoz guruhi yaratish",
    retrieve="Mijoz guruhi ma'lumotlari",
    update="Mijoz guruhini yangilash",
    partial_update="Mijoz guruhini qisman yangilash",
    destroy="Mijoz guruhini o'chirish",
)
class CustomerGroupViewSet(viewsets.ModelViewSet):
    queryset = CustomerGroup.objects.filter(is_deleted=False)
    serializer_class = CustomerGroupSerializer
    permission_classes = [IsAuthenticated]

    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.save()


@schema_view(
    "Customers",
    list="Mijozlar ro'yxati",
    create="Yangi mijoz qo'shish",
    retrieve="Mijoz ma'lumotlari",
    update="Mijozni yangilash",
    partial_update="Mijozni qisman yangilash",
    destroy="Mijozni o'chirish",
)
class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.filter(is_deleted=False).select_related("group", "branch")
    serializer_class = CustomerSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        search = self.request.query_params.get("search")
        if search:
            qs = qs.filter(
                Q(first_name__icontains=search)
                | Q(last_name__icontains=search)
                | Q(phone__icontains=search)
            )
        group = self.request.query_params.get("group")
        if group:
            qs = qs.filter(group_id=group)
        branch = self.request.query_params.get("branch")
        if branch:
            qs = qs.filter(branch_id=branch)
        is_active = self.request.query_params.get("is_active")
        if is_active is not None:
            qs = qs.filter(is_active=is_active.lower() == "true")
        return qs

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.save()

    @extend_schema(tags=["Customers"], summary="Mijozning so'nggi 20 ta sotuvi")
    @action(detail=True, methods=["get"], url_path="sales")
    def sales(self, request, pk=None):
        customer = self.get_object()
        qs = Sale.objects.filter(
            customer=customer, is_deleted=False
        ).order_by("-sale_date")[:20]
        return Response(SaleSerializer(qs, many=True).data)


@schema_view(
    "Cash Registers",
    list="Kassalar ro'yxati",
    create="Yangi kassa qo'shish",
    retrieve="Kassa ma'lumotlari",
    update="Kassani yangilash",
    partial_update="Kassani qisman yangilash",
    destroy="Kassani o'chirish",
)
class CashRegisterViewSet(viewsets.ModelViewSet):
    queryset = CashRegister.objects.filter(is_deleted=False).select_related("branch")
    serializer_class = CashRegisterSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        branch = self.request.query_params.get("branch")
        if branch:
            qs = qs.filter(branch_id=branch)
        return qs

    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.save()


@schema_view(
    "Cash Sessions",
    list="Kassa smenalari ro'yxati",
    create="Yangi smena ochish",
    retrieve="Smena ma'lumotlari",
    update="Smenani yangilash",
    partial_update="Smenani qisman yangilash",
    destroy="Smenani o'chirish",
)
class CashSessionViewSet(viewsets.ModelViewSet):
    queryset = CashSession.objects.filter(is_deleted=False).select_related(
        "cash_register", "cashier"
    )
    serializer_class = CashSessionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        cash_register = self.request.query_params.get("cash_register")
        if cash_register:
            qs = qs.filter(cash_register_id=cash_register)
        session_status = self.request.query_params.get("status")
        if session_status:
            qs = qs.filter(status=session_status)
        return qs

    def perform_create(self, serializer):
        serializer.save(cashier=self.request.user, status=CashSession.Status.OPEN)

    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.save()

    @extend_schema(tags=["Cash Sessions"], summary="Smenani yopish")
    @action(detail=True, methods=["post"], url_path="close")
    def close(self, request, pk=None):
        session = self.get_object()
        if session.status == CashSession.Status.CLOSED:
            return Response(
                {"detail": "Smena allaqachon yopilgan."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        session.status = CashSession.Status.CLOSED
        session.closing_balance = request.data.get("closing_balance", 0)
        session.closed_at = timezone.now()
        session.notes = request.data.get("notes", session.notes)
        session.save()
        return Response(self.get_serializer(session).data)

    @extend_schema(tags=["Cash Sessions"], summary="Smena yakuniy hisoboti")
    @action(detail=True, methods=["get"], url_path="summary")
    def summary(self, request, pk=None):
        session = self.get_object()
        total_sales = Sale.objects.filter(
            cash_session=session, is_deleted=False
        ).aggregate(total=Sum("total_amount"))["total"] or 0
        total_expenses = Expense.objects.filter(
            cash_session=session, is_deleted=False
        ).aggregate(total=Sum("amount"))["total"] or 0
        movements = list(
            CashMovement.objects.filter(cash_session=session)
            .values("movement_type")
            .annotate(total=Sum("amount"))
        )
        return Response({
            "session": self.get_serializer(session).data,
            "sales_count": Sale.objects.filter(cash_session=session, is_deleted=False).count(),
            "total_sales": total_sales,
            "total_expenses": total_expenses,
            "movements": movements,
        })


@schema_view(
    "Sales",
    list="Sotuvlar ro'yxati",
    create="Yangi sotuv yaratish",
    retrieve="Sotuv tafsilotlari (items va payments bilan)",
    update="Sotuvni yangilash",
    partial_update="Sotuvni qisman yangilash",
    destroy="Sotuvni o'chirish",
)
class SaleViewSet(viewsets.ModelViewSet):
    queryset = (
        Sale.objects.filter(is_deleted=False)
        .select_related("branch", "customer", "seller", "cash_session")
        .prefetch_related("items", "payments")
    )
    serializer_class = SaleSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        branch = self.request.query_params.get("branch")
        if branch:
            qs = qs.filter(branch_id=branch)
        seller = self.request.query_params.get("seller")
        if seller:
            qs = qs.filter(seller_id=seller)
        customer = self.request.query_params.get("customer")
        if customer:
            qs = qs.filter(customer_id=customer)
        sale_status = self.request.query_params.get("status")
        if sale_status:
            qs = qs.filter(status=sale_status)
        payment_status = self.request.query_params.get("payment_status")
        if payment_status:
            qs = qs.filter(payment_status=payment_status)
        date_from = self.request.query_params.get("date_from")
        if date_from:
            qs = qs.filter(sale_date__date__gte=date_from)
        date_to = self.request.query_params.get("date_to")
        if date_to:
            qs = qs.filter(sale_date__date__lte=date_to)
        search = self.request.query_params.get("search")
        if search:
            qs = qs.filter(
                Q(receipt_number__icontains=search)
                | Q(customer__first_name__icontains=search)
                | Q(customer__phone__icontains=search)
            )
        return qs

    def perform_create(self, serializer):
        serializer.save(seller=self.request.user)

    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.save()

    @extend_schema(tags=["Sales"], summary="Sotuvni yakunlash (draft → completed)")
    @action(detail=True, methods=["post"], url_path="complete")
    def complete(self, request, pk=None):
        sale = self.get_object()
        if sale.status != Sale.Status.DRAFT:
            return Response(
                {"detail": "Faqat qoralama sotuvlarni yakunlash mumkin."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        sale.status = Sale.Status.COMPLETED
        sale.save()
        return Response(self.get_serializer(sale).data)

    @extend_schema(tags=["Sales"], summary="Sotuvni bekor qilish")
    @action(detail=True, methods=["post"], url_path="cancel")
    def cancel(self, request, pk=None):
        sale = self.get_object()
        if sale.status == Sale.Status.COMPLETED:
            return Response(
                {"detail": "Yakunlangan sotuvni bekor qilib bo'lmaydi. Qaytarish amali qiling."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        sale.status = Sale.Status.CANCELLED
        sale.save()
        return Response(self.get_serializer(sale).data)

    @extend_schema(tags=["Sales"], summary="Sotuv bo'yicha qaytarishlar ro'yxati")
    @action(detail=True, methods=["get"], url_path="returns")
    def returns(self, request, pk=None):
        sale = self.get_object()
        qs = SaleReturn.objects.filter(sale=sale, is_deleted=False)
        return Response(SaleReturnSerializer(qs, many=True).data)


@schema_view(
    "Payment Methods",
    list="To'lov usullari ro'yxati",
    create="Yangi to'lov usuli yaratish",
    retrieve="To'lov usuli ma'lumotlari",
    update="To'lov usulini yangilash",
    partial_update="To'lov usulini qisman yangilash",
    destroy="To'lov usulini o'chirish",
)
class PaymentMethodViewSet(viewsets.ModelViewSet):
    queryset = PaymentMethod.objects.filter(is_deleted=False).order_by("sort_order")
    serializer_class = PaymentMethodSerializer
    permission_classes = [IsAuthenticated]

    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.save()


@schema_view(
    "Expense Categories",
    list="Xarajat turlari ro'yxati",
    create="Yangi xarajat turi yaratish",
    retrieve="Xarajat turi ma'lumotlari",
    update="Xarajat turini yangilash",
    partial_update="Xarajat turini qisman yangilash",
    destroy="Xarajat turini o'chirish",
)
class ExpenseCategoryViewSet(viewsets.ModelViewSet):
    queryset = ExpenseCategory.objects.filter(is_deleted=False).select_related("parent")
    serializer_class = ExpenseCategorySerializer
    permission_classes = [IsAuthenticated]

    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.save()


@schema_view(
    "Expenses",
    list="Xarajatlar ro'yxati",
    create="Yangi xarajat qo'shish",
    retrieve="Xarajat ma'lumotlari",
    update="Xarajatni yangilash",
    partial_update="Xarajatni qisman yangilash",
    destroy="Xarajatni o'chirish",
)
class ExpenseViewSet(viewsets.ModelViewSet):
    queryset = Expense.objects.filter(is_deleted=False).select_related(
        "branch", "category", "payment_method", "created_by"
    )
    serializer_class = ExpenseSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        branch = self.request.query_params.get("branch")
        if branch:
            qs = qs.filter(branch_id=branch)
        category = self.request.query_params.get("category")
        if category:
            qs = qs.filter(category_id=category)
        date_from = self.request.query_params.get("date_from")
        if date_from:
            qs = qs.filter(expense_date__gte=date_from)
        date_to = self.request.query_params.get("date_to")
        if date_to:
            qs = qs.filter(expense_date__lte=date_to)
        return qs

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.save()


@schema_view(
    "Cash Movements",
    list="Kassa harakatlari ro'yxati",
    create="Yangi kassa harakati (kirim/chiqim)",
    retrieve="Kassa harakati ma'lumotlari",
    update="Kassa harakatini yangilash",
    partial_update="Kassa harakatini qisman yangilash",
    destroy="Kassa harakatini o'chirish",
)
class CashMovementViewSet(viewsets.ModelViewSet):
    queryset = CashMovement.objects.filter(is_deleted=False).select_related(
        "cash_session", "created_by"
    )
    serializer_class = CashMovementSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        session = self.request.query_params.get("cash_session")
        if session:
            qs = qs.filter(cash_session_id=session)
        movement_type = self.request.query_params.get("movement_type")
        if movement_type:
            qs = qs.filter(movement_type=movement_type)
        return qs

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.save()
