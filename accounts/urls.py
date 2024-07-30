# sales/urls.py
from django.urls import path , include
from rest_framework.routers import DefaultRouter
from .views import RoleViewSet, UserAccountViewSet,UserCreateView, CategoryViewSet, SubCategoryViewSet, ElectronicsViewSet, StockViewSet, SaleViewSet
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
router = DefaultRouter()
router.register(r'roles', RoleViewSet)
router.register(r'users', UserAccountViewSet)
router.register(r'categories', CategoryViewSet)
router.register(r'subcategories', SubCategoryViewSet)
router.register(r'electronics', ElectronicsViewSet)
router.register(r'stocks', StockViewSet)
router.register(r'sales', SaleViewSet)
urlpatterns = [
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('create-user/', UserCreateView.as_view(), name='create-user'),
    path('', include(router.urls)),
]
