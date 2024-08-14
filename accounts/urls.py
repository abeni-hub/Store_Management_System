from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SalesSummaryView
from .serializers import CustomTokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

from .views import (
    UserAccountViewSet,
    UserCreateViewSet,
    RoleViewSet,
    CategoryViewSet,
    SubCategoryViewSet,
    ElectronicsViewSet,
    SaleViewSet,
    CashierCreateViewSet,
    SalesSummaryViewSet,
    ExpenseViewSet,
    UserDetail
)

router = DefaultRouter()
router.register(r'users', UserAccountViewSet)
router.register(r'users/create', UserCreateViewSet, basename='user-create')  # Add the create endpoint
router.register(r'roles', RoleViewSet)
router.register(r'cashiers', CashierCreateViewSet, basename='cashier-create')
router.register(r'categories', CategoryViewSet)
router.register(r'subcategories', SubCategoryViewSet)
router.register(r'electronics', ElectronicsViewSet)
router.register(r'sales', SaleViewSet)
router.register(r'sales-summary', SalesSummaryViewSet)
router.register(r'expenses', ExpenseViewSet, basename='expense')

urlpatterns = [
    path('', include(router.urls)),
    path('api/sales-summary/<str:period>/', SalesSummaryView.as_view(), name='sales-summary'),
    path('auth/jwt/create/', TokenObtainPairView.as_view(serializer_class=CustomTokenObtainPairSerializer), name='token_obtain_pair'),
    path('user-detail/', UserDetail, name= "UserDetail")

]