from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

from users.auth import RegisterView, LoginView, LogoutView
from users.views import BranchViewSet, RoleViewSet, UserViewSet, SalesTargetViewSet
from products.views import (
    CategoryViewSet, BrandViewSet, UnitViewSet,
    ProductAttributeViewSet, ProductViewSet, ProductVariantViewSet, PriceListViewSet,
)
from billz.views import (
    CustomerGroupViewSet, CustomerViewSet,
    CashRegisterViewSet, CashSessionViewSet,
    SaleViewSet, PaymentMethodViewSet,
    ExpenseCategoryViewSet, ExpenseViewSet, CashMovementViewSet,
)
from inventory.views import (
    WarehouseViewSet, StockViewSet, SupplierViewSet,
    PurchaseOrderViewSet, StockTransferViewSet,
    InventoryViewSet, WriteOffViewSet,
)

router = DefaultRouter()

# Users
router.register("branches", BranchViewSet)
router.register("roles", RoleViewSet)
router.register("users", UserViewSet)
router.register("sales-targets", SalesTargetViewSet)

# Products
router.register("categories", CategoryViewSet)
router.register("brands", BrandViewSet)
router.register("units", UnitViewSet)
router.register("product-attributes", ProductAttributeViewSet)
router.register("products", ProductViewSet)
router.register("product-variants", ProductVariantViewSet)
router.register("price-lists", PriceListViewSet)

# Billz
router.register("customer-groups", CustomerGroupViewSet)
router.register("customers", CustomerViewSet)
router.register("cash-registers", CashRegisterViewSet)
router.register("cash-sessions", CashSessionViewSet)
router.register("sales", SaleViewSet)
router.register("payment-methods", PaymentMethodViewSet)
router.register("expense-categories", ExpenseCategoryViewSet)
router.register("expenses", ExpenseViewSet)
router.register("cash-movements", CashMovementViewSet)

# Inventory
router.register("warehouses", WarehouseViewSet)
router.register("stocks", StockViewSet)
router.register("suppliers", SupplierViewSet)
router.register("purchase-orders", PurchaseOrderViewSet)
router.register("stock-transfers", StockTransferViewSet)
router.register("inventories", InventoryViewSet)
router.register("write-offs", WriteOffViewSet)

urlpatterns = [
    path("admin/", admin.site.urls),
    # Auth
    path("api/auth/register/", RegisterView.as_view(), name="auth-register"),
    path("api/auth/login/", LoginView.as_view(), name="auth-login"),
    path("api/auth/logout/", LogoutView.as_view(), name="auth-logout"),
    path("api/auth/token/refresh/", TokenRefreshView.as_view(), name="auth-token-refresh"),
    # API
    path("api/", include(router.urls)),
    # Swagger / OpenAPI docs
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
]
