import json
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view, renderer_classes
from django.core import serializers
from django.db.models import Sum
from rest_framework import permissions
from rest_framework.permissions import AllowAny
from rest_framework.decorators import action
import openpyxl
import datetime
from django.db.models import F
from django.db.models.functions import TruncMonth, ExtractWeekDay
from django.http import HttpResponse
from django.db import models
from django.utils.timezone import now
from datetime import timedelta
from rest_framework import status
from rest_framework.renderers import JSONRenderer, TemplateHTMLRenderer
from django.http import JsonResponse
from .models import Exchange,Buying, Revenue, UserAccount, Cashier, Role, Category, SubCategory, Electronics, Sales, SalesSummary, Expense
from .serializers import (
    RevenueSerializer,
    UserAccountSerializer,
    UserCreateSerializer,
    RoleSerializer,
    CategorySerializer,
    SubCategorySerializer,
    ElectronicsSerializer,
    BuyingSerializer,
    SalesSerializer,
    CashierSerializer,
    SalesSummarySerializer,
    ExpenseSerializer,
    ExchangeSerializer,
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
    from rest_framework import permissions


class UserAccountViewSet(viewsets.ModelViewSet):
    queryset = UserAccount.objects.all()
    serializer_class = UserAccountSerializer
    permission_classes = [AllowAny]  # Temporarily allow any user to delete

    def get_permissions(self):
        if self.action == 'destroy':
            return [permissions.AllowAny()]  # Allow any user to delete
        return super().get_permissions()

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_destroy(self, instance):
        instance.delete()
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

    # 🔹 Export to Excel
    @action(detail=False, methods=["get"])
    def export_excel(self, request):
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Electronics"

        ws.append(["ID", "Name", "Size", "Quantity", "Buying Price", "Date Added", "Added By", "Capital"])

        for obj in Electronics.objects.all():
            capital = obj.quantity * obj.buying_price
            ws.append([
                obj.id, obj.name, obj.size, obj.quantity,
                obj.buying_price, obj.date_added, obj.added_by, capital
            ])

        response = HttpResponse(
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        response["Content-Disposition"] = 'attachment; filename="electronics.xlsx"'
        wb.save(response)
        return response

    # 🔹 Summary API (all stats in one response)
    @action(detail=False, methods=["get"])
    def summary(self, request):
        total_quantity = Electronics.objects.aggregate(total=models.Sum("quantity"))["total"] or 0
        total_capital = Electronics.objects.aggregate(
            total_capital=models.Sum(models.F("quantity") * models.F("buying_price"))
        )["total_capital"] or 0

        per_item_quantities = list(
            Electronics.objects.values("name").annotate(total_quantity=models.Sum("quantity"))
        )
        per_item_capitals = list(
            Electronics.objects.values("name").annotate(
                total_capital=models.Sum(models.F("quantity") * models.F("buying_price"))
            )
        )

        return Response({
            "total_quantity": total_quantity,
            "total_capital": total_capital,
            "per_item_quantities": per_item_quantities,
            "per_item_capitals": per_item_capitals
        })


# -----------------------------
# 📦 Buying ViewSet
# -----------------------------
class BuyingViewSet(viewsets.ModelViewSet):
    queryset = Buying.objects.all()
    serializer_class = BuyingSerializer

    # 🔹 Export Buying to Excel
    @action(detail=False, methods=["get"])
    def export_excel(self, request):
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Buying"

        ws.append(["ID", "Name", "Size", "Quantity", "Buying Price", "Date Added", "Added By", "Capital"])

        for obj in Buying.objects.all():
            capital = obj.quantity * obj.buying_price
            ws.append([
                obj.id, obj.name, obj.size, obj.quantity,
                obj.buying_price, obj.date_added, obj.added_by, capital
            ])

        response = HttpResponse(
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        response["Content-Disposition"] = 'attachment; filename="buying.xlsx"'
        wb.save(response)
        return response

    @action(detail=False, methods=["get"])
    def summary(self, request):
        total_quantity = Buying.objects.aggregate(total=Sum("quantity"))["total"] or 0
        total_capital = Buying.objects.aggregate(
            total_capital=Sum(F("quantity") * F("buying_price"))
        )["total_capital"] or 0

        per_item_quantities = list(
            Buying.objects.values("name").annotate(total_quantity=Sum("quantity"))
        )
        per_item_capitals = list(
            Buying.objects.values("name").annotate(
                total_capital=Sum(F("quantity") * F("buying_price"))
            )
        )

        return Response({
            "total_quantity": total_quantity,
            "total_capital": total_capital,
            "per_item_quantities": per_item_quantities,
            "per_item_capitals": per_item_capitals
        })

    # -----------------------------
    # 📊 Analytics API
    # -----------------------------
    @action(detail=False, methods=["get"])
    def analytics(self, request):
        today = datetime.date.today()

        # 🔹 Today total
        today_total = Buying.objects.filter(date_added=today).aggregate(
            total=Sum(F("quantity") * F("buying_price"))
        )["total"] or 0

        # 🔹 Weekly total (current week)
        week_start = today - datetime.timedelta(days=today.weekday())  # Monday start
        week_end = week_start + datetime.timedelta(days=6)
        weekly_total = Buying.objects.filter(date_added__range=[week_start, week_end]).aggregate(
            total=Sum(F("quantity") * F("buying_price"))
        )["total"] or 0

        # 🔹 Weekly breakdown (Mon-Sun, across all data)
        weekday_data = Buying.objects.annotate(
            weekday=ExtractWeekDay("date_added")
        ).values("weekday").annotate(
            total=Sum(F("quantity") * F("buying_price"))
        ).order_by("weekday")

        # Map Django weekday (1=Sunday, 2=Monday … 7=Saturday) to readable names
        weekday_map = {
            1: "Sunday", 2: "Monday", 3: "Tuesday", 4: "Wednesday",
            5: "Thursday", 6: "Friday", 7: "Saturday"
        }
        weekly_breakdown = {weekday_map[item["weekday"]]: item["total"] for item in weekday_data}

        # 🔹 Monthly totals
        monthly_data = Buying.objects.annotate(
            month=TruncMonth("date_added")
        ).values("month").annotate(
            total=Sum(F("quantity") * F("buying_price"))
        ).order_by("month")

        monthly_totals = [
            {"month": item["month"].strftime("%B %Y"), "total": item["total"]}
            for item in monthly_data
        ]

        return Response({
            "today_total": today_total,
            "weekly_total": weekly_total,
            "weekly_breakdown": weekly_breakdown,
            "monthly_totals": monthly_totals
        })

class SaleViewSet(viewsets.ModelViewSet):
    queryset = Sales.objects.all()
    serializer_class = SalesSerializer


class SalesSummaryViewSet(viewsets.ModelViewSet):
    queryset = SalesSummary.objects.all()
    serializer_class = SalesSummarySerializer


class ExpenseViewSet(viewsets.ModelViewSet):
    queryset = Expense.objects.all()  # Get all expenses
    serializer_class = ExpenseSerializer  # Use the Expense serializer
class RevenueViewSet(viewsets.ModelViewSet):
    queryset = Revenue.objects.all()  # Get all expenses
    serializer_class = RevenueSerializer  # Use the Expense serializer
class ExchangeViewSet(viewsets.ModelViewSet):
    queryset = Exchange.objects.all()  # Get all expenses
    serializer_class = ExchangeSerializer  # Use the Expense serializer
class SalesSummaryView(APIView):
    def get_sales_expenses(self, start_date, end_date):
        sales = Sales.objects.filter(date__range=(start_date, end_date)).aggregate(
            total_sales=Sum('selling_price'),
            total_profit=Sum('profit')
        )
        expenses = Expense.objects.filter(date__range=(start_date, end_date)).aggregate(
            total_expenses=Sum('amount')
        )

        return {
            'sales': sales['total_sales'] or 0,
            'expenses': expenses['total_expenses'] or 0,
            'profit': sales['total_profit'] or 0,
        }

    def get_daily_summary(self):
        today = now().date()
        return self.get_sales_expenses(today, today)

    def get_weekly_summary(self):
        today = now().date()
        start_of_week = today - timedelta(days=today.weekday())
        return self.get_sales_expenses(start_of_week, today)

    def get_monthly_summary(self):
        today = now().date()
        start_of_month = today.replace(day=1)
        return self.get_sales_expenses(start_of_month, today)

    def get(self, request, period, *args, **kwargs):
        if period == 'daily':
            summary = self.get_daily_summary()
        elif period == 'weekly':
            summary = self.get_weekly_summary()
        elif period == 'monthly':
            summary = self.get_monthly_summary()
        else:
            return Response({'error': 'Invalid period'}, status=400)

        return Response(summary, status=200)


@api_view(('GET',))
# @renderer_classes( JSONRenderer)
def UserDetail(request):
    if request.method == "GET":

        user = UserAccount.objects.filter(email=request.GET.get('email'))
        # & UserAccount.objects.filter(password = request.GET.get('password'))
        if user:
            js = serializers.serialize('json', user)
            return JsonResponse(js, safe=False)
        else:
            return Response({"error": "user not found"}, status=404)
