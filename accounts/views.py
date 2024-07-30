from rest_framework import viewsets, generics
from .models import UserAccount, Role, Category, SubCategory, Electronics, Stock, Sale
from .serializers import UserAccountSerializer, UserCreateSerializer, RoleSerializer, CategorySerializer, SubCategorySerializer, ElectronicsSerializer, StockSerializer, SaleSerializer

class RoleViewSet(viewsets.ModelViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer

    def perform_create(self, serializer):
        Role.create_default_roles()
        serializer.save()

class UserAccountViewSet(viewsets.ModelViewSet):
    queryset = UserAccount.objects.all()
    serializer_class = UserAccountSerializer

class UserCreateView(generics.CreateAPIView):
    queryset = UserAccount.objects.all()
    serializer_class = UserCreateSerializer

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class SubCategoryViewSet(viewsets.ModelViewSet):
    queryset = SubCategory.objects.all()
    serializer_class = SubCategorySerializer

class ElectronicsViewSet(viewsets.ModelViewSet):
    queryset = Electronics.objects.all()
    serializer_class = ElectronicsSerializer

class StockViewSet(viewsets.ModelViewSet):
    queryset = Stock.objects.all()
    serializer_class = StockSerializer

class SaleViewSet(viewsets.ModelViewSet):
    queryset = Sale.objects.all()
    serializer_class = SaleSerializer
