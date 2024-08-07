from rest_framework import viewsets
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Sum
from datetime import timedelta
from datetime import date
from rest_framework import status
from .models import UserAccount, Cashier , Role, Category, SubCategory, Electronics, Sales, SalesSummary, Expense
from .serializers import (
    UserAccountSerializer,
    UserCreateSerializer,
    RoleSerializer,
    CategorySerializer,
    SubCategorySerializer,
    ElectronicsSerializer,
    SalesSerializer,
    CashierSerializer,
    SalesSummarySerializer,
    ExpenseSerializer,
)

class RoleViewSet(viewsets.ModelViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
class CashierCreateViewSet(viewsets.ModelViewSet):
    queryset = Cashier.objects.all()
    serializer_class = CashierSerializer
class UserAccountViewSet(viewsets.ModelViewSet):
    queryset = UserAccount.objects.all()
    serializer_class = UserAccountSerializer

    # def get_queryset(self):
    #     """
    #     Optionally restricts the returned users to a given email,
    #     by filtering against a 'email' query parameter in the URL.
    #     """
    #     queryset = super().get_queryset()
    #     email = self.request.query_params.get('email', None)
    #     if email is not None:
    #         queryset = queryset.filter(email=email)
    #     return queryset
    #
    # def retrieve(self, request, *args, **kwargs):
    #     # Get the user instance
    #     instance = self.get_object()
    #
    #     # Clear user groups and permissions
    #     instance.remove_groups()
    #     instance.remove_permissions()
    #
    #     # Serialize the user instance
    #     serializer = self.get_serializer(instance)
    #     return Response(serializer.data)

class UserCreateViewSet(viewsets.ModelViewSet):
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

class SalesViewSet(viewsets.ModelViewSet):
    queryset = Sales.objects.all()
    serializer_class = SalesSerializer

    def get_sales_summary(self):
        today = timezone.now().date()

        # Daily sales
        daily_sales = Sales.objects.filter(date=today).values(
            'item_name', 'category', 'sub_category'
        ).annotate(total_quantity=Sum('quantity'))

        # Weekly sales
        start_of_week = today - timedelta(days=today.weekday())  # Monday as the start of the week
        weekly_sales = Sales.objects.filter(date__gte=start_of_week).values(
            'item_name', 'category', 'sub_category'
        ).annotate(total_quantity=Sum('quantity'))

        # Monthly sales
        start_of_month = today.replace(day=1)
        monthly_sales = Sales.objects.filter(date__gte=start_of_month).values(
            'item_name', 'category', 'sub_category'
        ).annotate(total_quantity=Sum('quantity'))

        return {
            'daily_sales': list(daily_sales),
            'weekly_sales': list(weekly_sales),
            'monthly_sales': list(monthly_sales)
        }

    def list(self, request, *args, **kwargs):
        # Get the sales summary
        summary = self.get_sales_summary()

        # Get the usual queryset
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)

        return Response({
            'sales': serializer.data,
            'summary': summary
        })

class SalesSummaryViewSet(viewsets.ModelViewSet):
    queryset = SalesSummary.objects.all()
    serializer_class = SalesSummarySerializer

class ExpenseViewSet(viewsets.ModelViewSet):
    queryset = Expense.objects.all()  # Get all expenses
    serializer_class = ExpenseSerializer  # Use the Expense serializer
