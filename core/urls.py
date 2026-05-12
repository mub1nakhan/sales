from django.urls import path, include
from rest_framework.routers import DefaultRouter
from users.views import BranchViewSet, RoleViewSet, UserViewSet, SalesTargetViewSet
from products.views import CategoryViewSet, BrandViewSet, UnitViewSet,ProductViewSet, ProductVariantViewSet,PriceListViewSet, PriceListItemViewSet


router = DefaultRouter()
router.register("branches", BranchViewSet)
router.register("roles", RoleViewSet)
router.register("users", UserViewSet)
router.register("sales-targets", SalesTargetViewSet)


router.register("categories", CategoryViewSet)
router.register("brands", BrandViewSet)
router.register("units", UnitViewSet)
router.register("products", ProductViewSet)
router.register("variants", ProductVariantViewSet)
router.register("price-lists", PriceListViewSet)
router.register("price-list-items", PriceListItemViewSet)



urlpatterns = [
    path("", include(router.urls)),
]