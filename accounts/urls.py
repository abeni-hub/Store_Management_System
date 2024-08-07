from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserAccountViewSet,
    UserCreateViewSet,
    RoleViewSet,
    CategoryViewSet,
    SubCategoryViewSet,
    ElectronicsViewSet,
    SalesViewSet,
    CashierCreateViewSet,
    SalesSummaryViewSet,
    ExpenseViewSet,
)

router = DefaultRouter()
router.register(r'users', UserAccountViewSet)
router.register(r'users/create', UserCreateViewSet, basename='user-create')  # Add the create endpoint
router.register(r'roles', RoleViewSet)
router.register(r'cashiers', CashierCreateViewSet, basename='cashier-create')
router.register(r'categories', CategoryViewSet)
router.register(r'subcategories', SubCategoryViewSet)
router.register(r'electronics', ElectronicsViewSet)
router.register(r'sales', SalesViewSet)
router.register(r'sales-summary', SalesSummaryViewSet)
router.register(r'expenses', ExpenseViewSet, basename='expense')

urlpatterns = [
    path('', include(router.urls)),
]
