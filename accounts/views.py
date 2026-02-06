# views.py - Complete file with backend pagination
import json
from rest_framework import viewsets, status, pagination
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view, renderer_classes
from django.db.models import Q, Sum, Count
from django.utils import timezone
from datetime import timedelta
from django.core import serializers
from django.db import transaction
from django.db.models import Sum, Q
from rest_framework import permissions
from rest_framework.permissions import AllowAny
from django.utils import timezone
from django.utils.timezone import now
from datetime import timedelta, datetime
from rest_framework.renderers import JSONRenderer, TemplateHTMLRenderer
# Add these imports if missing
from django.db.models import Sum, Avg, Q, Count
from django.utils import timezone
from datetime import datetime
from django.http import JsonResponse
from .models import Buying, Exchange, QuickSale, Revenue, UserAccount, Cashier, Role, Category, SubCategory, Electronics, Sales, SalesSummary, Expense
from .serializers import (
    BuyingSerializer,
    RevenueSerializer,
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
    ExchangeSerializer,
    QuickSaleSerializer,
)

# Custom Pagination Classes
class StandardPagination(pagination.PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100

    def get_paginated_response(self, data):
        return Response({
            'count': self.page.paginator.count,
            'total_pages': self.page.paginator.num_pages,
            'current_page': self.page.number,
            'page_size': self.get_page_size(self.request),
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'results': data
        })

class LargePagination(pagination.PageNumberPagination):
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 200

    def get_paginated_response(self, data):
        return Response({
            'count': self.page.paginator.count,
            'total_pages': self.page.paginator.num_pages,
            'current_page': self.page.number,
            'page_size': self.get_page_size(self.request),
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'results': data
        })

# ViewSets with Pagination
class RoleViewSet(viewsets.ModelViewSet):
    queryset = Role.objects.all().order_by('id')
    serializer_class = RoleSerializer
    pagination_class = StandardPagination

    def get_queryset(self):
        queryset = Role.objects.all().order_by('id')
        search = self.request.query_params.get('search', None)
        
        if search:
            queryset = queryset.filter(name__icontains=search)
            
        return queryset

class CashierCreateViewSet(viewsets.ModelViewSet):
    queryset = Cashier.objects.all().order_by('id')
    serializer_class = CashierSerializer
    pagination_class = StandardPagination

    def get_queryset(self):
        queryset = Cashier.objects.all().order_by('id')
        search = self.request.query_params.get('search', None)
        
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | 
                Q(email__icontains=search) |
                Q(phone_number__icontains=search)
            )
            
        return queryset

class UserAccountViewSet(viewsets.ModelViewSet):
    queryset = UserAccount.objects.all().order_by('id')
    serializer_class = UserAccountSerializer
    pagination_class = StandardPagination
    permission_classes = [AllowAny]

    def get_permissions(self):
        if self.action == 'destroy':
            return [permissions.AllowAny()]
        return super().get_permissions()

    def get_queryset(self):
        queryset = UserAccount.objects.all().order_by('id')
        
        search = self.request.query_params.get('search', None)
        role = self.request.query_params.get('role', None)
        is_active = self.request.query_params.get('is_active', None)
        
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | 
                Q(email__icontains=search)
            )
        
        if role:
            queryset = queryset.filter(role=role)
            
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
            
        return queryset

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_destroy(self, instance):
        instance.delete()

class UserCreateViewSet(viewsets.ModelViewSet):
    queryset = UserAccount.objects.all().order_by('id')
    serializer_class = UserCreateSerializer
    pagination_class = StandardPagination

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all().order_by('id')
    serializer_class = CategorySerializer
    pagination_class = StandardPagination

    def get_queryset(self):
        queryset = Category.objects.all().order_by('id')
        search = self.request.query_params.get('search', None)
        
        if search:
            queryset = queryset.filter(name__icontains=search)
            
        return queryset

class SubCategoryViewSet(viewsets.ModelViewSet):
    queryset = SubCategory.objects.all().order_by('id')
    serializer_class = SubCategorySerializer
    pagination_class = StandardPagination

    def get_queryset(self):
        queryset = SubCategory.objects.all().order_by('id')
        search = self.request.query_params.get('search', None)
        main_category = self.request.query_params.get('main_category', None)
        
        if search:
            queryset = queryset.filter(name__icontains=search)
        
        if main_category:
            queryset = queryset.filter(main_category_id=main_category)
            
        return queryset

class ElectronicsViewSet(viewsets.ModelViewSet):
    queryset = Electronics.objects.all().order_by('-date_added')
    serializer_class = ElectronicsSerializer
    pagination_class = StandardPagination

    def get_queryset(self):
        queryset = Electronics.objects.all().order_by('-date_added')
        
        search = self.request.query_params.get('search', None)
        main_category = self.request.query_params.get('main_category', None)
        sub_category = self.request.query_params.get('sub_category', None)
        min_quantity = self.request.query_params.get('min_quantity', None)
        max_quantity = self.request.query_params.get('max_quantity', None)
        low_stock = self.request.query_params.get('low_stock', None)
        
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(size__icontains=search) |
                Q(added_by__icontains=search)
            )
        
        if main_category:
            queryset = queryset.filter(main_category_id=main_category)
            
        if sub_category:
            queryset = queryset.filter(sub_category_id=sub_category)
            
        if min_quantity:
            queryset = queryset.filter(quantity__gte=int(min_quantity))
            
        if max_quantity:
            queryset = queryset.filter(quantity__lte=int(max_quantity))
            
        if low_stock == 'true':
            queryset = queryset.filter(quantity__lte=10)
            
        return queryset

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters

class SaleViewSet(viewsets.ModelViewSet):
    queryset = Sales.objects.all().order_by('-id')
    serializer_class = SalesSerializer
    pagination_class = LargePagination
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    ordering_fields = [
        'id', 'date', 'item_name', 'quantity', 'selling_price', 
        'profit', 'seller_name', 'payment_method'
    ]
    ordering = ['-id']  # Default ordering

    def get_queryset(self):
        queryset = Sales.objects.all().order_by('-id')
        
        # Your existing filter logic here...
        search = self.request.query_params.get('search', None)
        start_date = self.request.query_params.get('start_date', None)
        end_date = self.request.query_params.get('end_date', None)
        seller_name = self.request.query_params.get('seller_name', None)
        status = self.request.query_params.get('status', None)
        payment_method = self.request.query_params.get('payment_method', None)
        main_category = self.request.query_params.get('main_category', None)
        sub_category = self.request.query_params.get('sub_category', None)
        
        if search:
            queryset = queryset.filter(
                Q(item_name__icontains=search) |
                Q(buyer_name__icontains=search) |
                Q(seller_name__icontains=search)
            )
        
        if start_date:
            queryset = queryset.filter(date__gte=start_date)
            
        if end_date:
            queryset = queryset.filter(date__lte=end_date)
            
        if seller_name:
            queryset = queryset.filter(seller_name__icontains=seller_name)
            
        if status:
            queryset = queryset.filter(status=status)
            
        if payment_method:
            queryset = queryset.filter(payment_method=payment_method)
            
        if main_category:
            queryset = queryset.filter(main_category_id=main_category)
            
        if sub_category:
            queryset = queryset.filter(sub_category_id=sub_category)
            
        return queryset
class SalesSummaryViewSet(viewsets.ModelViewSet):
    queryset = SalesSummary.objects.all().order_by('-date')
    serializer_class = SalesSummarySerializer
    pagination_class = StandardPagination

    def get_queryset(self):
        queryset = SalesSummary.objects.all().order_by('-date')
        
        start_date = self.request.query_params.get('start_date', None)
        end_date = self.request.query_params.get('end_date', None)
        
        if start_date:
            queryset = queryset.filter(date__gte=start_date)
            
        if end_date:
            queryset = queryset.filter(date__lte=end_date)
            
        return queryset

class ExpenseViewSet(viewsets.ModelViewSet):
    queryset = Expense.objects.all().order_by('-date')
    serializer_class = ExpenseSerializer
    pagination_class = StandardPagination

    def get_queryset(self):
        queryset = Expense.objects.all().order_by('-date')
        
        search = self.request.query_params.get('search', None)
        start_date = self.request.query_params.get('start_date', None)
        end_date = self.request.query_params.get('end_date', None)
        is_verified = self.request.query_params.get('is_verified', None)
        min_amount = self.request.query_params.get('min_amount', None)
        max_amount = self.request.query_params.get('max_amount', None)
        
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(description__icontains=search)
            )
            
        if start_date:
            queryset = queryset.filter(date__gte=start_date)
            
        if end_date:
            queryset = queryset.filter(date__lte=end_date)
            
        if is_verified is not None:
            queryset = queryset.filter(is_verified=is_verified.lower() == 'true')
            
        if min_amount:
            queryset = queryset.filter(amount__gte=float(min_amount))
            
        if max_amount:
            queryset = queryset.filter(amount__lte=float(max_amount))
            
        return queryset

class RevenueViewSet(viewsets.ModelViewSet):
    queryset = Revenue.objects.all().order_by('-date')
    serializer_class = RevenueSerializer
    pagination_class = StandardPagination

    def get_queryset(self):
        queryset = Revenue.objects.all().order_by('-date')
        
        search = self.request.query_params.get('search', None)
        start_date = self.request.query_params.get('start_date', None)
        end_date = self.request.query_params.get('end_date', None)
        is_verified = self.request.query_params.get('is_verified', None)
        min_amount = self.request.query_params.get('min_amount', None)
        max_amount = self.request.query_params.get('max_amount', None)
        reason = self.request.query_params.get('reason', None)
        
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(recievername__icontains=search) |
                Q(description__icontains=search) |
                Q(reason__icontains=search)
            )
            
        if start_date:
            queryset = queryset.filter(date__gte=start_date)
            
        if end_date:
            queryset = queryset.filter(date__lte=end_date)
            
        if is_verified is not None:
            queryset = queryset.filter(is_verified=is_verified.lower() == 'true')
            
        if min_amount:
            queryset = queryset.filter(amount__gte=float(min_amount))
            
        if max_amount:
            queryset = queryset.filter(amount__lte=float(max_amount))
            
        if reason:
            queryset = queryset.filter(reason=reason)
            
        return queryset

class ExchangeViewSet(viewsets.ModelViewSet):
    queryset = Exchange.objects.all().order_by('-date')
    serializer_class = ExchangeSerializer
    pagination_class = StandardPagination

    def get_queryset(self):
        queryset = Exchange.objects.all().order_by('-date')
        
        search = self.request.query_params.get('search', None)
        start_date = self.request.query_params.get('start_date', None)
        end_date = self.request.query_params.get('end_date', None)
        seller_name = self.request.query_params.get('seller_name', None)
        payment_method = self.request.query_params.get('payment_method', None)
        main_category = self.request.query_params.get('main_category', None)
        sub_category = self.request.query_params.get('sub_category', None)
        
        if search:
            queryset = queryset.filter(
                Q(item_name__icontains=search) |
                Q(new_item_name__icontains=search) |
                Q(seller_name__icontains=search)
            )
            
        if start_date:
            queryset = queryset.filter(date__gte=start_date)
            
        if end_date:
            queryset = queryset.filter(date__lte=end_date)
            
        if seller_name:
            queryset = queryset.filter(seller_name__icontains=seller_name)
            
        if payment_method:
            queryset = queryset.filter(payment_method=payment_method)
            
        if main_category:
            queryset = queryset.filter(main_category_id=main_category)
            
        if sub_category:
            queryset = queryset.filter(sub_category_id=sub_category)
            
        return queryset

class QuickSaleViewSet(viewsets.ModelViewSet):
    queryset = QuickSale.objects.all().order_by('-created_at')  # FIX: Default to newest first
    serializer_class = QuickSaleSerializer
    pagination_class = StandardPagination

    def get_queryset(self):
        # Start with the base queryset that's already ordered by newest first
        queryset = QuickSale.objects.all().order_by('-created_at')
        
        # Get filter parameters
        is_quick_sale = self.request.query_params.get('is_quick_sale')
        is_completed = self.request.query_params.get('is_completed')
        status = self.request.query_params.get('status')
        search = self.request.query_params.get('search')
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        
        # Apply filters
        if is_quick_sale:
            queryset = queryset.filter(is_quick_sale=True)
        
        if is_completed is not None:
            queryset = queryset.filter(is_completed=is_completed.lower() == 'true')
        
        if status:
            queryset = queryset.filter(status=status)
            
        if search:
            queryset = queryset.filter(
                Q(item_name__icontains=search) |
                Q(seller_name__icontains=search) |
                Q(customer_name__icontains=search) |
                Q(buyer_name__icontains=search)
            )
        
        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        if end_date:
            queryset = queryset.filter(date__lte=end_date)
        
        # Handle ordering - FIX: Use Django's ordering parameter
        ordering = self.request.query_params.get('ordering', '-created_at')
        if ordering:
            # Validate the ordering field to prevent SQL injection
            valid_ordering_fields = [
                'created_at', '-created_at', 'date', '-date', 
                'item_name', '-item_name', 'quantity', '-quantity',
                'buying_price', '-buying_price'
            ]
            if ordering in valid_ordering_fields:
                queryset = queryset.order_by(ordering)
        
        return queryset

    # Add this method to handle the pending endpoint properly
    @action(detail=False, methods=['get'])
    def pending(self, request):
        """Get all pending quick sales with proper ordering"""
        try:
            # Get filter parameters
            search = request.query_params.get('search', '')
            main_category = request.query_params.get('main_category', '')
            ordering = request.query_params.get('ordering', '-created_at')
            page = int(request.query_params.get('page', 1))
            page_size = int(request.query_params.get('page_size', 10))
            
            # Start with pending, incomplete quick sales
            queryset = QuickSale.objects.filter(
                is_completed=False,
                status='pending'
            )
            
            # Apply search filter
            if search:
                queryset = queryset.filter(
                    Q(item_name__icontains=search) |
                    Q(seller_name__icontains=search) |
                    Q(customer_name__icontains=search)
                )
            
            # Apply category filter
            if main_category:
                queryset = queryset.filter(main_category_id=main_category)
            
            # Apply date filters if provided
            start_date = request.query_params.get('start_date')
            end_date = request.query_params.get('end_date')
            
            if start_date:
                queryset = queryset.filter(created_at__gte=start_date)
            if end_date:
                queryset = queryset.filter(created_at__lte=end_date)
            
            # Apply ordering - FIX: Ensure newest first by default
            valid_ordering_fields = [
                'created_at', '-created_at', 'date', '-date', 
                'item_name', '-item_name', 'quantity', '-quantity',
                'buying_price', '-buying_price'
            ]
            if ordering in valid_ordering_fields:
                queryset = queryset.order_by(ordering)
            else:
                # Default to newest first
                queryset = queryset.order_by('-created_at')
            
            # Paginate the results
            paginator = StandardPagination()
            paginator.page_size = page_size
            paginated_queryset = paginator.paginate_queryset(queryset, request)
            
            # Serialize the data
            serializer = self.get_serializer(paginated_queryset, many=True)
            
            # Return paginated response
            return paginator.get_paginated_response(serializer.data)
            
        except Exception as e:
            return Response({'error': str(e)}, status=500)
# Summary and Analytics Views
class SalesSummaryView(APIView):
    def get_sales_expenses(self, start_date, end_date):
        sales = Sales.objects.filter(date__range=(start_date, end_date)).aggregate(
            total_sales=Sum('selling_price'),
            total_profit=Sum('profit')
        )
        expenses = Expense.objects.filter(date__range=(start_date, end_date)).aggregate(
            total_expenses=Sum('amount')
        )
        revenue = Revenue.objects.filter(date__range=(start_date, end_date)).aggregate(
            total_revenue=Sum('amount')
        )

        return {
            'sales': sales['total_sales'] or 0,
            'expenses': expenses['total_expenses'] or 0,
            'profit': sales['total_profit'] or 0,
            'revenue': revenue['total_revenue'] or 0,
            'net_profit': (sales['total_profit'] or 0) + (revenue['total_revenue'] or 0) - (expenses['total_expenses'] or 0)
        }

    def get_daily_summary(self):
        today = timezone.now().date()
        return self.get_sales_expenses(today, today)

    def get_weekly_summary(self):
        today = timezone.now().date()
        start_of_week = today - timedelta(days=today.weekday())
        return self.get_sales_expenses(start_of_week, today)

    def get_monthly_summary(self):
        today = timezone.now().date()
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

# Dashboard Statistics
class DashboardStatsView(APIView):
    def get(self, request):
        today = timezone.now().date()
        
        # Today's stats
        today_sales = Sales.objects.filter(date=today).aggregate(
            total_sales=Sum('selling_price'),
            total_profit=Sum('profit'),
            total_items=Sum('quantity')
        ) or {'total_sales': 0, 'total_profit': 0, 'total_items': 0}
        
        today_expenses = Expense.objects.filter(date=today).aggregate(
            total_expenses=Sum('amount')
        ) or {'total_expenses': 0}
        
        today_revenue = Revenue.objects.filter(date=today).aggregate(
            total_revenue=Sum('amount')
        ) or {'total_revenue': 0}
        
        # Weekly stats
        start_of_week = today - timedelta(days=today.weekday())
        weekly_sales = Sales.objects.filter(date__range=[start_of_week, today]).aggregate(
            total_sales=Sum('selling_price')
        ) or {'total_sales': 0}
        
        # Monthly stats
        start_of_month = today.replace(day=1)
        monthly_sales = Sales.objects.filter(date__range=[start_of_month, today]).aggregate(
            total_sales=Sum('selling_price')
        ) or {'total_sales': 0}
        
        # System stats
        low_stock_items = Electronics.objects.filter(quantity__lte=10).count()
        pending_quick_sales = QuickSale.objects.filter(is_completed=False).count()
        total_products = Electronics.objects.count()
        total_categories = Category.objects.count()
        
        stats = {
            'today': {
                'sales': today_sales['total_sales'] or 0,
                'profit': today_sales['total_profit'] or 0,
                'items_sold': today_sales['total_items'] or 0,
                'expenses': today_expenses['total_expenses'] or 0,
                'revenue': today_revenue['total_revenue'] or 0,
            },
            'weekly_sales': weekly_sales['total_sales'] or 0,
            'monthly_sales': monthly_sales['total_sales'] or 0,
            'system': {
                'low_stock_items': low_stock_items,
                'pending_quick_sales': pending_quick_sales,
                'total_products': total_products,
                'total_categories': total_categories,
            }
        }
        
        return Response(stats)

# User Management
@api_view(['GET'])
def UserDetail(request):
    if request.method == "GET":
        user = UserAccount.objects.filter(email=request.GET.get('email'))
        if user:
            js = serializers.serialize('json', user)
            return JsonResponse(js, safe=False)
        else:
            return Response({"error": "user not found"}, status=404)

# Bulk Operations
class BulkOperationsView(APIView):
    def post(self, request, model_type):
        try:
            with transaction.atomic():
                if model_type == 'electronics':
                    serializer = ElectronicsSerializer(data=request.data, many=True)
                elif model_type == 'sales':
                    serializer = SalesSerializer(data=request.data, many=True)
                elif model_type == 'expenses':
                    serializer = ExpenseSerializer(data=request.data, many=True)
                elif model_type == 'revenue':
                    serializer = RevenueSerializer(data=request.data, many=True)
                else:
                    return Response({'error': 'Invalid model type'}, status=400)
                
                if serializer.is_valid():
                    serializer.save()
                    return Response({
                        'message': f'Successfully created {len(serializer.validated_data)} records',
                        'data': serializer.data
                    }, status=201)
                else:
                    return Response({'error': 'Invalid data', 'details': serializer.errors}, status=400)
                    
        except Exception as e:
            return Response({'error': str(e)}, status=400)

# Export Data
class ExportDataView(APIView):
    def get(self, request, model_type):
        try:
            if model_type == 'sales':
                queryset = Sales.objects.all()
                serializer = SalesSerializer
            elif model_type == 'electronics':
                queryset = Electronics.objects.all()
                serializer = ElectronicsSerializer
            elif model_type == 'expenses':
                queryset = Expense.objects.all()
                serializer = ExpenseSerializer
            elif model_type == 'revenue':
                queryset = Revenue.objects.all()
                serializer = RevenueSerializer
            else:
                return Response({'error': 'Invalid model type'}, status=400)
            
            # Apply filters if provided
            start_date = request.query_params.get('start_date')
            end_date = request.query_params.get('end_date')
            
            if start_date and hasattr(queryset.model, 'date'):
                queryset = queryset.filter(date__gte=start_date)
            if end_date and hasattr(queryset.model, 'date'):
                queryset = queryset.filter(date__lte=end_date)
            
            data = serializer(queryset, many=True).data
            
            return Response({
                'count': len(data),
                'data': data,
                'exported_at': timezone.now().isoformat()
            })
            
        except Exception as e:
            return Response({'error': str(e)}, status=400)
        

# Add these imports at the top if not already there
from rest_framework.views import APIView
from django.db.models import Sum, Q
from django.utils import timezone
from datetime import timedelta

# Add these dashboard views to your views.py

class DashboardStatsView(APIView):
    def get(self, request):
        try:
            today = timezone.now().date()
            
            # SIMPLIFIED APPROACH - No complex aggregations with mixed types
            
            # Today's calculations
            today_sales = Sales.objects.filter(date=today)
            today_exchange = Exchange.objects.filter(date=today)
            today_expenses = Expense.objects.filter(date=today)
            today_revenue = Revenue.objects.filter(date=today, is_verified=True)
            today_electronics = Electronics.objects.filter(date_added=today)
            
            # Weekly calculations
            start_of_week = today - timedelta(days=today.weekday())
            week_sales = Sales.objects.filter(date__range=[start_of_week, today])
            week_exchange = Exchange.objects.filter(date__range=[start_of_week, today])
            week_expenses = Expense.objects.filter(date__range=[start_of_week, today])
            week_revenue = Revenue.objects.filter(date__range=[start_of_week, today], is_verified=True)
            
            # Monthly calculations
            start_of_month = today.replace(day=1)
            month_sales = Sales.objects.filter(date__range=[start_of_month, today])
            month_exchange = Exchange.objects.filter(date__range=[start_of_month, today])
            month_expenses = Expense.objects.filter(date__range=[start_of_month, today])
            month_revenue = Revenue.objects.filter(date__range=[start_of_month, today], is_verified=True)
            
            # All time calculations
            all_sales = Sales.objects.all()
            all_exchange = Exchange.objects.all()
            all_expenses = Expense.objects.all()
            all_revenue = Revenue.objects.filter(is_verified=True)
            all_electronics = Electronics.objects.all()
            
            # ===== SIMPLE CALCULATIONS - NO MIXED TYPES =====
            
            # Helper function to safely calculate sums
            def calculate_sum(queryset, field_name):
                total = 0
                for item in queryset:
                    value = getattr(item, field_name)
                    if value is not None:
                        total += float(value)
                return total
            
            # Helper function for exchange total
            def calculate_exchange_total(queryset):
                total = 0
                for item in queryset:
                    estimated = item.estimated_exchange_price or 0
                    additional = item.additional_payment or 0
                    total += float(estimated) + float(additional)
                return total
            
            # Helper function for exchange profit
            def calculate_exchange_profit(queryset):
                total = 0
                for item in queryset:
                    profit = item.profit or 0
                    total += float(profit)
                return total
            
            # Helper function for total purchase
            def calculate_total_purchase(queryset):
                total = 0
                for item in queryset:
                    total += float(item.buying_price) * item.quantity
                return total
            
            # Calculate totals - TODAY
            today_sales_total = calculate_sum(today_sales, 'selling_price')
            today_sales_profit = calculate_sum(today_sales, 'profit')
            today_sales_items = sum(sale.quantity for sale in today_sales)
            
            today_exchange_total = calculate_exchange_total(today_exchange)
            today_exchange_profit = calculate_exchange_profit(today_exchange)
            
            today_expenses_total = calculate_sum(today_expenses, 'amount')
            today_revenue_total = calculate_sum(today_revenue, 'amount')
            
            # Calculate totals - WEEKLY
            week_sales_total = calculate_sum(week_sales, 'selling_price')
            week_sales_profit = calculate_sum(week_sales, 'profit')
            
            week_exchange_total = calculate_exchange_total(week_exchange)
            week_exchange_profit = calculate_exchange_profit(week_exchange)
            
            week_expenses_total = calculate_sum(week_expenses, 'amount')
            week_revenue_total = calculate_sum(week_revenue, 'amount')
            
            # Calculate totals - MONTHLY
            month_sales_total = calculate_sum(month_sales, 'selling_price')
            month_sales_profit = calculate_sum(month_sales, 'profit')
            
            month_exchange_total = calculate_exchange_total(month_exchange)
            month_exchange_profit = calculate_exchange_profit(month_exchange)
            
            month_expenses_total = calculate_sum(month_expenses, 'amount')
            month_revenue_total = calculate_sum(month_revenue, 'amount')
            
            # Calculate totals - ALL TIME
            all_sales_total = calculate_sum(all_sales, 'selling_price')
            all_sales_profit = calculate_sum(all_sales, 'profit')
            
            all_exchange_total = calculate_exchange_total(all_exchange)
            all_exchange_profit = calculate_exchange_profit(all_exchange)
            
            all_expenses_total = calculate_sum(all_expenses, 'amount')
            all_revenue_total = calculate_sum(all_revenue, 'amount')
            all_purchase_total = calculate_total_purchase(all_electronics)
            
            # System stats
            total_product_quantity = sum(item.quantity for item in all_electronics)
            low_stock_items = all_electronics.filter(quantity__lte=10).count()
            total_categories = Category.objects.count()
            total_subcategories = SubCategory.objects.count()
            
            # Transaction counts
            today_transaction_count = (
                today_sales.count() + 
                today_expenses.count() + 
                today_electronics.count() +
                today_exchange.count()
            )
            
            # Recent activities
            recent_sales = today_sales.order_by('-id')[:3]
            recent_purchases = today_electronics.order_by('-id')[:2]
            recent_expenses = today_expenses.order_by('-id')[:2]
            
            # ===== FINAL TOTALS =====
            
            # Today's totals
            today_total_sales = today_sales_total + today_exchange_total
            today_total_profit = today_sales_profit + today_exchange_profit
            today_balance = today_total_sales - today_expenses_total - today_revenue_total
            
            # Weekly totals
            weekly_total_sales = week_sales_total + week_exchange_total
            weekly_total_profit = week_sales_profit + week_exchange_profit
            weekly_balance = weekly_total_sales - week_expenses_total - week_revenue_total
            
            # Monthly totals
            monthly_total_sales = month_sales_total + month_exchange_total
            monthly_total_profit = month_sales_profit + month_exchange_profit
            monthly_balance = monthly_total_sales - month_expenses_total - month_revenue_total
            
            # All time totals
            all_time_total_sales = all_sales_total + all_exchange_total
            all_time_total_profit = all_sales_profit + all_exchange_profit
            all_time_net_balance = all_time_total_sales - all_expenses_total - all_revenue_total
            
            stats = {
                'today': {
                    'date': today.isoformat(),
                    'transaction_count': today_transaction_count,
                    'sales': {
                        'amount': round(today_total_sales, 2),
                        'profit': round(today_total_profit, 2),
                        'items_sold': today_sales_items,
                        'transaction_count': today_sales.count() + today_exchange.count()
                    },
                    'expenses': round(today_expenses_total, 2),
                    'revenue': round(today_revenue_total, 2),
                    'balance': round(today_balance, 2)
                },
                'weekly': {
                    'sales': round(weekly_total_sales, 2),
                    'profit': round(weekly_total_profit, 2),
                    'expenses': round(week_expenses_total, 2),
                    'revenue': round(week_revenue_total, 2),
                    'balance': round(weekly_balance, 2)
                },
                'monthly': {
                    'sales': round(monthly_total_sales, 2),
                    'profit': round(monthly_total_profit, 2),
                    'expenses': round(month_expenses_total, 2),
                    'revenue': round(month_revenue_total, 2),
                    'balance': round(monthly_balance, 2)
                },
                'all_time': {
                    'total_sales': round(all_time_total_sales, 2),
                    'total_profit': round(all_time_total_profit, 2),
                    'total_expenses': round(all_expenses_total, 2),
                    'total_revenue': round(all_revenue_total, 2),
                    'total_purchase': round(all_purchase_total, 2),
                    'net_balance': round(all_time_net_balance, 2)
                },
                'system': {
                    'total_product_quantity': total_product_quantity,
                    'low_stock_items': low_stock_items,
                    'total_categories': total_categories,
                    'total_subcategories': total_subcategories,
                    'total_products': all_electronics.count()
                },
                'exchange': {
                    'today_sales': round(today_exchange_total, 2),
                    'today_profit': round(today_exchange_profit, 2),
                    'today_count': today_exchange.count(),
                    'all_time_sales': round(all_exchange_total, 2),
                    'all_time_profit': round(all_exchange_profit, 2)
                },
                'recent_activities': {
                    'sales': SalesSerializer(recent_sales, many=True).data,
                    'purchases': ElectronicsSerializer(recent_purchases, many=True).data,
                    'expenses': ExpenseSerializer(recent_expenses, many=True).data
                },
                'calculation_notes': {
                    'revenue_includes_only_verified': True,
                    'exchange_sales_includes_estimated_plus_additional': True,
                    'all_values_rounded_to_2_decimals': True,
                    'simple_calculation_method': True
                }
            }
            
            return Response(stats, status=200)
            
        except Exception as e:
            import traceback
            print(f"Dashboard calculation error: {str(e)}")
            print(f"Traceback: {traceback.format_exc()}")
            return Response({'error': f'Calculation error: {str(e)}'}, status=500)        
class DashboardRecentActivityView(APIView):
    def get(self, request):
        try:
            today = timezone.now().date()
            
            # Get recent activities from last 7 days
            week_ago = today - timedelta(days=7)
            
            recent_sales = Sales.objects.filter(date__gte=week_ago).order_by('-date', '-id')[:10]
            recent_exchanges = Exchange.objects.filter(date__gte=week_ago).order_by('-date', '-id')[:10]
            recent_expenses = Expense.objects.filter(date__gte=week_ago).order_by('-date', '-id')[:10]
            recent_purchases = Electronics.objects.filter(date_added__gte=week_ago).order_by('-date_added', '-id')[:10]
            recent_revenue = Revenue.objects.filter(date__gte=week_ago, is_verified=True).order_by('-date', '-id')[:10]
            
            activities = []
            
            # Process sales
            for sale in recent_sales:
                activities.append({
                    'type': 'sale',
                    'title': f'Sale: {sale.item_name}',
                    'description': f'{sale.quantity} items sold for ${sale.selling_price}',
                    'amount': float(sale.selling_price),
                    'date': sale.date.isoformat(),
                    'icon': 'cart-shopping',
                    'color': 'green'
                })
            
            # Process exchanges
            for exchange in recent_exchanges:
                activities.append({
                    'type': 'exchange',
                    'title': f'Exchange: {exchange.item_name}',
                    'description': f'Exchanged for {exchange.new_item_name}',
                    'amount': float(exchange.estimated_exchange_price + exchange.additional_payment),
                    'date': exchange.date.isoformat(),
                    'icon': 'exchange-alt',
                    'color': 'blue'
                })
            
            # Process expenses
            for expense in recent_expenses:
                activities.append({
                    'type': 'expense',
                    'title': f'Expense: {expense.name}',
                    'description': expense.description or 'No description',
                    'amount': float(expense.amount),
                    'date': expense.date.isoformat(),
                    'icon': 'money-bill-wave',
                    'color': 'red'
                })
            
            # Process purchases
            for purchase in recent_purchases:
                activities.append({
                    'type': 'purchase',
                    'title': f'Purchase: {purchase.name}',
                    'description': f'{purchase.quantity} items added to inventory',
                    'amount': float(purchase.buying_price),
                    'date': purchase.date_added.isoformat(),
                    'icon': 'box-open',
                    'color': 'purple'
                })
            
            # Process revenue
            for revenue in recent_revenue:
                activities.append({
                    'type': 'revenue',
                    'title': f'Revenue: {revenue.name}',
                    'description': f'Received by {revenue.recievername}',
                    'amount': float(revenue.amount),
                    'date': revenue.date.isoformat(),
                    'icon': 'dollar-sign',
                    'color': 'green'
                })
            
            # Sort by date (newest first)
            activities.sort(key=lambda x: x['date'], reverse=True)
            
            return Response(activities[:15], status=200)
            
        except Exception as e:
            import traceback
            print(f"Recent activities error: {str(e)}")
            print(f"Traceback: {traceback.format_exc()}")
            return Response({'error': str(e)}, status=500)
        
# Add this to your views.py

class TodayTransactionsView(APIView):
    def get(self, request):
        try:
            today = timezone.now().date()
            
            # Get today's data
            today_sales = Sales.objects.filter(date=today)
            today_expenses = Expense.objects.filter(date=today)
            today_purchases = Electronics.objects.filter(date_added=today)
            
            # Calculate totals
            total_sales = sum(float(sale.selling_price) for sale in today_sales)
            total_expenses = sum(float(expense.amount) for expense in today_expenses)
            total_purchases = sum(float(purchase.buying_price) for purchase in today_purchases)
            total_profit = sum(float(sale.profit or 0) for sale in today_sales)
            
            # Prepare transactions data
            transactions = []
            
            # Add sales transactions
            for sale in today_sales:
                transactions.append({
                    'id': f"sale_{sale.id}",
                    'type': 'sale',
                    'name': sale.item_name,
                    'description': f"Sold {sale.quantity} items",
                    'amount': float(sale.selling_price),
                    'quantity': sale.quantity,
                    'timestamp': sale.date.isoformat(),
                    'profit': float(sale.profit or 0),
                    'seller': sale.seller_name,
                    'buyer': sale.buyer_name,
                    'payment_method': sale.payment_method,
                    'status': sale.status
                })
            
            # Add expense transactions
            for expense in today_expenses:
                transactions.append({
                    'id': f"expense_{expense.id}",
                    'type': 'expense',
                    'name': expense.name,
                    'description': expense.description or "No description",
                    'amount': float(expense.amount),
                    'timestamp': expense.date.isoformat(),
                    'is_verified': expense.is_verified
                })
            
            # Add purchase transactions
            for purchase in today_purchases:
                transactions.append({
                    'id': f"purchase_{purchase.id}",
                    'type': 'purchase',
                    'name': purchase.name,
                    'description': f"Added {purchase.quantity} items to inventory",
                    'amount': float(purchase.buying_price),
                    'quantity': purchase.quantity,
                    'timestamp': purchase.date_added.isoformat(),
                    'size': purchase.size,
                    'added_by': purchase.added_by,
                    'category': purchase.main_category.name if purchase.main_category else None,
                    'subcategory': purchase.sub_category.name if purchase.sub_category else None
                })
            
            # Sort transactions by timestamp (newest first)
            transactions.sort(key=lambda x: x['timestamp'], reverse=True)
            
            # Prepare summary
            summary = {
                'date': today.isoformat(),
                'total_transactions': len(transactions),
                'sales_count': today_sales.count(),
                'expenses_count': today_expenses.count(),
                'purchases_count': today_purchases.count(),
                'total_sales': round(total_sales, 2),
                'total_expenses': round(total_expenses, 2),
                'total_purchases': round(total_purchases, 2),
                'total_profit': round(total_profit, 2),
                'net_flow': round(total_sales - total_purchases - total_expenses, 2),
                'transactions': transactions
            }
            
            return Response(summary, status=200)
            
        except Exception as e:
            import traceback
            print(f"Today transactions error: {str(e)}")
            print(f"Traceback: {traceback.format_exc()}")
            return Response({'error': f'Failed to fetch transactions: {str(e)}'}, status=500)
 # Add these to your views.py

class InventorySummaryView(APIView):
    def get(self, request):
        try:
            # Get all electronics with related data
            electronics_data = Electronics.objects.all()
            
            # Calculate inventory metrics
            total_items = electronics_data.count()
            total_quantity = sum(item.quantity for item in electronics_data)
            out_of_stock = electronics_data.filter(quantity=0).count()
            low_stock = electronics_data.filter(quantity__lte=2, quantity__gt=0).count()
            total_value = sum(float(item.buying_price) * item.quantity for item in electronics_data)
            
            summary = {
                'total_items': total_items,
                'total_quantity': total_quantity,
                'out_of_stock': out_of_stock,
                'low_stock': low_stock,
                'total_value': round(total_value, 2)
            }
            
            return Response(summary, status=200)
            
        except Exception as e:
            return Response({'error': str(e)}, status=500)

class InventoryItemsView(APIView):
    def get(self, request):
        try:
            # Get all query parameters with defaults
            search = request.query_params.get('search', '').strip()
            category = request.query_params.get('category', 'all')
            stock_status = request.query_params.get('stock_status', 'all')
            sort_by = request.query_params.get('sort_by', 'id')
            sort_order = request.query_params.get('sort_order', 'desc')
            page = int(request.query_params.get('page', 1))
            page_size = int(request.query_params.get('page_size', 10))
            
            # DEBUG: Print received parameters
            print(f"DEBUG - Received parameters:")
            print(f"  search: {search}")
            print(f"  category: {category}")
            print(f"  stock_status: {stock_status}")
            print(f"  sort_by: {sort_by}")
            print(f"  sort_order: {sort_order}")
            print(f"  page: {page}")
            print(f"  page_size: {page_size}")
            
            # Validate page parameters
            if page < 1:
                page = 1
            if page_size < 1 or page_size > 100:
                page_size = 10
            
            # Start with base queryset
            queryset = Electronics.objects.select_related('main_category', 'sub_category').all()
            
            # Apply search filter
            if search:
                queryset = queryset.filter(name__icontains=search)
            
            # Apply category filter
            if category != 'all':
                queryset = queryset.filter(main_category_id=category)
            
            # Apply stock status filter
            if stock_status != 'all':
                if stock_status == 'out-of-stock':
                    queryset = queryset.filter(quantity=0)
                elif stock_status == 'low-stock':
                    queryset = queryset.filter(quantity__range=[1, 2])
                elif stock_status == 'in-stock':
                    queryset = queryset.filter(quantity__gt=2)
            
            # DEBUG: Print queryset before sorting
            print(f"DEBUG - Queryset count before sorting: {queryset.count()}")
            
            # Apply sorting with validation
            valid_sort_fields = ['id', 'name', 'quantity', 'buying_price', 'date_added']
            if sort_by in valid_sort_fields:
                if sort_order == 'desc':
                    sort_field = f'-{sort_by}'
                else:
                    sort_field = sort_by
                queryset = queryset.order_by(sort_field)
                print(f"DEBUG - Applied sorting: {sort_field}")
            else:
                # Default sorting to newest first
                queryset = queryset.order_by('-id')
                print(f"DEBUG - Applied default sorting: -id")
            
            # DEBUG: Check first few items to verify sorting
            sample_items = queryset[:5]
            print(f"DEBUG - First 5 item IDs after sorting: {[item.id for item in sample_items]}")
            
            # Calculate pagination
            total_count = queryset.count()
            total_pages = (total_count + page_size - 1) // page_size
            
            # Ensure page is within valid range
            if page > total_pages and total_pages > 0:
                page = total_pages
            
            # Calculate slice indices
            start_index = (page - 1) * page_size
            end_index = start_index + page_size
            
            # Get paginated items
            paginated_items = queryset[start_index:end_index]
            
            # Prepare response data
            items_data = []
            for item in paginated_items:
                # Calculate stock status on backend
                quantity = item.quantity
                if quantity == 0:
                    stock_status_info = 'out-of-stock'
                    stock_status_text = 'Out of Stock'
                    stock_status_color = 'red'
                elif quantity <= 2:
                    stock_status_info = 'low-stock'
                    stock_status_text = 'Low Stock'
                    stock_status_color = 'orange'
                else:
                    stock_status_info = 'in-stock'
                    stock_status_text = 'In Stock'
                    stock_status_color = 'green'
                
                items_data.append({
                    'id': item.id,
                    'name': item.name,
                    'main_category': item.main_category.id if item.main_category else None,
                    'main_category_name': item.main_category.name if item.main_category else 'Unknown',
                    'sub_category': item.sub_category.id if item.sub_category else None,
                    'sub_category_name': item.sub_category.name if item.sub_category else 'Unknown',
                    'size': item.size,
                    'quantity': quantity,
                    'buying_price': float(item.buying_price),
                    'added_by': item.added_by,
                    'date_added': item.date_added.isoformat(),
                    'image': item.image.name if item.image else None,
                    'stock_status': stock_status_info,
                    'stock_status_text': stock_status_text,
                    'stock_status_color': stock_status_color,
                    'item_value': float(item.buying_price) * quantity
                })
            
            # Build pagination info
            pagination_info = {
                'current_page': page,
                'page_size': page_size,
                'total_count': total_count,
                'total_pages': total_pages,
                'has_next': page < total_pages,
                'has_previous': page > 1,
                'next_page': page + 1 if page < total_pages else None,
                'previous_page': page - 1 if page > 1 else None,
                'start_index': start_index + 1 if total_count > 0 else 0,
                'end_index': min(end_index, total_count)
            }
            
            # Build filters info
            filters_info = {
                'search': search,
                'category': category,
                'stock_status': stock_status,
                'sort_by': sort_by,
                'sort_order': sort_order
            }
            
            response_data = {
                'success': True,
                'items': items_data,
                'pagination': pagination_info,
                'filters': filters_info,
                'summary': {
                    'filtered_count': total_count,
                    'displaying_count': len(items_data)
                },
                # DEBUG: Add sorting info to response
                'debug_sorting': {
                    'requested_sort_by': sort_by,
                    'requested_sort_order': sort_order,
                    'applied_sorting': sort_field if 'sort_field' in locals() else '-id'
                }
            }
            
            return Response(response_data, status=200)
            
        except Exception as e:
            import traceback
            print(f"Inventory items error: {str(e)}")
            print(f"Traceback: {traceback.format_exc()}")
            return Response({
                'success': False,
                'error': f'Failed to fetch inventory items: {str(e)}'
            }, status=500)

class InventoryCategoriesView(APIView):
    def get(self, request):
        try:
            categories = Category.objects.all().order_by('name')
            subcategories = SubCategory.objects.all().order_by('name')
            
            data = {
                'success': True,
                'categories': CategorySerializer(categories, many=True).data,
                'subcategories': SubCategorySerializer(subcategories, many=True).data
            }
            
            return Response(data, status=200)
            
        except Exception as e:
            return Response({
                'success': False,
                'error': f'Failed to fetch categories: {str(e)}'
            }, status=500)

class InventoryExportView(APIView):
    def get(self, request):
        try:
            # Get all filter parameters (same as InventoryItemsView)
            search = request.query_params.get('search', '').strip()
            category = request.query_params.get('category', 'all')
            stock_status = request.query_params.get('stock_status', 'all')
            
            # Start with base queryset
            queryset = Electronics.objects.select_related('main_category', 'sub_category').all()
            
            # Apply filters (same logic as InventoryItemsView)
            if search:
                queryset = queryset.filter(name__icontains=search)
            if category != 'all':
                queryset = queryset.filter(main_category_id=category)
            if stock_status != 'all':
                if stock_status == 'out-of-stock':
                    queryset = queryset.filter(quantity=0)
                elif stock_status == 'low-stock':
                    queryset = queryset.filter(quantity__range=[1, 2])
                elif stock_status == 'in-stock':
                    queryset = queryset.filter(quantity__gt=2)
            
            # Order by name for consistent export
            queryset = queryset.order_by('name')
            
            # Prepare export data
            export_data = []
            for item in queryset:
                # Calculate stock status (same logic as InventoryItemsView)
                quantity = item.quantity
                if quantity == 0:
                    stock_status_text = 'Out of Stock'
                elif quantity <= 2:
                    stock_status_text = 'Low Stock'
                else:
                    stock_status_text = 'In Stock'
                
                export_data.append({
                    'ID': item.id,
                    'Product Name': item.name,
                    'Main Category': item.main_category.name if item.main_category else 'Unknown',
                    'Sub Category': item.sub_category.name if item.sub_category else 'Unknown',
                    'Size': item.size or '',
                    'Quantity': quantity,
                    'Buying Price': float(item.buying_price),
                    'Stock Status': stock_status_text,
                    'Added By': item.added_by or '',
                    'Date Added': item.date_added.strftime('%Y-%m-%d'),
                    'Total Value': float(item.buying_price) * quantity
                })
            
            return Response({
                'success': True,
                'export_data': export_data,
                'total_items': len(export_data),
                'filters': {
                    'search': search,
                    'category': category,
                    'stock_status': stock_status
                }
            }, status=200)
            
        except Exception as e:
            return Response({
                'success': False,
                'error': f'Failed to prepare export data: {str(e)}'
            }, status=500)

# Add this to your views.py - FIXED VERSION
class SalesStatisticsView(APIView):
    def get(self, request):
        try:
            # Get filters from request
            filters = request.query_params.dict()
            
            # Apply the same filtering logic as SaleViewSet
            queryset = Sales.objects.all()
            
            search = filters.get('search')
            start_date = filters.get('start_date')
            end_date = filters.get('end_date')
            seller_name = filters.get('seller_name')
            payment_method = filters.get('payment_method')
            main_category = filters.get('main_category')
            sub_category = filters.get('sub_category')
            
            if search:
                queryset = queryset.filter(
                    Q(item_name__icontains=search) |
                    Q(buyer_name__icontains=search) |
                    Q(seller_name__icontains=search)
                )
            
            if start_date:
                queryset = queryset.filter(date__gte=start_date)
                
            if end_date:
                queryset = queryset.filter(date__lte=end_date)
                
            if seller_name:
                queryset = queryset.filter(seller_name__icontains=seller_name)
                
            if payment_method:
                queryset = queryset.filter(payment_method=payment_method)
                
            if main_category:
                queryset = queryset.filter(main_category_id=main_category)
                
            if sub_category:
                queryset = queryset.filter(sub_category_id=sub_category)
            
            # PROPER CALCULATIONS with error handling
            total_sales = queryset.count()
            
            # Use Coalesce to handle None values
            from django.db.models import Value, FloatField
            from django.db.models.functions import Coalesce
            
            revenue_agg = queryset.aggregate(
                total_revenue=Coalesce(Sum('selling_price'), Value(0.0), output_field=FloatField())
            )
            profit_agg = queryset.aggregate(
                total_profit=Coalesce(Sum('profit'), Value(0.0), output_field=FloatField())
            )
            commission_agg = queryset.aggregate(
                total_commission=Coalesce(Sum('commission_amount'), Value(0.0), output_field=FloatField())
            )
            
            total_revenue = float(revenue_agg['total_revenue'])
            total_profit = float(profit_agg['total_profit'])
            total_commission = float(commission_agg['total_commission'])
            
            # Calculate averages safely
            average_revenue = total_revenue / total_sales if total_sales > 0 else 0
            average_profit = total_profit / total_sales if total_sales > 0 else 0
            average_commission = total_commission / total_sales if total_sales > 0 else 0
            
            # Calculate net revenue (revenue - commission)
            net_revenue = total_revenue - total_commission
            
            return Response({
                'totalSales': total_sales,
                'totalRevenue': round(total_revenue, 2),
                'totalProfit': round(total_profit, 2),
                'totalCommission': round(total_commission, 2),
                'netRevenue': round(net_revenue, 2),
                'averageRevenue': round(average_revenue, 2),
                'averageProfit': round(average_profit, 2),
                'averageCommission': round(average_commission, 2),
                'profitMargin': round((total_profit / total_revenue * 100) if total_revenue > 0 else 0, 2)
            })
            
        except Exception as e:
            import traceback
            print(f"Statistics calculation error: {str(e)}")
            print(f"Traceback: {traceback.format_exc()}")
            return Response({'error': f'Statistics calculation failed: {str(e)}'}, status=500)

class SalesExportView(APIView):
    def get(self, request):
        try:
            # Get filters from request
            filters = request.query_params.dict()
            
            # Apply the same filtering logic as SaleViewSet
            queryset = Sales.objects.select_related('main_category', 'sub_category').all()
            
            search = filters.get('search')
            start_date = filters.get('start_date')
            end_date = filters.get('end_date')
            seller_name = filters.get('seller_name')
            payment_method = filters.get('payment_method')
            main_category = filters.get('main_category')
            sub_category = filters.get('sub_category')
            
            if search:
                queryset = queryset.filter(
                    Q(item_name__icontains=search) |
                    Q(buyer_name__icontains=search) |
                    Q(seller_name__icontains=search)
                )
            
            if start_date:
                queryset = queryset.filter(date__gte=start_date)
                
            if end_date:
                queryset = queryset.filter(date__lte=end_date)
                
            if seller_name:
                queryset = queryset.filter(seller_name__icontains=seller_name)
                
            if payment_method:
                queryset = queryset.filter(payment_method=payment_method)
                
            if main_category:
                queryset = queryset.filter(main_category_id=main_category)
                
            if sub_category:
                queryset = queryset.filter(sub_category_id=sub_category)
            
            # Prepare export data with proper calculations
            export_data = []
            for sale in queryset:
                net_amount = (sale.selling_price or 0) - (sale.commission_amount or 0)
                
                export_data.append({
                    'ID': sale.id,
                    'Item Name': sale.item_name,
                    'Main Category': sale.main_category.name if sale.main_category else 'Unknown',
                    'Sub Category': sale.sub_category.name if sale.sub_category else 'Unknown',
                    'Quantity': sale.quantity,
                    'Seller': sale.seller_name,
                    'Buyer': sale.buyer_name or '',
                    'Date': sale.date.isoformat() if sale.date else '',
                    'Payment Method': sale.payment_method,
                    'Selling Price': float(sale.selling_price or 0),
                    'Credit Amount': float(sale.credit_amount or 0),
                    'Commission Amount': float(sale.commission_amount or 0),
                    'Net Amount': float(net_amount),
                    'Profit': float(sale.profit or 0),
                    'Status': sale.status,
                    'Profit Margin %': round((sale.profit / sale.selling_price * 100) if sale.selling_price and sale.selling_price > 0 else 0, 2)
                })
            
            return Response({
                'data': export_data,
                'exported_at': timezone.now().isoformat(),
                'total_records': len(export_data),
                'filters_applied': filters
            })
            
        except Exception as e:
            return Response({'error': str(e)}, status=500)

# Add this to your views.py
class SaleDetailView(APIView):
    def get(self, request, pk):
        try:
            sale = Sales.objects.select_related('main_category', 'sub_category').get(id=pk)
            
            # Prepare detailed sale data with category names
            sale_data = SalesSerializer(sale).data
            
            # Add additional calculated fields
            sale_data['net_amount'] = float(sale.selling_price or 0) - float(sale.commission_amount or 0)
            sale_data['profit_margin'] = round(
                (sale.profit / sale.selling_price * 100) if sale.selling_price and sale.selling_price > 0 else 0, 
                2
            )
            
            return Response(sale_data)
            
        except Sales.DoesNotExist:
            return Response({'error': 'Sale not found'}, status=404)
        except Exception as e:
            return Response({'error': str(e)}, status=500)

# Add to views.py


# REPLACE the current SalesAnalyticsView with this REAL DATA version
class SalesAnalyticsView(APIView):
    def get(self, request):
        try:
            print("=== REAL SALES ANALYTICS ENDPOINT CALLED ===")
            
            # Get real data from database
            sales_queryset = Sales.objects.all()
            electronics_queryset = Electronics.objects.all()
            
            print(f"Found {sales_queryset.count()} sales records")
            print(f"Found {electronics_queryset.count()} electronics records")
            
            # Calculate real metrics
            inventory_data = self.calculate_real_inventory_metrics(electronics_queryset)
            sales_data = self.calculate_real_sales_metrics(sales_queryset)
            analysis_data = self.analyze_real_sales_data(sales_queryset)
            
            # Get today's real sales
            today_sales_data = SalesSerializer(
                sales_queryset.filter(date=timezone.now().date()), 
                many=True
            ).data
            
            # Add formatting and metadata
            response_data = self.format_response_data({
                'inventory': inventory_data,
                'sales': sales_data,
                'analysis': analysis_data,
                'today_sales': today_sales_data
            })
            
            print("=== REAL ANALYTICS SUCCESS ===")
            print(f"Total products: {inventory_data['total_items']}")
            print(f"Total product quantity: {inventory_data['total_product_quantity']}")
            print(f"Total revenue: ${sales_data['total_revenue']:,.2f}")
            print(f"Best sellers found: {len(analysis_data['best_sellers'])}")
            
            return Response(response_data)
            
        except Exception as e:
            print(f"=== REAL ANALYTICS ERROR: {str(e)} ===")
            import traceback
            traceback.print_exc()
            return Response(
                {'error': f'Server error: {str(e)}'}, 
                status=500
            )
    
    def calculate_real_inventory_metrics(self, electronics_queryset):
        """Calculate real inventory metrics from database"""
        try:
            # Get real counts from database
            total_items = electronics_queryset.count()
            
            # Get real quantities using aggregation
            inventory_agg = electronics_queryset.aggregate(
                total_quantity=Sum('quantity'),
                total_purchase_value=Sum('buying_price')
            )
            
            total_product_quantity = inventory_agg['total_quantity'] or 0
            total_purchase_value = inventory_agg['total_purchase_value'] or 0
            
            # Get stock status
            stocklow_items = electronics_queryset.filter(quantity__lte=1, quantity__gt=0).count()
            stockout_items = electronics_queryset.filter(quantity=0).count()
            
            # Calculate stock health
            stock_health_percentage = 0
            if total_items > 0:
                stock_health_percentage = round(((total_items - stockout_items) / total_items) * 100, 2)
            
            return {
                'total_product_quantity': total_product_quantity,
                'total_items': total_items,
                'total_purchase_value': float(total_purchase_value),
                'stocklow_items': stocklow_items,
                'stockout_items': stockout_items,
                'stock_health_percentage': stock_health_percentage
            }
            
        except Exception as e:
            print(f"Inventory calculation error: {e}")
            return {
                'total_product_quantity': 0,
                'total_items': 0,
                'total_purchase_value': 0,
                'stocklow_items': 0,
                'stockout_items': 0,
                'stock_health_percentage': 0
            }
    
    def calculate_real_sales_metrics(self, sales_queryset):
        """Calculate real sales metrics from database"""
        try:
            # Get real sales aggregations
            sales_agg = sales_queryset.aggregate(
                total_revenue=Sum('selling_price'),
                total_transactions=Count('id'),
                unique_items=Count('item_name', distinct=True),
                total_profit=Sum('profit'),
                total_quantity_sold=Sum('quantity')
            )
            
            total_revenue = sales_agg['total_revenue'] or 0
            total_transactions = sales_agg['total_transactions'] or 0
            unique_items_sold = sales_agg['unique_items'] or 0
            total_profit = sales_agg['total_profit'] or 0
            total_quantity_sold = sales_agg['total_quantity_sold'] or 0
            
            # Calculate averages
            average_sale_value = 0
            if total_transactions > 0:
                average_sale_value = round(float(total_revenue) / total_transactions, 2)
            
            average_profit = 0
            if total_transactions > 0:
                average_profit = round(float(total_profit) / total_transactions, 2)
            
            # Today's sales
            today = timezone.now().date()
            today_sales = sales_queryset.filter(date=today)
            today_agg = today_sales.aggregate(
                total_today=Sum('selling_price'),
                count_today=Count('id'),
                profit_today=Sum('profit')
            )
            
            return {
                'total_revenue': float(total_revenue),
                'total_transactions': total_transactions,
                'unique_items_sold': unique_items_sold,
                'total_profit': float(total_profit),
                'total_quantity_sold': total_quantity_sold,
                'average_sale_value': average_sale_value,
                'average_profit': average_profit,
                'total_sales_today': float(today_agg['total_today'] or 0),
                'today_transactions': today_agg['count_today'] or 0,
                'today_profit': float(today_agg['profit_today'] or 0)
            }
            
        except Exception as e:
            print(f"Sales calculation error: {e}")
            return {
                'total_revenue': 0,
                'total_transactions': 0,
                'unique_items_sold': 0,
                'total_profit': 0,
                'total_quantity_sold': 0,
                'average_sale_value': 0,
                'average_profit': 0,
                'total_sales_today': 0,
                'today_transactions': 0,
                'today_profit': 0
            }
    
    def analyze_real_sales_data(self, sales_queryset):
        """Analyze real sales data for best sellers, frequent sellers, etc."""
        try:
            # Use database aggregation for better performance
            from django.db.models import Count, Sum, FloatField
            from django.db.models.functions import Coalesce
            
            # Get top items by quantity (best sellers)
            best_sellers_agg = sales_queryset.values('item_name').annotate(
                total_quantity=Sum('quantity'),
                total_revenue=Sum('selling_price'),
                transaction_count=Count('id'),
                total_profit=Sum('profit')
            ).order_by('-total_quantity')[:10]
            
            # Get frequent sellers
            frequent_sellers_agg = sales_queryset.values('item_name').annotate(
                transaction_count=Count('id'),
                total_quantity=Sum('quantity'),
                total_revenue=Sum('selling_price')
            ).order_by('-transaction_count')[:10]
            
            # Get top revenue
            top_revenue_agg = sales_queryset.values('item_name').annotate(
                total_revenue=Sum('selling_price'),
                total_quantity=Sum('quantity'),
                transaction_count=Count('id')
            ).order_by('-total_revenue')[:10]
            
            # Convert to list format with proper structure
            best_sellers = []
            for i, item in enumerate(best_sellers_agg):
                avg_quantity = item['total_quantity'] / item['transaction_count'] if item['transaction_count'] > 0 else 0
                best_sellers.append({
                    'name': item['item_name'],
                    'total_quantity': item['total_quantity'],
                    'total_revenue': float(item['total_revenue'] or 0),
                    'transaction_count': item['transaction_count'],
                    'total_profit': float(item['total_profit'] or 0),
                    'average_quantity': round(avg_quantity, 1),
                    'rank': i + 1,
                    'badge_color': self.get_badge_color(i),
                    'badge_text': self.get_badge_text(i)
                })
            
            frequent_sellers = []
            for i, item in enumerate(frequent_sellers_agg):
                frequent_sellers.append({
                    'name': item['item_name'],
                    'transaction_count': item['transaction_count'],
                    'total_quantity': item['total_quantity'],
                    'total_revenue': float(item['total_revenue'] or 0),
                    'rank': i + 1
                })
            
            top_revenue = []
            for i, item in enumerate(top_revenue_agg):
                top_revenue.append({
                    'name': item['item_name'],
                    'total_revenue': float(item['total_revenue'] or 0),
                    'total_quantity': item['total_quantity'],
                    'transaction_count': item['transaction_count'],
                    'rank': i + 1
                })
            
            # Monthly trends (simplified - use recent 15 sales)
            monthly_trends = []
            recent_sales = sales_queryset.order_by('-date')[:15]
            for sale in recent_sales:
                monthly_trends.append({
                    'month': sale.date.strftime('%Y-%m') if sale.date else 'Unknown',
                    'item_name': sale.item_name or 'Unknown',
                    'quantity': sale.quantity or 0,
                    'revenue': float(sale.selling_price or 0),
                    'profit': float(sale.profit or 0)
                })
            
            return {
                'best_sellers': best_sellers,
                'frequent_sellers': frequent_sellers,
                'top_revenue': top_revenue,
                'monthly_trends': monthly_trends
            }
            
        except Exception as e:
            print(f"Sales analysis error: {e}")
            return self.get_empty_analysis()
    
    def format_response_data(self, data):
        """Add formatted values for frontend display"""
        try:
            # Format inventory values
            data['inventory']['total_product_quantity_formatted'] = f"{data['inventory']['total_product_quantity']:,}"
            data['inventory']['total_items_formatted'] = f"{data['inventory']['total_items']:,}"
            data['inventory']['total_purchase_value_formatted'] = f"${data['inventory']['total_purchase_value']:,.2f}"
            data['inventory']['stock_health_percentage_formatted'] = f"{data['inventory']['stock_health_percentage']}%"
            
            # Format sales values
            data['sales']['total_revenue_formatted'] = f"${data['sales']['total_revenue']:,.2f}"
            data['sales']['total_sales_today_formatted'] = f"${data['sales']['total_sales_today']:,.2f}"
            data['sales']['average_sale_value_formatted'] = f"${data['sales']['average_sale_value']:,.2f}"
            data['sales']['total_profit_formatted'] = f"${data['sales']['total_profit']:,.2f}"
            data['sales']['average_profit_formatted'] = f"${data['sales']['average_profit']:,.2f}"
            data['sales']['total_quantity_sold_formatted'] = f"{data['sales']['total_quantity_sold']:,}"
            
            # Format analysis values
            for item in data['analysis']['best_sellers']:
                item['total_quantity_formatted'] = f"{item['total_quantity']:,}"
                item['total_revenue_formatted'] = f"${item['total_revenue']:,.2f}"
                item['total_profit_formatted'] = f"${item['total_profit']:,.2f}"
                item['average_quantity_formatted'] = f"{item['average_quantity']:.1f}"
                item['average_revenue_formatted'] = f"${item['total_revenue'] / item['transaction_count']:,.2f}" if item['transaction_count'] > 0 else '$0.00'
                
            for item in data['analysis']['frequent_sellers']:
                item['total_quantity_formatted'] = f"{item['total_quantity']:,}"
                item['total_revenue_formatted'] = f"${item['total_revenue']:,.2f}"
                
            for item in data['analysis']['top_revenue']:
                item['total_revenue_formatted'] = f"${item['total_revenue']:,.2f}"
                item['total_quantity_formatted'] = f"{item['total_quantity']:,}"
            
            for trend in data['analysis']['monthly_trends']:
                trend['revenue_formatted'] = f"${trend['revenue']:,.2f}"
                trend['quantity_formatted'] = f"{trend['quantity']:,}"
                trend['profit_formatted'] = f"${trend['profit']:,.2f}"
        
            # Format today's sales
            for sale in data['today_sales']:
                if 'selling_price' in sale:
                    sale['selling_price_formatted'] = f"${float(sale.get('selling_price', 0)):,.2f}"
            
            return data
            
        except Exception as e:
            print(f"Formatting error: {e}")
            return data
    
    def get_badge_color(self, index):
        """Get badge color based on rank"""
        if index == 0: return 'bg-yellow-100 text-yellow-800'
        if index == 1: return 'bg-gray-100 text-gray-800'
        if index == 2: return 'bg-orange-100 text-orange-800'
        return 'bg-blue-100 text-blue-800'
    
    def get_badge_text(self, index):
        """Get badge text based on rank"""
        if index == 0: return '1st'
        if index == 1: return '2nd'
        if index == 2: return '3rd'
        return f'{index + 1}th'
    
    def get_empty_analysis(self):
        """Return empty analysis structure"""
        return {
            'best_sellers': [],
            'frequent_sellers': [],
            'top_revenue': [],
            'monthly_trends': []
        }
    

def get_analytics_with_metadata(self, sales_queryset, electronics_queryset):
    """Get complete analytics with all metadata needed for frontend"""
    try:
        # Calculate all metrics
        inventory_data = self.calculate_inventory_metrics(electronics_queryset)
        sales_data = self.calculate_sales_metrics(sales_queryset)
        analysis_data = self.analyze_sales_data(sales_queryset)
        
        # Get today's sales
        today_sales_data = SalesSerializer(
            sales_queryset.filter(date=timezone.now().date()), 
            many=True
        ).data
        
        # Add performance badges to analysis data
        analysis_data = self.add_performance_metadata(analysis_data)
        
        # Add formatted values for frontend display
        formatted_data = self.add_formatted_values({
            'inventory': inventory_data,
            'sales': sales_data,
            'analysis': analysis_data,
            'today_sales': today_sales_data
        })
        
        return formatted_data
        
    except Exception as e:
        print(f"Metadata generation error: {e}")
        return self.get_empty_response()

def add_performance_metadata(self, analysis_data):
    """Add performance badges and rankings to analysis data"""
    try:
        # Add badges to best sellers
        for i, item in enumerate(analysis_data['best_sellers']):
            item['rank'] = i + 1
            item['badge_color'] = self.get_badge_color(i)
            item['badge_text'] = self.get_badge_text(i)
        
        # Add rankings to other lists
        for i, item in enumerate(analysis_data['frequent_sellers']):
            item['rank'] = i + 1
        
        for i, item in enumerate(analysis_data['top_revenue']):
            item['rank'] = i + 1
            
        return analysis_data
        
    except Exception as e:
        print(f"Performance metadata error: {e}")
        return analysis_data

def get_badge_color(self, index):
    """Get badge color based on rank (moved from frontend)"""
    if index == 0: return 'bg-yellow-100 text-yellow-800'
    if index == 1: return 'bg-gray-100 text-gray-800'
    if index == 2: return 'bg-orange-100 text-orange-800'
    return 'bg-blue-100 text-blue-800'

def get_badge_text(self, index):
    """Get badge text based on rank (moved from frontend)"""
    if index == 0: return '1st'
    if index == 1: return '2nd'
    if index == 2: return '3rd'
    return f'{index + 1}th'

def add_formatted_values(self, data):
    """Add pre-formatted values for frontend display"""
    try:
        # Format inventory values
        data['inventory']['total_product_quantity_formatted'] = f"{data['inventory']['total_product_quantity']:,}"
        data['inventory']['stock_health_percentage_formatted'] = f"{data['inventory']['stock_health_percentage']}%"
        
        # Format sales values
        data['sales']['total_revenue_formatted'] = f"${data['sales']['total_revenue']:,.2f}"
        data['sales']['total_sales_today_formatted'] = f"${data['sales']['total_sales_today']:,.2f}"
        data['sales']['average_sale_value_formatted'] = f"${data['sales']['average_sale_value']:,.2f}"
        
        # Format analysis values
        for item in data['analysis']['best_sellers']:
            item['total_quantity_formatted'] = f"{item['total_quantity']:,}"
            item['total_revenue_formatted'] = f"${item['total_revenue']:,.2f}"
            item['average_quantity_formatted'] = f"{item['average_quantity']:.1f}"
            
        for item in data['analysis']['frequent_sellers']:
            item['total_quantity_formatted'] = f"{item['total_quantity']:,}"
            item['total_revenue_formatted'] = f"${item['total_revenue']:,.2f}"
            
        for item in data['analysis']['top_revenue']:
            item['total_revenue_formatted'] = f"${item['total_revenue']:,.2f}"
            item['total_quantity_formatted'] = f"{item['total_quantity']:,}"
            
        for trend in data['analysis']['monthly_trends']:
            trend['revenue_formatted'] = f"${trend['revenue']:,.2f}"
            trend['quantity_formatted'] = f"{trend['quantity']:,}"
        
        # Format today's sales
        for sale in data['today_sales']:
            if 'selling_price' in sale:
                sale['selling_price_formatted'] = f"${float(sale.get('selling_price', 0)):,.2f}"
        
        return data
        
    except Exception as e:
        print(f"Formatting error: {e}")
        return data

def get_empty_response(self):
    """Return empty response with proper structure"""
    return {
        'inventory': {
            'total_product_quantity': 0,
            'total_product_quantity_formatted': '0',
            'stocklow_items': 0,
            'stockout_items': 0,
            'total_items': 0,
            'stock_health_percentage': 0,
            'stock_health_percentage_formatted': '0%'
        },
        'sales': {
            'total_revenue': 0,
            'total_revenue_formatted': '$0.00',
            'total_transactions': 0,
            'unique_items_sold': 0,
            'average_sale_value': 0,
            'average_sale_value_formatted': '$0.00',
            'total_sales_today': 0,
            'total_sales_today_formatted': '$0.00',
            'today_transactions': 0
        },
        'analysis': {
            'best_sellers': [],
            'frequent_sellers': [],
            'monthly_trends': [],
            'top_revenue': []
        },
        'today_sales': []
    }
class InventoryAlertsView(APIView):
    def get(self, request):
        try:
            low_stock_items = Electronics.objects.filter(quantity__lte=1, quantity__gt=0)
            out_of_stock_items = Electronics.objects.filter(quantity=0)
            
            return Response({
                'low_stock': ElectronicsSerializer(low_stock_items, many=True).data,
                'out_of_stock': ElectronicsSerializer(out_of_stock_items, many=True).data
            })
            
        except Exception as e:
            return Response({'error': str(e)}, status=500)

class BuyingViewSet(viewsets.ModelViewSet):
    queryset = Buying.objects.all().order_by('-date_added')
    serializer_class = BuyingSerializer
    pagination_class = StandardPagination

    def get_queryset(self):
        queryset = Buying.objects.all().order_by('-date_added')
        
        # Add your filtering logic here if needed
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(supplier__icontains=search)
            )
        return queryset

    def perform_create(self, serializer):
        # Get the user from the request
        user_name = getattr(self.request.user, 'name', 'System')
        serializer.save(added_by=user_name)
 
    def list(self, request):
        queryset = self.filter_queryset(self.get_queryset())
        
        # Check if metrics are requested
        include_metrics = request.query_params.get('include_metrics') == 'true'
        
        if include_metrics:
            # Calculate metrics on backend
            metrics = {
                'total_amount': queryset.aggregate(total=Sum('buying_price'))['total'] or 0,
                'total_items': queryset.count(),
                'total_quantity': queryset.aggregate(total=Sum('quantity'))['total'] or 0
            }
            
            # Paginate the data
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response({
                    'results': serializer.data,
                    'metrics': metrics
                })
            
            serializer = self.get_serializer(queryset, many=True)
            return Response({
                'data': serializer.data,
                'metrics': metrics
            })
        else:
            # Normal paginated response
            return super().list(request)


class BuyingSummaryView(APIView):
    def get(self, request):
        try:
            today = timezone.now().date()
            
            # Today's purchases
            today_purchases = Buying.objects.filter(date_added=today)
            today_amount = today_purchases.aggregate(
                total=Sum('buying_price')
            )['total'] or 0
            today_items = today_purchases.count()
            today_quantity = today_purchases.aggregate(
                total=Sum('quantity')
            )['total'] or 0
            
            # This week's purchases
            start_of_week = today - timedelta(days=today.weekday())
            end_of_week = start_of_week + timedelta(days=6)
            week_purchases = Buying.objects.filter(date_added__range=[start_of_week, end_of_week])
            week_amount = week_purchases.aggregate(
                total=Sum('buying_price')
            )['total'] or 0
            week_items = week_purchases.count()
            week_quantity = week_purchases.aggregate(
                total=Sum('quantity')
            )['total'] or 0
            
            # This month's purchases
            start_of_month = today.replace(day=1)
            end_of_month = today
            month_purchases = Buying.objects.filter(date_added__range=[start_of_month, end_of_month])
            month_amount = month_purchases.aggregate(
                total=Sum('buying_price')
            )['total'] or 0
            month_items = month_purchases.count()
            month_quantity = month_purchases.aggregate(
                total=Sum('quantity')
            )['total'] or 0
            
            # All time purchases
            total_purchases = Buying.objects.all()
            total_amount = total_purchases.aggregate(
                total=Sum('buying_price')
            )['total'] or 0
            total_items = total_purchases.count()
            total_quantity = total_purchases.aggregate(
                total=Sum('quantity')
            )['total'] or 0
            
            summary = {
                'today': {
                    'amount': float(today_amount),
                    'items': today_items,
                    'quantity': today_quantity
                },
                'week': {
                    'amount': float(week_amount),
                    'items': week_items,
                    'quantity': week_quantity
                },
                'month': {
                    'amount': float(month_amount),
                    'items': month_items,
                    'quantity': month_quantity
                },
                'total': {
                    'amount': float(total_amount),
                    'items': total_items,
                    'quantity': total_quantity
                }
            }
            
            return Response(summary)
            
        except Exception as e:
            print(f"Error in BuyingSummaryView: {str(e)}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
            return Response(
                {'error': f'Server error: {str(e)}'}, 
                status=500
            )

class BuyingReportsView(APIView):
    def get(self, request):
        try:
            # Get filter parameters
            period = request.query_params.get('period', 'all')
            search = request.query_params.get('search', '')
            
            # Get sorting parameters from frontend with defaults for newest first
            sort_by = request.query_params.get('sort_by', 'id')  # Default to ID
            sort_order = request.query_params.get('sort_order', 'desc')  # Default to descending (highest ID first = newest)
            
            print(f"Sorting parameters received - sort_by: {sort_by}, sort_order: {sort_order}")

            # Start with all purchases
            queryset = Buying.objects.all()
            
            # Apply period filter
            today = timezone.now().date()
            if period == 'today':
                queryset = queryset.filter(date_added=today)
            elif period == 'week':
                start_of_week = today - timedelta(days=today.weekday())
                end_of_week = start_of_week + timedelta(days=6)
                queryset = queryset.filter(date_added__range=[start_of_week, end_of_week])
            elif period == 'month':
                start_of_month = today.replace(day=1)
                end_of_month = today
                queryset = queryset.filter(date_added__range=[start_of_month, end_of_month])
            
            # Apply search filter
            if search:
                queryset = queryset.filter(
                    Q(name__icontains=search) |
                    Q(supplier__icontains=search) |
                    Q(purchase_order__icontains=search)
                )
            
            # Apply sorting based on frontend parameters
            valid_sort_fields = ['id', 'name', 'quantity', 'buying_price', 'date_added', 'supplier']
            
            # Map frontend field names to actual model field names if needed
            field_mapping = {
                'total_cost': 'buying_price'  # For total_cost, sort by buying_price
            }
            
            actual_sort_field = field_mapping.get(sort_by, sort_by)
            
            if actual_sort_field in valid_sort_fields:
                if sort_order == 'desc':
                    sort_field = f'-{actual_sort_field}'
                else:
                    sort_field = actual_sort_field
                queryset = queryset.order_by(sort_field)
                print(f"Applied sorting: {sort_field}")
            else:
                # Fallback to default sorting (highest ID first = newest)
                queryset = queryset.order_by('-id')
                print("Applied default sorting: -id")
            
            # Get the actual item data with proper serialization
            serializer = BuyingSerializer(queryset, many=True)
            buying_data = serializer.data
            
            # Calculate metrics from the actual data
            total_amount = sum(float(item['buying_price']) * item['quantity'] for item in buying_data)
            total_items = len(buying_data)
            total_quantity = sum(item['quantity'] for item in buying_data)
            
            response_data = {
                'results': buying_data,  # This contains the actual item list
                'metrics': {
                    'total_amount': total_amount,
                    'total_items': total_items,
                    'total_quantity': total_quantity
                },
                # Return sorting info for debugging
                'sorting_applied': {
                    'sort_by': sort_by,
                    'sort_order': sort_order,
                    'actual_field': actual_sort_field
                }
            }
            
            return Response(response_data)
            
        except Exception as e:
            print(f"Error in BuyingReportsView: {str(e)}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
            return Response(
                {'error': f'Server error: {str(e)}'}, 
                status=500
            )

class OutOfStockItemsView(APIView):
    def get(self, request):
        try:
            # Get all query parameters
            search = request.query_params.get('search', '').strip()
            category = request.query_params.get('category', 'all')
            sort_by = request.query_params.get('sort_by', '-id')  # Default: highest ID first
            sort_order = request.query_params.get('sort_order', 'desc')
            page = int(request.query_params.get('page', 1))
            page_size = int(request.query_params.get('page_size', 10))
            
            # Validate page parameters
            if page < 1:
                page = 1
            if page_size < 1 or page_size > 100:
                page_size = 10
            
            # Start with out of stock items only
            queryset = Electronics.objects.filter(quantity=0).select_related('main_category', 'sub_category')
            
            # Apply search filter
            if search:
                queryset = queryset.filter(name__icontains=search)
            
            # Apply category filter
            if category != 'all':
                queryset = queryset.filter(main_category_id=category)
            
            # Handle sorting - ensure ID is always sorted descending by default
            valid_sort_fields = ['id', 'name', 'buying_price', 'date_added']
            if sort_by.lstrip('-') in valid_sort_fields:
                # If sort_order is provided, use it to determine direction
                if sort_order == 'desc' and not sort_by.startswith('-'):
                    sort_by = f'-{sort_by}'
                elif sort_order == 'asc' and sort_by.startswith('-'):
                    sort_by = sort_by.lstrip('-')
            else:
                # Default sorting: highest ID first
                sort_by = '-id'
            
            queryset = queryset.order_by(sort_by)
            
            # Calculate pagination
            total_count = queryset.count()
            total_pages = (total_count + page_size - 1) // page_size
            
            # Ensure page is within valid range
            if page > total_pages and total_pages > 0:
                page = total_pages
            
            # Calculate slice indices
            start_index = (page - 1) * page_size
            end_index = start_index + page_size
            
            # Get paginated items
            paginated_items = queryset[start_index:end_index]
            
            # Calculate metrics
            total_value = sum(float(item.buying_price) * item.quantity for item in queryset)
            
            # Category breakdown
            category_breakdown = {}
            for item in queryset:
                if item.main_category:
                    category_name = item.main_category.name
                    category_breakdown[category_name] = category_breakdown.get(category_name, 0) + 1
            
            # Prepare items data
            items_data = []
            for item in paginated_items:
                items_data.append({
                    'id': item.id,
                    'name': item.name,
                    'main_category': item.main_category.id if item.main_category else None,
                    'main_category_name': item.main_category.name if item.main_category else 'Unknown',
                    'sub_category': item.sub_category.id if item.sub_category else None,
                    'sub_category_name': item.sub_category.name if item.sub_category else 'Unknown',
                    'size': item.size,
                    'quantity': item.quantity,
                    'buying_price': float(item.buying_price),
                    'added_by': item.added_by,
                    'date_added': item.date_added.isoformat(),
                    'stock_status': 'out-of-stock',
                    'stock_status_text': 'Out of Stock',
                    'stock_status_color': 'red'
                })
            
            # Build pagination info
            pagination_info = {
                'current_page': page,
                'page_size': page_size,
                'total_count': total_count,
                'total_pages': total_pages,
                'has_next': page < total_pages,
                'has_previous': page > 1,
                'next_page': page + 1 if page < total_pages else None,
                'previous_page': page - 1 if page > 1 else None
            }
            
            # Build metrics
            metrics = {
                'total_items': total_count,
                'total_value': round(total_value, 2),
                'categories_affected': len(category_breakdown),
                'category_breakdown': category_breakdown
            }
            
            # Get categories for dropdown
            all_categories = Category.objects.all().order_by('name')
            categories_data = CategorySerializer(all_categories, many=True).data
            
            response_data = {
                'success': True,
                'items': items_data,
                'pagination': pagination_info,
                'metrics': metrics,
                'categories': categories_data,  # Include categories in response
                'filters': {
                    'search': search,
                    'category': category,
                    'sort_by': sort_by.lstrip('-'),
                    'sort_order': 'desc' if sort_by.startswith('-') else 'asc'
                }
            }
            
            return Response(response_data, status=200)
            
        except Exception as e:
            import traceback
            print(f"Out of stock items error: {str(e)}")
            print(f"Traceback: {traceback.format_exc()}")
            return Response({
                'success': False,
                'error': f'Failed to fetch out of stock items: {str(e)}'
            }, status=500)
    def get(self, request):
        try:
            # Get all query parameters
            search = request.query_params.get('search', '').strip()
            category = request.query_params.get('category', 'all')
            sort_by = request.query_params.get('sort_by', '-id')  # Default: highest ID first
            sort_order = request.query_params.get('sort_order', 'desc')
            page = int(request.query_params.get('page', 1))
            page_size = int(request.query_params.get('page_size', 10))
            
            # Validate page parameters
            if page < 1:
                page = 1
            if page_size < 1 or page_size > 100:
                page_size = 10
            
            # Start with out of stock items only
            queryset = Electronics.objects.filter(quantity=0).select_related('main_category', 'sub_category')
            
            # Apply search filter
            if search:
                queryset = queryset.filter(name__icontains=search)
            
            # Apply category filter
            if category != 'all':
                queryset = queryset.filter(main_category_id=category)
            
            # Handle sorting - ensure ID is always sorted descending by default
            valid_sort_fields = ['id', 'name', 'buying_price', 'date_added']
            if sort_by.lstrip('-') in valid_sort_fields:
                # If sort_order is provided, use it to determine direction
                if sort_order == 'desc' and not sort_by.startswith('-'):
                    sort_by = f'-{sort_by}'
                elif sort_order == 'asc' and sort_by.startswith('-'):
                    sort_by = sort_by.lstrip('-')
            else:
                # Default sorting: highest ID first
                sort_by = '-id'
            
            queryset = queryset.order_by(sort_by)
            
            # Calculate pagination
            total_count = queryset.count()
            total_pages = (total_count + page_size - 1) // page_size
            
            # Ensure page is within valid range
            if page > total_pages and total_pages > 0:
                page = total_pages
            
            # Calculate slice indices
            start_index = (page - 1) * page_size
            end_index = start_index + page_size
            
            # Get paginated items
            paginated_items = queryset[start_index:end_index]
            
            # Calculate metrics
            total_value = sum(float(item.buying_price) * item.quantity for item in queryset)
            
            # Category breakdown
            category_breakdown = {}
            for item in queryset:
                if item.main_category:
                    category_name = item.main_category.name
                    category_breakdown[category_name] = category_breakdown.get(category_name, 0) + 1
            
            # Prepare items data
            items_data = []
            for item in paginated_items:
                items_data.append({
                    'id': item.id,
                    'name': item.name,
                    'main_category': item.main_category.id if item.main_category else None,
                    'main_category_name': item.main_category.name if item.main_category else 'Unknown',
                    'sub_category': item.sub_category.id if item.sub_category else None,
                    'sub_category_name': item.sub_category.name if item.sub_category else 'Unknown',
                    'size': item.size,
                    'quantity': item.quantity,
                    'buying_price': float(item.buying_price),
                    'added_by': item.added_by,
                    'date_added': item.date_added.isoformat(),
                    'stock_status': 'out-of-stock',
                    'stock_status_text': 'Out of Stock',
                    'stock_status_color': 'red'
                })
            
            # Build pagination info
            pagination_info = {
                'current_page': page,
                'page_size': page_size,
                'total_count': total_count,
                'total_pages': total_pages,
                'has_next': page < total_pages,
                'has_previous': page > 1,
                'next_page': page + 1 if page < total_pages else None,
                'previous_page': page - 1 if page > 1 else None
            }
            
            # Build metrics
            metrics = {
                'total_items': total_count,
                'total_value': round(total_value, 2),
                'categories_affected': len(category_breakdown),
                'category_breakdown': category_breakdown
            }
            
            response_data = {
                'success': True,
                'items': items_data,
                'pagination': pagination_info,
                'metrics': metrics,
                'filters': {
                    'search': search,
                    'category': category,
                    'sort_by': sort_by.lstrip('-'),
                    'sort_order': 'desc' if sort_by.startswith('-') else 'asc'
                }
            }
            
            return Response(response_data, status=200)
            
        except Exception as e:
            import traceback
            print(f"Out of stock items error: {str(e)}")
            print(f"Traceback: {traceback.format_exc()}")
            return Response({
                'success': False,
                'error': f'Failed to fetch out of stock items: {str(e)}'
            }, status=500)

# Add to your views.py

class LowStockItemsView(APIView):
    def get(self, request):
        try:
            # Get query parameters
            search = request.query_params.get('search', '').strip()
            category = request.query_params.get('category', 'all')
            sort_by = request.query_params.get('sort_by', 'name')
            sort_order = request.query_params.get('sort_order', 'asc')
            page = int(request.query_params.get('page', 1))
            page_size = int(request.query_params.get('page_size', 10))
            
            # Validate parameters
            if page < 1:
                page = 1
            if page_size < 1 or page_size > 100:
                page_size = 10
            
            # Get low stock items (quantity <= 2 and > 0)
            queryset = Electronics.objects.filter(
                quantity__lte=2, 
                quantity__gt=0
            ).select_related('main_category', 'sub_category')
            
            # Apply search filter
            if search:
                queryset = queryset.filter(name__icontains=search)
            
            # Apply category filter
            if category != 'all':
                queryset = queryset.filter(main_category_id=category)
            
            # Apply sorting
            valid_sort_fields = ['id', 'name', 'quantity', 'buying_price', 'date_added']
            if sort_by in valid_sort_fields:
                if sort_order == 'desc':
                    sort_by = f'-{sort_by}'
                queryset = queryset.order_by(sort_by)
            else:
                queryset = queryset.order_by('name')
            
            # Calculate metrics BEFORE pagination
            total_items = queryset.count()
            critical_items = queryset.filter(quantity=1).count()
            warning_items = queryset.filter(quantity=2).count()
            total_value = sum(
                float(item.buying_price) * item.quantity 
                for item in queryset
            )
            
            # Category breakdown
            categories = Category.objects.all()
            by_category = {}
            for cat in categories:
                count = queryset.filter(main_category=cat).count()
                if count > 0:
                    by_category[cat.name] = count
            
            # Paginate results
            total_pages = (total_items + page_size - 1) // page_size
            if page > total_pages and total_pages > 0:
                page = total_pages
            
            start_index = (page - 1) * page_size
            end_index = start_index + page_size
            paginated_items = queryset[start_index:end_index]
            
            # Prepare items data
            items_data = []
            for item in paginated_items:
                # Determine stock level
                quantity = item.quantity
                if quantity == 1:
                    stock_level = 'critical'
                    stock_level_text = 'Critical'
                    stock_level_color = 'red'
                elif quantity == 2:
                    stock_level = 'warning'
                    stock_level_text = 'Warning'
                    stock_level_color = 'orange'
                else:
                    stock_level = 'low'
                    stock_level_text = 'Low'
                    stock_level_color = 'yellow'
                
                items_data.append({
                    'id': item.id,
                    'name': item.name,
                    'main_category': item.main_category.id if item.main_category else None,
                    'main_category_name': item.main_category.name if item.main_category else 'Unknown',
                    'sub_category': item.sub_category.id if item.sub_category else None,
                    'sub_category_name': item.sub_category.name if item.sub_category else 'Unknown',
                    'size': item.size,
                    'quantity': quantity,
                    'buying_price': float(item.buying_price),
                    'added_by': item.added_by,
                    'date_added': item.date_added.isoformat(),
                    'stock_level': stock_level,
                    'stock_level_text': stock_level_text,
                    'stock_level_color': stock_level_color,
                    'item_value': float(item.buying_price) * quantity
                })
            
            # Build pagination info
            pagination_info = {
                'current_page': page,
                'page_size': page_size,
                'total_count': total_items,
                'total_pages': total_pages,
                'has_next': page < total_pages,
                'has_previous': page > 1,
                'next_page': page + 1 if page < total_pages else None,
                'previous_page': page - 1 if page > 1 else None,
                'start_index': start_index + 1 if total_items > 0 else 0,
                'end_index': min(end_index, total_items)
            }
            
            # Build metrics
            metrics = {
                'total_items': total_items,
                'critical_items': critical_items,
                'warning_items': warning_items,
                'total_value': round(total_value, 2),
                'by_category': by_category
            }
            
            # Build filters info
            filters_info = {
                'search': search,
                'category': category,
                'sort_by': sort_by.lstrip('-') if sort_by.startswith('-') else sort_by,
                'sort_order': 'desc' if sort_by.startswith('-') else 'asc'
            }
            
            response_data = {
                'success': True,
                'items': items_data,
                'metrics': metrics,
                'pagination': pagination_info,
                'filters': filters_info,
                'summary': {
                    'filtered_count': total_items,
                    'displaying_count': len(items_data)
                }
            }
            
            return Response(response_data, status=200)
            
        except Exception as e:
            import traceback
            print(f"Low stock items error: {str(e)}")
            print(f"Traceback: {traceback.format_exc()}")
            return Response({
                'success': False,
                'error': f'Failed to fetch low stock items: {str(e)}'
            }, status=500)


class LowStockExportView(APIView):
    def get(self, request):
        try:
            # Get filter parameters
            search = request.query_params.get('search', '').strip()
            category = request.query_params.get('category', 'all')
            
            # Get low stock items with filters
            queryset = Electronics.objects.filter(
                quantity__lte=2, 
                quantity__gt=0
            ).select_related('main_category', 'sub_category')
            
            if search:
                queryset = queryset.filter(name__icontains=search)
            
            if category != 'all':
                queryset = queryset.filter(main_category_id=category)
            
            # Order by name for consistent export
            queryset = queryset.order_by('name')
            
            # Prepare export data
            export_data = []
            for item in queryset:
                # Determine stock level
                quantity = item.quantity
                if quantity == 1:
                    stock_level_text = 'Critical'
                elif quantity == 2:
                    stock_level_text = 'Warning'
                else:
                    stock_level_text = 'Low'
                
                export_data.append({
                    'ID': item.id,
                    'Product Name': item.name,
                    'Main Category': item.main_category.name if item.main_category else 'Unknown',
                    'Sub Category': item.sub_category.name if item.sub_category else 'Unknown',
                    'Size': item.size or '',
                    'Quantity': quantity,
                    'Buying Price': float(item.buying_price),
                    'Stock Level': stock_level_text,
                    'Added By': item.added_by or '',
                    'Date Added': item.date_added.strftime('%Y-%m-%d'),
                    'Total Value': float(item.buying_price) * quantity
                })
            
            return Response({
                'success': True,
                'export_data': export_data,
                'total_items': len(export_data),
                'exported_at': timezone.now().isoformat(),
                'filters': {
                    'search': search,
                    'category': category
                }
            }, status=200)
            
        except Exception as e:
            return Response({
                'success': False,
                'error': f'Failed to prepare export data: {str(e)}'
            }, status=500)
        

# Add to your views.py


class CategoryManagementView(APIView):
    def get(self, request):
        try:
            # Get paginated categories
            categories = Category.objects.all().order_by('name')
            
            # Get all subcategories with their category information
            subcategories = SubCategory.objects.select_related('main_category').all()
            
            # Calculate statistics
            total_categories = categories.count()
            total_subcategories = subcategories.count()
            
            stats = {
                'total_categories': total_categories,
                'total_subcategories': total_subcategories,
                'average_subcategories': round(total_subcategories / total_categories, 1) if total_categories > 0 else 0,
            }
            
            # Prepare categories with their subcategories
            categories_data = []
            for category in categories:
                category_subs = subcategories.filter(main_category=category)
                categories_data.append({
                    'id': category.id,
                    'name': category.name,
                    'subcategories': SubCategorySerializer(category_subs, many=True).data,
                    'subcategories_count': category_subs.count()
                })
            
            return Response({
                'stats': stats,
                'categories': categories_data,
                'all_subcategories': SubCategorySerializer(subcategories, many=True).data
            }, status=200)
            
        except Exception as e:
            return Response({'error': str(e)}, status=500)
        

class ExpenseStatisticsView(APIView):
    def get(self, request):
        try:
            expenses = Expense.objects.all()
            
            stats = {
                'total_expenses': expenses.count(),
                'verified_expenses': expenses.filter(is_verified=True).count(),
                'total_amount': expenses.aggregate(total=Sum('amount'))['total'] or 0,
                'pending_verification': expenses.filter(is_verified=False).count(),
                'average_amount': expenses.aggregate(avg=Avg('amount'))['avg'] or 0,
                'this_month_expenses': expenses.filter(
                    date__month=timezone.now().month,
                    date__year=timezone.now().year
                ).count(),
                'this_month_amount': expenses.filter(
                    date__month=timezone.now().month,
                    date__year=timezone.now().year
                ).aggregate(total=Sum('amount'))['total'] or 0
            }
            
            return Response(stats, status=200)
            
        except Exception as e:
            import traceback
            print(f"Expense statistics error: {str(e)}")
            print(f"Traceback: {traceback.format_exc()}")
            return Response({'error': f'Statistics calculation failed: {str(e)}'}, status=500)

class ExpenseExportView(APIView):
    def get(self, request):
        try:
            # Get filters from query parameters
            search = request.query_params.get('search', '')
            filter_verified = request.query_params.get('filter_verified', 'all')
            
            # Apply the same filtering logic as ExpenseViewSet
            queryset = Expense.objects.all()
            
            if search:
                queryset = queryset.filter(
                    Q(name__icontains=search) |
                    Q(description__icontains=search)
                )
            
            if filter_verified != 'all':
                if filter_verified == 'verified':
                    queryset = queryset.filter(is_verified=True)
                elif filter_verified == 'pending':
                    queryset = queryset.filter(is_verified=False)
            
            # Order by latest first
            queryset = queryset.order_by('-id')
            
            # Prepare export data - REMOVE created_at since it doesn't exist
            export_data = []
            for expense in queryset:
                export_data.append({
                    'ID': expense.id,
                    'Submitter': expense.name,
                    'Amount': float(expense.amount),
                    'Date': expense.date.isoformat() if expense.date else '',
                    'Description': expense.description or '',
                    'Status': 'Verified' if expense.is_verified else 'Pending',
                    'Verified': 'Yes' if expense.is_verified else 'No'
                    # Removed 'Created_At' since field doesn't exist
                })
            
            return Response({
                'data': export_data,
                'total_records': len(export_data),
                'exported_at': timezone.now().isoformat(),
                'filters_applied': {
                    'search': search,
                    'filter_verified': filter_verified
                }
            }, status=200)
            
        except Exception as e:
            return Response({'error': str(e)}, status=500)

class ExpenseStatisticsView(APIView):
    def get(self, request):
        try:
            expenses = Expense.objects.all()
            
            stats = {
                'total_expenses': expenses.count(),
                'verified_expenses': expenses.filter(is_verified=True).count(),
                'total_amount': expenses.aggregate(total=Sum('amount'))['total'] or 0,
                'pending_verification': expenses.filter(is_verified=False).count(),
                'average_amount': expenses.aggregate(avg=Avg('amount'))['avg'] or 0,
                'this_month_expenses': expenses.filter(
                    date__month=timezone.now().month,
                    date__year=timezone.now().year
                ).count(),
                'this_month_amount': expenses.filter(
                    date__month=timezone.now().month,
                    date__year=timezone.now().year
                ).aggregate(total=Sum('amount'))['total'] or 0
            }
            
            return Response(stats, status=200)
            
        except Exception as e:
            import traceback
            print(f"Expense statistics error: {str(e)}")
            print(f"Traceback: {traceback.format_exc()}")
            return Response({'error': f'Statistics calculation failed: {str(e)}'}, status=500)

class ExpenseExportView(APIView):
    def get(self, request):
        try:
            # Get filters from query parameters
            search = request.query_params.get('search', '')
            filter_verified = request.query_params.get('filter_verified', 'all')
            
            # Apply the same filtering logic as ExpenseViewSet
            queryset = Expense.objects.all()
            
            if search:
                queryset = queryset.filter(
                    Q(name__icontains=search) |
                    Q(description__icontains=search)
                )
            
            if filter_verified != 'all':
                if filter_verified == 'verified':
                    queryset = queryset.filter(is_verified=True)
                elif filter_verified == 'pending':
                    queryset = queryset.filter(is_verified=False)
            
            # Order by latest first
            queryset = queryset.order_by('-id')
            
            # Prepare export data - NO created_at
            export_data = []
            for expense in queryset:
                export_data.append({
                    'ID': expense.id,
                    'Submitter': expense.name,
                    'Amount': float(expense.amount),
                    'Date': expense.date.isoformat() if expense.date else '',
                    'Description': expense.description or '',
                    'Status': 'Verified' if expense.is_verified else 'Pending',
                    'Verified': 'Yes' if expense.is_verified else 'No'
                })
            
            return Response({
                'data': export_data,
                'total_records': len(export_data),
                'exported_at': timezone.now().isoformat(),
                'filters_applied': {
                    'search': search,
                    'filter_verified': filter_verified
                }
            }, status=200)
            
        except Exception as e:
            return Response({'error': str(e)}, status=500)

class ExpenseListView(APIView):
    def get(self, request):
        try:
            # Get query parameters
            page = int(request.query_params.get('page', 1))
            page_size = int(request.query_params.get('page_size', 10))
            search = request.query_params.get('search', '')
            filter_verified = request.query_params.get('filter_verified', 'all')
            sort_by = request.query_params.get('sort_by', 'id')
            sort_order = request.query_params.get('sort_order', 'desc')
            
            # Validate parameters
            if page < 1:
                page = 1
            if page_size < 1 or page_size > 100:
                page_size = 10
            
            # Start with base queryset
            queryset = Expense.objects.all()
            
            # Apply search filter
            if search:
                queryset = queryset.filter(
                    Q(name__icontains=search) |
                    Q(description__icontains=search)
                )
            
            # Apply verification filter
            if filter_verified != 'all':
                if filter_verified == 'verified':
                    queryset = queryset.filter(is_verified=True)
                elif filter_verified == 'pending':
                    queryset = queryset.filter(is_verified=False)
            
            # Apply sorting
            valid_sort_fields = ['id', 'name', 'amount', 'date', 'is_verified']
            if sort_by in valid_sort_fields:
                if sort_order == 'desc':
                    sort_by = f'-{sort_by}'
                queryset = queryset.order_by(sort_by)
            else:
                # Default sorting by latest
                queryset = queryset.order_by('-id')
            
            # Calculate pagination
            total_count = queryset.count()
            total_pages = (total_count + page_size - 1) // page_size
            
            # Ensure page is within valid range
            if page > total_pages and total_pages > 0:
                page = total_pages
            
            # Calculate slice indices
            start_index = (page - 1) * page_size
            end_index = start_index + page_size
            
            # Get paginated items
            paginated_expenses = queryset[start_index:end_index]
            
            # Prepare response data - NO created_at
            expenses_data = []
            for expense in paginated_expenses:
                expense_data = {
                    'id': expense.id,
                    'name': expense.name,
                    'amount': float(expense.amount),
                    'date': expense.date.isoformat() if expense.date else '',
                    'description': expense.description,
                    'is_verified': expense.is_verified
                }
                expenses_data.append(expense_data)
            
            # Build pagination info
            pagination_info = {
                'current_page': page,
                'page_size': page_size,
                'total_count': total_count,
                'total_pages': total_pages,
                'has_next': page < total_pages,
                'has_previous': page > 1,
                'next_page': page + 1 if page < total_pages else None,
                'previous_page': page - 1 if page > 1 else None
            }
            
            # Build filters info
            filters_info = {
                'search': search,
                'filter_verified': filter_verified,
                'sort_by': sort_by.lstrip('-') if sort_by.startswith('-') else sort_by,
                'sort_order': 'desc' if sort_by.startswith('-') else 'asc'
            }
            
            response_data = {
                'success': True,
                'expenses': expenses_data,
                'pagination': pagination_info,
                'filters': filters_info,
                'summary': {
                    'filtered_count': total_count,
                    'displaying_count': len(expenses_data)
                }
            }
            
            return Response(response_data, status=200)
            
        except Exception as e:
            import traceback
            print(f"Expense list error: {str(e)}")
            print(f"Traceback: {traceback.format_exc()}")
            return Response({
                'success': False,
                'error': f'Failed to fetch expenses: {str(e)}'
                
            }, status=500)

# Add these to your views.py


    def get(self, request):
        try:
            # Simple response to get the endpoint working
            return Response({
                'period': '30days',
                'overview': {
                    'total_sales': 0,
                    'total_revenue': 0,
                    'total_profit': 0,
                    'average_order_value': 0,
                    'profit_margin': 0
                },
                'top_items': [],
                'category_sales': [],
                'daily_trends': [],
                'seller_performance': [],
                'calculated_at': timezone.now().isoformat()
            }, status=200)
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=500)
        

class SalesReportsView(APIView):
    def get(self, request):
        try:
            # Get query parameters
            view_type = request.query_params.get('view', 'overview')
            search = request.query_params.get('search', '').strip()
            day = request.query_params.get('day', '')
            month = request.query_params.get('month', '')
            page_size = int(request.query_params.get('page_size', 10))
            page = int(request.query_params.get('page', 1))
            
            # Validate page parameters
            if page < 1:
                page = 1
            if page_size < 1 or page_size > 100:
                page_size = 10
            
            today = timezone.now().date()
            start_of_week = today - timedelta(days=today.weekday())
            start_of_month = today.replace(day=1)
            
            # Base queryset with search
            queryset = Sales.objects.select_related('main_category', 'sub_category').all()
            
            if search:
                queryset = queryset.filter(
                    Q(item_name__icontains=search) |
                    Q(seller_name__icontains=search) |
                    Q(buyer_name__icontains=search) |
                    Q(main_category__name__icontains=search) |  # Add category search
                    Q(sub_category__name__icontains=search)     # Add subcategory search
                )
            
            # Calculate summary data using aggregation for better performance
            today_agg = queryset.filter(date=today).aggregate(
                total_sales=Sum('selling_price'),
                total_quantity=Sum('quantity'),
                total_profit=Sum('profit'),
                transactions=Count('id')
            )
            
            week_agg = queryset.filter(date__range=[start_of_week, today]).aggregate(
                total_sales=Sum('selling_price'),
                total_quantity=Sum('quantity'),
                total_profit=Sum('profit'),
                transactions=Count('id')
            )
            
            month_agg = queryset.filter(date__range=[start_of_month, today]).aggregate(
                total_sales=Sum('selling_price'),
                total_quantity=Sum('quantity'),
                total_profit=Sum('profit'),
                transactions=Count('id')
            )
            
            total_agg = queryset.aggregate(
                total_sales=Sum('selling_price'),
                total_quantity=Sum('quantity'),
                total_profit=Sum('profit'),
                transactions=Count('id')
            )
            
            summary = {
                'today': {
                    'sales': float(today_agg['total_sales'] or 0),
                    'quantity': today_agg['total_quantity'] or 0,
                    'profit': float(today_agg['total_profit'] or 0),
                    'transactions': today_agg['transactions'] or 0
                },
                'week': {
                    'sales': float(week_agg['total_sales'] or 0),
                    'quantity': week_agg['total_quantity'] or 0,
                    'profit': float(week_agg['total_profit'] or 0),
                    'transactions': week_agg['transactions'] or 0
                },
                'month': {
                    'sales': float(month_agg['total_sales'] or 0),
                    'quantity': month_agg['total_quantity'] or 0,
                    'profit': float(month_agg['total_profit'] or 0),
                    'transactions': month_agg['transactions'] or 0
                },
                'total': {
                    'sales': float(total_agg['total_sales'] or 0),
                    'quantity': total_agg['total_quantity'] or 0,
                    'profit': float(total_agg['total_profit'] or 0),
                    'transactions': total_agg['transactions'] or 0
                }
            }
            
            response_data = {
                'success': True,
                'summary': summary,
                'detailed_data': [],
                'view_metrics': {},
                'pagination': {},
                'filters': {
                    'view': view_type,
                    'search': search,
                    'day': day,
                    'month': month
                }
            }
            
            # Handle detailed views
            if view_type in ['today', 'week', 'month']:
                if view_type == 'today':
                    view_queryset = queryset.filter(date=today)
                elif view_type == 'week':
                    view_queryset = queryset.filter(date__range=[start_of_week, today])
                    if day:
                        try:
                            # Convert day string to integer and handle week_day filter
                            day_int = int(day)
                            # Django week_day: 1=Sunday, 2=Monday, ..., 7=Saturday
                            view_queryset = view_queryset.filter(date__week_day=day_int + 1)
                        except (ValueError, TypeError):
                            pass  # If day conversion fails, ignore the filter
                elif view_type == 'month':
                    view_queryset = queryset.filter(date__range=[start_of_month, today])
                    if month:
                        try:
                            month_int = int(month)
                            # Add 1 because months are 1-12 in Django
                            view_queryset = view_queryset.filter(date__month=month_int + 1)
                        except (ValueError, TypeError):
                            pass  # If month conversion fails, ignore the filter
                
                # Calculate view metrics using aggregation
                view_metrics_agg = view_queryset.aggregate(
                    total_sales=Sum('selling_price'),
                    total_quantity=Sum('quantity'),
                    total_profit=Sum('profit'),
                    total_transactions=Count('id')
                )
                
                response_data['view_metrics'] = {
                    'total_sales': float(view_metrics_agg['total_sales'] or 0),
                    'total_quantity': view_metrics_agg['total_quantity'] or 0,
                    'total_profit': float(view_metrics_agg['total_profit'] or 0),
                    'total_transactions': view_metrics_agg['total_transactions'] or 0
                }
                
                # Apply pagination
                total_count = view_queryset.count()
                total_pages = (total_count + page_size - 1) // page_size
                
                if page > total_pages and total_pages > 0:
                    page = total_pages
                
                start_index = (page - 1) * page_size
                end_index = start_index + page_size
                
                # Get paginated data ordered by date
                paginated_queryset = view_queryset.order_by('-date', '-id')[start_index:end_index]
                
                # Prepare detailed data - ADDED CATEGORY AND SUBCATEGORY FIELDS
                detailed_data = []
                for sale in paginated_queryset:
                    detailed_data.append({
                        'id': sale.id,
                        'date': sale.date.isoformat() if sale.date else '',
                        'formatted_date': sale.date.strftime('%Y-%m-%d') if sale.date else '',
                        'item_name': sale.item_name,
                        'quantity': sale.quantity,
                        'selling_price': float(sale.selling_price or 0),
                        'profit': float(sale.profit or 0),
                        'seller_name': sale.seller_name,
                        'buyer_name': sale.buyer_name or '',
                        'payment_method': sale.payment_method,
                        'status': sale.status,
                        # ADD THESE CATEGORY FIELDS:
                        'main_category_name': sale.main_category.name if sale.main_category else 'N/A',
                        'sub_category_name': sale.sub_category.name if sale.sub_category else 'N/A'
                    })
                
                response_data['detailed_data'] = detailed_data
                response_data['pagination'] = {
                    'current_page': page,
                    'page_size': page_size,
                    'total_count': total_count,
                    'total_pages': total_pages,
                    'has_next': page < total_pages,
                    'has_previous': page > 1,
                    'next_page': page + 1 if page < total_pages else None,
                    'previous_page': page - 1 if page > 1 else None,
                    'start_index': start_index + 1 if total_count > 0 else 0,
                    'end_index': min(end_index, total_count)
                }
            
            return Response(response_data, status=200)
            
        except Exception as e:
            import traceback
            error_traceback = traceback.format_exc()
            print(f"Sales reports error: {str(e)}")
            print(f"Traceback: {error_traceback}")
            return Response({
                'success': False,
                'error': f'Failed to generate sales reports: {str(e)}',
                'debug_info': str(e)
            }, status=500)

class SalesPerformanceInsightsView(APIView):
    def get(self, request):
        try:
            today = timezone.now().date()
            start_of_month = today.replace(day=1)
            
            # Get sales data
            today_sales = Sales.objects.filter(date=today)
            month_sales = Sales.objects.filter(date__range=[start_of_month, today])
            all_sales = Sales.objects.all()
            
            # Calculate insights
            # Average daily sales (based on all time)
            total_all_sales = sum(float(sale.selling_price or 0) for sale in all_sales)
            total_days = max(1, (all_sales.last().date - all_sales.first().date).days + 1) if all_sales.exists() else 1
            avg_daily_sales = total_all_sales / total_days
            
            # Items sold today
            items_sold_today = sum(sale.quantity for sale in today_sales)
            
            # Today's profit
            todays_profit = sum(float(sale.profit or 0) for sale in today_sales)
            
            # Monthly daily rate
            total_month_sales = sum(float(sale.selling_price or 0) for sale in month_sales)
            days_in_month = today.day
            monthly_daily_rate = total_month_sales / days_in_month if days_in_month > 0 else 0
            
            insights = {
                'avg_daily_sales': round(avg_daily_sales, 2),
                'items_sold_today': items_sold_today,
                'todays_profit': round(todays_profit, 2),
                'monthly_daily_rate': round(monthly_daily_rate, 2)
            }
            
            return Response({
                'success': True,
                'insights': insights
            }, status=200)
            
        except Exception as e:
            import traceback
            print(f"Sales insights error: {str(e)}")
            print(f"Traceback: {traceback.format_exc()}")
            return Response({
                'success': False,
                'error': f'Failed to generate sales insights: {str(e)}'
            }, status=500)
        
# Add to views.py - Debit Report Views
class DebitReportView(APIView):
    pagination_class = StandardPagination
    
    def get(self, request):
        try:
            # Get query parameters
            search = request.query_params.get('search', '')
            sort_by = request.query_params.get('sort_by', 'id')
            sort_order = request.query_params.get('sort_order', 'desc')
            page = int(request.query_params.get('page', 1))
            page_size = int(request.query_params.get('page_size', 10))
            
            # Validate and sanitize sort parameters
            valid_sort_fields = ['id', 'item_name', 'quantity', 'seller_name', 'buyer_name', 
                               'date', 'payment_method', 'commission_amount', 'selling_price', 
                               'credit_amount', 'profit', 'status']
            
            if sort_by not in valid_sort_fields:
                sort_by = 'id'
            
            # Apply sorting
            if sort_order == 'desc':
                sort_field = f'-{sort_by}'
            else:
                sort_field = sort_by
            
            # Get debit sales with related data
            queryset = Sales.objects.filter(
                payment_method="debit"
            ).select_related('main_category', 'sub_category').order_by(sort_field)
            
            # Apply search filter
            if search:
                queryset = queryset.filter(
                    Q(item_name__icontains=search) |
                    Q(seller_name__icontains=search) |
                    Q(buyer_name__icontains=search)
                )
            
            # Calculate statistics
            total_debits = queryset.count()
            
            # Use Coalesce to handle None values
            from django.db.models import Value, FloatField
            from django.db.models.functions import Coalesce
            
            stats_agg = queryset.aggregate(
                total_credit_amount=Coalesce(Sum('credit_amount'), Value(0.0), output_field=FloatField()),
                paid_debits=Count('id', filter=Q(status='paid')),
                unpaid_debits=Count('id', filter=Q(status='unpaid'))
            )
            
            debit_stats = {
                'totalDebits': total_debits,
                'totalCreditAmount': float(stats_agg['total_credit_amount']),
                'paidDebits': stats_agg['paid_debits'],
                'unpaidDebits': stats_agg['unpaid_debits']
            }
            
            # Apply pagination
            paginator = self.pagination_class()
            paginator.page_size = page_size
            result_page = paginator.paginate_queryset(queryset, request)
            
            # Serialize data with category names
            sales_data = []
            for sale in result_page:
                sales_data.append({
                    'id': sale.id,
                    'item_name': sale.item_name,
                    'main_category': sale.main_category.id if sale.main_category else None,
                    'main_category_name': sale.main_category.name if sale.main_category else 'Unknown',
                    'sub_category': sale.sub_category.id if sale.sub_category else None,
                    'sub_category_name': sale.sub_category.name if sale.sub_category else 'Unknown',
                    'quantity': sale.quantity,
                    'seller_name': sale.seller_name,
                    'buyer_name': sale.buyer_name,
                    'date': sale.date.isoformat() if sale.date else None,
                    'payment_method': sale.payment_method,
                    'commission_amount': float(sale.commission_amount or 0),
                    'selling_price': float(sale.selling_price or 0),
                    'credit_amount': float(sale.credit_amount or 0),
                    'profit': float(sale.profit or 0),
                    'status': sale.status
                })
            
            return Response({
                'success': True,
                'debit_stats': debit_stats,
                'sales': sales_data,
                'pagination': {
                    'count': paginator.page.paginator.count,
                    'total_pages': paginator.page.paginator.num_pages,
                    'current_page': page,
                    'page_size': page_size,
                    'next': paginator.get_next_link(),
                    'previous': paginator.get_previous_link(),
                },
                'filters': {
                    'search': search,
                    'sort_by': sort_by,
                    'sort_order': sort_order
                }
            })
            
        except Exception as e:
            import traceback
            print(f"Debit report error: {str(e)}")
            print(f"Traceback: {traceback.format_exc()}")
            return Response({
                'success': False,
                'error': f'Failed to fetch debit report: {str(e)}'
            }, status=500)

class DebitSaleDetailView(APIView):
    def get(self, request, pk):
        try:
            sale = Sales.objects.select_related('main_category', 'sub_category').get(id=pk)
            
            if sale.payment_method != "debit":
                return Response({'error': 'Sale is not a debit transaction'}, status=400)
            
            sale_data = {
                'id': sale.id,
                'item_name': sale.item_name,
                'main_category': sale.main_category.id if sale.main_category else None,
                'main_category_name': sale.main_category.name if sale.main_category else 'Unknown',
                'sub_category': sale.sub_category.id if sale.sub_category else None,
                'sub_category_name': sale.sub_category.name if sale.sub_category else 'Unknown',
                'quantity': sale.quantity,
                'seller_name': sale.seller_name,
                'buyer_name': sale.buyer_name,
                'date': sale.date.isoformat() if sale.date else None,
                'payment_method': sale.payment_method,
                'commission_amount': float(sale.commission_amount or 0),
                'selling_price': float(sale.selling_price or 0),
                'credit_amount': float(sale.credit_amount or 0),
                'profit': float(sale.profit or 0),
                'status': sale.status,
                'net_amount': float((sale.selling_price or 0) - (sale.commission_amount or 0))
            }
            
            return Response({
                'success': True,
                'sale': sale_data
            })
            
        except Sales.DoesNotExist:
            return Response({'error': 'Debit sale not found'}, status=404)
        except Exception as e:
            return Response({'error': str(e)}, status=500)

class DebitStatusUpdateView(APIView):
    def patch(self, request, pk):
        try:
            with transaction.atomic():
                sale = Sales.objects.get(id=pk)
                
                if sale.payment_method != "debit":
                    return Response({'error': 'Sale is not a debit transaction'}, status=400)
                
                new_status = request.data.get('status')
                if new_status not in ['paid', 'unpaid']:
                    return Response({'error': 'Invalid status'}, status=400)
                
                # Calculate updated values
                if new_status == 'paid':
                    updated_profit = (sale.credit_amount or 0) + (sale.profit or 0)
                    updated_selling_price = (sale.credit_amount or 0) + (sale.selling_price or 0)
                    updated_credit = 0
                else:
                    # If marking as unpaid, we need business logic for what values should be
                    updated_profit = sale.profit
                    updated_selling_price = sale.selling_price
                    updated_credit = sale.credit_amount
                
                sale.status = new_status
                sale.selling_price = updated_selling_price
                sale.profit = updated_profit
                sale.credit_amount = updated_credit
                sale.save()
                
                return Response({
                    'success': True,
                    'message': f'Debit marked as {new_status}',
                    'sale': SalesSerializer(sale).data
                })
                
        except Sales.DoesNotExist:
            return Response({'error': 'Debit sale not found'}, status=404)
        except Exception as e:
            return Response({'error': str(e)}, status=500)

class DebitExportView(APIView):
    def get(self, request):
        try:
            # Get filters from request
            search = request.query_params.get('search', '')
            sort_by = request.query_params.get('sort_by', 'id')
            sort_order = request.query_params.get('sort_order', 'desc')
            
            # Apply the same filtering logic as DebitReportView
            queryset = Sales.objects.filter(
                payment_method="debit"
            ).select_related('main_category', 'sub_category')
            
            if search:
                queryset = queryset.filter(
                    Q(item_name__icontains=search) |
                    Q(seller_name__icontains=search) |
                    Q(buyer_name__icontains=search)
                )
            
            # Apply sorting
            if sort_order == 'desc':
                sort_field = f'-{sort_by}'
            else:
                sort_field = sort_by
            queryset = queryset.order_by(sort_field)
            
            # Prepare export data
            export_data = []
            for sale in queryset:
                export_data.append({
                    'ID': sale.id,
                    'Item Name': sale.item_name,
                    'Main Category': sale.main_category.name if sale.main_category else 'Unknown',
                    'Sub Category': sale.sub_category.name if sale.sub_category else 'Unknown',
                    'Quantity': sale.quantity,
                    'Seller Name': sale.seller_name,
                    'Buyer Name': sale.buyer_name,
                    'Date': sale.date.isoformat() if sale.date else '',
                    'Payment Method': sale.payment_method,
                    'Commission Amount': float(sale.commission_amount or 0),
                    'Selling Price': float(sale.selling_price or 0),
                    'Credit Amount': float(sale.credit_amount or 0),
                    'Profit': float(sale.profit or 0),
                    'Status': sale.status,
                    'Net Amount': float((sale.selling_price or 0) - (sale.commission_amount or 0))
                })
            
            return Response({
                'success': True,
                'export_data': export_data,
                'total_records': len(export_data),
                'exported_at': timezone.now().isoformat()
            })
            
        except Exception as e:
            return Response({
                'success': False,
                'error': f'Failed to export debit data: {str(e)}'
            }, status=500)

# Add to views.py - Exchange Report Views
# Replace the ExchangeReportView in views.py with this fixed version
# End of previous view (make sure it ends properly)
    def get_empty_response(self):
        """Return empty response with proper structure"""
        return {
            'inventory': {
                'total_product_quantity': 0,
                'total_product_quantity_formatted': '0',
                'stocklow_items': 0,
                'stockout_items': 0,
                'total_items': 0,
                'stock_health_percentage': 0,
                'stock_health_percentage_formatted': '0%'
            },
            'sales': {
                'total_revenue': 0,
                'total_revenue_formatted': '$0.00',
                'total_transactions': 0,
                'unique_items_sold': 0,
                'average_sale_value': 0,
                'average_sale_value_formatted': '$0.00',
                'total_sales_today': 0,
                'total_sales_today_formatted': '$0.00',
                'today_transactions': 0
            },
            'analysis': {
                'best_sellers': [],
                'frequent_sellers': [],
                'monthly_trends': [],
                'top_revenue': []
            },
            'today_sales': []
        }


# Replace your ExchangeReportView with this enhanced version
class ExchangeReportView(APIView):
    pagination_class = StandardPagination
    
    def get(self, request):
        try:
            print("=== EXCHANGE REPORT API CALLED ===")
            
            # Get query parameters
            search = request.query_params.get('search', '')
            sort_by = request.query_params.get('sort_by', 'id')
            sort_order = request.query_params.get('sort_order', 'desc')
            page = int(request.query_params.get('page', 1))
            page_size = int(request.query_params.get('page_size', 10))
            
            print(f"Params - search: '{search}', sort_by: '{sort_by}', sort_order: '{sort_order}'")
            
            # Build queryset
            queryset = Exchange.objects.select_related(
                'main_category', 'sub_category', 'new_item_sub_category'
            ).all()
            
            print(f"Initial queryset count: {queryset.count()}")
            
            # Apply search filter
            if search:
                queryset = queryset.filter(
                    Q(item_name__icontains=search) |
                    Q(new_item_name__icontains=search) |
                    Q(seller_name__icontains=search)
                )
                print(f"After search filter: {queryset.count()}")
            
            # Apply sorting
            if sort_order == 'desc':
                sort_field = f'-{sort_by}'
            else:
                sort_field = sort_by
            queryset = queryset.order_by(sort_field)
            
            print(f"Applied sorting: {sort_field}")
            
            # Calculate statistics
            total_exchanges = queryset.count()
            print(f"Total exchanges for stats: {total_exchanges}")
            
            # Calculate totals
            total_profit = 0
            total_exchange_value = 0
            
            for exchange in queryset:
                total_profit += float(exchange.profit or 0)
                total_exchange_value += float((exchange.estimated_exchange_price or 0) + (exchange.additional_payment or 0))
            
            average_profit = round(total_profit / total_exchanges, 2) if total_exchanges > 0 else 0
            
            exchange_stats = {
                'totalExchanges': total_exchanges,
                'totalProfit': round(total_profit, 2),
                'totalExchangeValue': round(total_exchange_value, 2),
                'averageProfit': average_profit
            }
            
            print(f"Calculated stats: {exchange_stats}")
            
            # Apply pagination
            paginator = self.pagination_class()
            paginator.page_size = page_size
            
            result_page = paginator.paginate_queryset(queryset, request)
            print(f"Paginated results count: {len(result_page) if result_page else 0}")
            
            # Serialize data
            exchange_data = []
            if result_page:
                for exchange in result_page:
                    try:
                        # Get category names
                        main_category_name = exchange.main_category.name if exchange.main_category else 'Unknown'
                        sub_category_name = exchange.sub_category.name if exchange.sub_category else 'Unknown'
                        new_item_category_name = exchange.new_item_sub_category.name if exchange.new_item_sub_category else 'Unknown'
                        
                        exchange_data.append({
                            'id': exchange.id,
                            'item_name': exchange.item_name or '',
                            'main_category': exchange.main_category.id if exchange.main_category else None,
                            'main_category_name': main_category_name,
                            'sub_category': exchange.sub_category.id if exchange.sub_category else None,
                            'sub_category_name': sub_category_name,
                            'size': '',  # Placeholder since model doesn't have size
                            'new_item_name': exchange.new_item_name or '',
                            'new_item_sub_category': exchange.new_item_sub_category.id if exchange.new_item_sub_category else None,
                            'new_item_sub_category_name': new_item_category_name,
                            'new_item_size': '',  # Placeholder since model doesn't have new_item_size
                            'quantity': exchange.quantity or 0,
                            'seller_name': exchange.seller_name or '',
                            'date': exchange.date.isoformat() if exchange.date else '',
                            'payment_method': exchange.payment_method or '',
                            'estimated_exchange_price': float(exchange.estimated_exchange_price or 0),
                            'additional_payment': float(exchange.additional_payment or 0),
                            'commission_amount': float(exchange.commission_amount or 0),
                            'profit': float(exchange.profit or 0),
                            'total_exchange_value': float((exchange.estimated_exchange_price or 0) + (exchange.additional_payment or 0))
                        })
                    except Exception as item_error:
                        print(f"Error processing exchange {exchange.id}: {str(item_error)}")
                        continue
            
            print(f"✅ Final exchange data count: {len(exchange_data)}")
            
            response_data = {
                'success': True,
                'exchange_stats': exchange_stats,
                'exchanges': exchange_data,
                'pagination': {
                    'count': paginator.page.paginator.count,
                    'total_pages': paginator.page.paginator.num_pages,
                    'current_page': page,
                    'page_size': page_size,
                    'next': paginator.get_next_link(),
                    'previous': paginator.get_previous_link(),
                },
                'filters': {
                    'search': search,
                    'sort_by': sort_by,
                    'sort_order': sort_order
                }
            }
            
            return Response(response_data)
            
        except Exception as e:
            import traceback
            print(f"=== EXCHANGE REPORT ERROR ===")
            print(f"Error: {str(e)}")
            print(f"Traceback: {traceback.format_exc()}")
            return Response({
                'success': False,
                'error': f'Server error: {str(e)}'
            }, status=500)
class ExchangeDetailView(APIView):
    def get(self, request, pk):
        try:
            print(f"=== EXCHANGE DETAIL API CALLED for ID: {pk} ===")
            
            exchange = Exchange.objects.select_related(
                'main_category', 'sub_category', 'new_item_sub_category'
            ).get(id=pk)
            
            print(f"Found exchange: {exchange.id} - {exchange.item_name}")
            
            # Get category names safely
            main_category_name = 'Unknown'
            sub_category_name = 'Unknown'
            new_item_category_name = 'Unknown'
            
            if exchange.main_category:
                main_category_name = exchange.main_category.name
                print(f"Main category: {main_category_name}")
            if exchange.sub_category:
                sub_category_name = exchange.sub_category.name
                print(f"Sub category: {sub_category_name}")
            if exchange.new_item_sub_category:
                new_item_category_name = exchange.new_item_sub_category.name
                print(f"New item category: {new_item_category_name}")
            
            exchange_data = {
                'id': exchange.id,
                'item_name': exchange.item_name or '',
                'main_category': exchange.main_category.id if exchange.main_category else None,
                'main_category_name': main_category_name,
                'sub_category': exchange.sub_category.id if exchange.sub_category else None,
                'sub_category_name': sub_category_name,
                'size': '',  # Your model doesn't have size field
                'new_item_name': exchange.new_item_name or '',
                'new_item_sub_category': exchange.new_item_sub_category.id if exchange.new_item_sub_category else None,
                'new_item_sub_category_name': new_item_category_name,
                'new_item_size': '',  # Your model doesn't have new_item_size field
                'quantity': exchange.quantity or 0,
                'seller_name': exchange.seller_name or '',
                'date': exchange.date.isoformat() if exchange.date else '',
                'payment_method': exchange.payment_method or '',
                'estimated_exchange_price': float(exchange.estimated_exchange_price or 0),
                'additional_payment': float(exchange.additional_payment or 0),
                'commission_amount': float(exchange.commission_amount or 0),
                'profit': float(exchange.profit or 0),
                'total_exchange_value': float((exchange.estimated_exchange_price or 0) + (exchange.additional_payment or 0))
            }
            
            print(f"✅ Successfully prepared exchange data for ID: {pk}")
            
            return Response({
                'success': True,
                'exchange': exchange_data
            })
            
        except Exchange.DoesNotExist:
            print(f"❌ Exchange with ID {pk} not found")
            return Response({'error': 'Exchange record not found'}, status=404)
        except Exception as e:
            import traceback
            error_traceback = traceback.format_exc()
            print(f"=== EXCHANGE DETAIL ERROR ===")
            print(f"Error: {str(e)}")
            print(f"Traceback: {error_traceback}")
            print(f"=== END ERROR ===")
            return Response({'error': str(e)}, status=500)


class ExchangeExportView(APIView):
    def get(self, request):
        try:
            # Get filters from request
            search = request.query_params.get('search', '')
            sort_by = request.query_params.get('sort_by', 'id')
            sort_order = request.query_params.get('sort_order', 'desc')
            
            # Apply the same filtering logic as ExchangeReportView
            queryset = Exchange.objects.select_related(
                'main_category', 'sub_category', 'new_item_sub_category'
            )
            
            if search:
                queryset = queryset.filter(
                    Q(item_name__icontains=search) |
                    Q(new_item_name__icontains=search) |
                    Q(seller_name__icontains=search)
                )
            
            # Apply sorting
            if sort_order == 'desc':
                sort_field = f'-{sort_by}'
            else:
                sort_field = sort_by
            queryset = queryset.order_by(sort_field)
            
            # Prepare export data
            export_data = []
            for exchange in queryset:
                total_value = (exchange.estimated_exchange_price or 0) + (exchange.additional_payment or 0)
                
                export_data.append({
                    'ID': exchange.id,
                    'Original Item Name': exchange.item_name,
                    'Original Category': exchange.main_category.name if exchange.main_category else 'Unknown',
                    'Original Subcategory': exchange.sub_category.name if exchange.sub_category else 'Unknown',
                    'Original Size': exchange.size or '',
                    'Exchanged Item Name': exchange.new_item_name,
                    'Exchanged Item Category': exchange.new_item_sub_category.name if exchange.new_item_sub_category else 'Unknown',
                    'Exchanged Item Size': exchange.new_item_size or '',
                    'Quantity': exchange.quantity,
                    'Seller Name': exchange.seller_name,
                    'Date': exchange.date.isoformat() if exchange.date else '',
                    'Payment Method': exchange.payment_method,
                    'Estimated Exchange Price': float(exchange.estimated_exchange_price or 0),
                    'Additional Payment': float(exchange.additional_payment or 0),
                    'Total Exchange Value': float(total_value),
                    'Commission Amount': float(exchange.commission_amount or 0),
                    'Profit': float(exchange.profit or 0)
                })
            
            return Response({
                'success': True,
                'export_data': export_data,
                'total_records': len(export_data),
                'exported_at': timezone.now().isoformat()
            })
            
        except Exception as e:
            return Response({
                'success': False,
                'error': f'Failed to export exchange data: {str(e)}'
            }, status=500)
        
# Add to views.py - Revenue Report Views
class RevenueReportView(APIView):
    pagination_class = StandardPagination
    
    def get(self, request):
        try:
            print("=== REVENUE REPORT API CALLED ===")
            
            # Get query parameters
            search = request.query_params.get('search', '')
            sort_by = request.query_params.get('sort_by', 'id')
            sort_order = request.query_params.get('sort_order', 'desc')
            page = int(request.query_params.get('page', 1))
            page_size = int(request.query_params.get('page_size', 10))
            
            print(f"Params - search: '{search}', sort_by: '{sort_by}', sort_order: '{sort_order}'")
            
            # Build queryset
            queryset = Revenue.objects.select_related().all()
            
            print(f"Initial queryset count: {queryset.count()}")
            
            # Apply search filter
            if search:
                queryset = queryset.filter(
                    Q(name__icontains=search) |
                    Q(recievername__icontains=search) |
                    Q(description__icontains=search) |
                    Q(reason__icontains=search)
                )
                print(f"After search filter: {queryset.count()}")
            
            # Apply sorting
            valid_sort_fields = ['id', 'name', 'recievername', 'amount', 'date']
            
            if sort_by in valid_sort_fields:
                if sort_order == 'desc':
                    sort_field = f'-{sort_by}'
                else:
                    sort_field = sort_by
                queryset = queryset.order_by(sort_field)
                print(f"Applied sorting: {sort_field}")
            else:
                queryset = queryset.order_by('-id')
                print("Applied default sorting: -id")
            
            # Calculate statistics
            total_records = queryset.count()
            
            # Use aggregation for better performance
            from django.db.models import Sum, Count, Value, FloatField
            from django.db.models.functions import Coalesce
            
            stats_agg = queryset.aggregate(
                total_amount=Coalesce(Sum('amount'), Value(0.0), output_field=FloatField()),
                verified_count=Count('id', filter=Q(is_verified=True)),
                pending_count=Count('id', filter=Q(is_verified=False))
            )
            
            revenue_stats = {
                'totalRecords': total_records,
                'totalAmount': float(stats_agg['total_amount']),
                'verifiedCount': stats_agg['verified_count'],
                'pendingCount': stats_agg['pending_count']
            }
            
            print(f"Calculated stats: {revenue_stats}")
            
            # Apply pagination
            paginator = self.pagination_class()
            paginator.page_size = page_size
            
            result_page = paginator.paginate_queryset(queryset, request)
            print(f"Paginated results: {len(result_page) if result_page else 0} items")
            
            # Serialize data
            revenue_data = []
            if result_page:
                for revenue in result_page:
                    try:
                        revenue_data.append({
                            'id': revenue.id,
                            'name': revenue.name or '',
                            'recievername': revenue.recievername or '',
                            'amount': float(revenue.amount or 0),
                            'date': revenue.date.isoformat() if revenue.date else '',
                            'description': revenue.description or '',
                            'reason': revenue.reason or '',
                            'is_verified': revenue.is_verified
                        })
                    except Exception as item_error:
                        print(f"Error processing revenue {revenue.id}: {str(item_error)}")
                        continue
            
            print(f"✅ Successfully processed {len(revenue_data)} revenue records")
            
            response_data = {
                'success': True,
                'revenue_stats': revenue_stats,
                'revenues': revenue_data,
                'pagination': {
                    'count': paginator.page.paginator.count,
                    'total_pages': paginator.page.paginator.num_pages,
                    'current_page': page,
                    'page_size': page_size,
                    'next': paginator.get_next_link(),
                    'previous': paginator.get_previous_link(),
                },
                'filters': {
                    'search': search,
                    'sort_by': sort_by,
                    'sort_order': sort_order
                }
            }
            
            return Response(response_data)
            
        except Exception as e:
            import traceback
            print(f"=== REVENUE REPORT ERROR ===")
            print(f"Error: {str(e)}")
            print(f"Traceback: {traceback.format_exc()}")
            return Response({
                'success': False,
                'error': f'Failed to fetch revenue report: {str(e)}'
            }, status=500)

class RevenueVerifyView(APIView):
    def patch(self, request, pk):
        try:
            print(f"=== REVENUE VERIFY API CALLED for ID: {pk} ===")
            
            revenue = Revenue.objects.get(id=pk)
            revenue.is_verified = True
            revenue.save()
            
            print(f"✅ Revenue {pk} verified successfully")
            
            return Response({
                'success': True,
                'message': 'Revenue verified successfully',
                'revenue': {
                    'id': revenue.id,
                    'is_verified': revenue.is_verified
                }
            })
            
        except Revenue.DoesNotExist:
            print(f"❌ Revenue with ID {pk} not found")
            return Response({'error': 'Revenue record not found'}, status=404)
        except Exception as e:
            print(f"❌ Revenue verification error: {str(e)}")
            return Response({'error': str(e)}, status=500)

class RevenueExportView(APIView):
    def get(self, request):
        try:
            # Get filters from request
            search = request.query_params.get('search', '')
            sort_by = request.query_params.get('sort_by', 'id')
            sort_order = request.query_params.get('sort_order', 'desc')
            
            # Apply the same filtering logic as RevenueReportView
            queryset = Revenue.objects.all()
            
            if search:
                queryset = queryset.filter(
                    Q(name__icontains=search) |
                    Q(recievername__icontains=search) |
                    Q(description__icontains=search) |
                    Q(reason__icontains=search)
                )
            
            # Apply sorting
            if sort_order == 'desc':
                sort_field = f'-{sort_by}'
            else:
                sort_field = sort_by
            queryset = queryset.order_by(sort_field)
            
            # Prepare export data
            export_data = []
            for revenue in queryset:
                export_data.append({
                    'ID': revenue.id,
                    'Submitter Name': revenue.name,
                    'Receiver Name': revenue.recievername,
                    'Amount': float(revenue.amount or 0),
                    'Date': revenue.date.isoformat() if revenue.date else '',
                    'Description': revenue.description or '',
                    'Reason': revenue.reason or '',
                    'Status': 'Verified' if revenue.is_verified else 'Pending',
                    'Verified': revenue.is_verified
                })
            
            return Response({
                'success': True,
                'export_data': export_data,
                'total_records': len(export_data),
                'exported_at': timezone.now().isoformat()
            })
            
        except Exception as e:
            return Response({
                'success': False,
                'error': f'Failed to export revenue data: {str(e)}'
            }, status=500)
        
# Add to views.py - Revenue Analytics Views
class RevenueAnalyticsView(APIView):
    pagination_class = StandardPagination
    
    def get(self, request):
        try:
            print("=== REVENUE ANALYTICS API CALLED ===")
            
            # Get query parameters
            view_type = request.query_params.get('view', 'overview')  # overview, today, weekly, monthly
            selected_day = request.query_params.get('day', '')
            selected_month = request.query_params.get('month', '')
            search = request.query_params.get('search', '')
            sort_by = request.query_params.get('sort_by', 'date')
            sort_order = request.query_params.get('sort_order', 'desc')
            page = int(request.query_params.get('page', 1))
            page_size = int(request.query_params.get('page_size', 10))
            
            print(f"Params - view: '{view_type}', day: '{selected_day}', month: '{selected_month}', search: '{search}'")
            
            # Get current date for calculations
            today = timezone.now().date()
            current_year = today.year
            
            # Build base queryset
            queryset = Revenue.objects.all()
            
            # Apply view-specific filters
            analytics_data = []
            stats = {}
            
            if view_type == 'overview':
                # Calculate overview statistics
                today_start = today
                today_end = today
                
                # Calculate start of week (Monday)
                start_of_week = today - timedelta(days=today.weekday())
                end_of_week = start_of_week + timedelta(days=6)
                
                # Calculate start of month
                start_of_month = today.replace(day=1)
                next_month = start_of_month.replace(day=28) + timedelta(days=4)
                end_of_month = next_month - timedelta(days=next_month.day)
                
                # Get filtered data for each period
                today_data = queryset.filter(date=today)
                weekly_data = queryset.filter(date__range=[start_of_week, end_of_week])
                monthly_data = queryset.filter(date__range=[start_of_month, end_of_month])
                
                # Calculate totals
                today_total = today_data.aggregate(total=Sum('amount'))['total'] or 0
                weekly_total = weekly_data.aggregate(total=Sum('amount'))['total'] or 0
                monthly_total = monthly_data.aggregate(total=Sum('amount'))['total'] or 0
                
                stats = {
                    'todayExpenses': float(today_total),
                    'weeklyExpenses': float(weekly_total),
                    'monthlyExpenses': float(monthly_total)
                }
                
            elif view_type == 'today':
                # Today's data
                filtered_data = queryset.filter(date=today)
                
                if search:
                    filtered_data = filtered_data.filter(
                        Q(name__icontains=search) |
                        Q(recievername__icontains=search) |
                        Q(reason__icontains=search)
                    )
                
                # Apply sorting
                if sort_order == 'desc':
                    sort_field = f'-{sort_by}'
                else:
                    sort_field = sort_by
                filtered_data = filtered_data.order_by(sort_field)
                
                # Calculate totals
                total_amount = filtered_data.count()
                total_money = filtered_data.aggregate(total=Sum('amount'))['total'] or 0
                
                stats = {
                    'totalAmount': total_amount,
                    'totalMoney': float(total_money)
                }
                
                # Apply pagination for data
                paginator = self.pagination_class()
                paginator.page_size = page_size
                result_page = paginator.paginate_queryset(filtered_data, request)
                
                # Serialize data
                for revenue in result_page:
                    analytics_data.append({
                        'id': revenue.id,
                        'name': revenue.name or '',
                        'recievername': revenue.recievername or '',
                        'amount': float(revenue.amount or 0),
                        'date': revenue.date.isoformat() if revenue.date else '',
                        'description': revenue.description or '',
                        'reason': revenue.reason or '',
                        'is_verified': revenue.is_verified
                    })
                
                stats['pagination'] = {
                    'count': paginator.page.paginator.count,
                    'total_pages': paginator.page.paginator.num_pages,
                    'current_page': page,
                    'page_size': page_size
                }
                
            elif view_type == 'weekly':
                # Calculate week range
                start_of_week = today - timedelta(days=today.weekday())
                end_of_week = start_of_week + timedelta(days=6)
                
                # Get weekly data
                filtered_data = queryset.filter(date__range=[start_of_week, end_of_week])
                
                # Apply day filter if selected
                if selected_day:
                    # Filter by specific day of week (0=Monday, 6=Sunday)
                    # Note: Django's week_day starts with Sunday=1, Saturday=7
                    # Convert from frontend (0=Sunday) to Django (1=Sunday)
                    django_week_day = int(selected_day) + 1
                    filtered_data = filtered_data.filter(date__week_day=django_week_day)
                
                if search:
                    filtered_data = filtered_data.filter(
                        Q(name__icontains=search) |
                        Q(recievername__icontains=search) |
                        Q(reason__icontains=search)
                    )
                
                # Apply sorting
                if sort_order == 'desc':
                    sort_field = f'-{sort_by}'
                else:
                    sort_field = sort_by
                filtered_data = filtered_data.order_by(sort_field)
                
                # Calculate totals
                total_amount = filtered_data.count()
                total_money = filtered_data.aggregate(total=Sum('amount'))['total'] or 0
                
                stats = {
                    'totalAmount': total_amount,
                    'totalMoney': float(total_money),
                    'weekRange': {
                        'start': start_of_week.isoformat(),
                        'end': end_of_week.isoformat()
                    }
                }
                
                # Apply pagination for data
                paginator = self.pagination_class()
                paginator.page_size = page_size
                result_page = paginator.paginate_queryset(filtered_data, request)
                
                # Serialize data
                for revenue in result_page:
                    analytics_data.append({
                        'id': revenue.id,
                        'name': revenue.name or '',
                        'recievername': revenue.recievername or '',
                        'amount': float(revenue.amount or 0),
                        'date': revenue.date.isoformat() if revenue.date else '',
                        'description': revenue.description or '',
                        'reason': revenue.reason or '',
                        'is_verified': revenue.is_verified
                    })
                
                stats['pagination'] = {
                    'count': paginator.page.paginator.count,
                    'total_pages': paginator.page.paginator.num_pages,
                    'current_page': page,
                    'page_size': page_size
                }
                
            elif view_type == 'monthly':
                # Determine month
                if selected_month:
                    month = int(selected_month)
                    year = current_year
                else:
                    month = today.month
                    year = current_year
                
                # Calculate month range
                start_of_month = date(year, month + 1, 1) if selected_month else today.replace(day=1)
                next_month = start_of_month.replace(day=28) + timedelta(days=4)
                end_of_month = next_month - timedelta(days=next_month.day)
                
                # Get monthly data
                filtered_data = queryset.filter(date__range=[start_of_month, end_of_month])
                
                # Apply day filter if selected
                if selected_day:
                    filtered_data = filtered_data.filter(date__day=int(selected_day))
                
                if search:
                    filtered_data = filtered_data.filter(
                        Q(name__icontains=search) |
                        Q(recievername__icontains=search) |
                        Q(reason__icontains=search)
                    )
                
                # Apply sorting
                if sort_order == 'desc':
                    sort_field = f'-{sort_by}'
                else:
                    sort_field = sort_by
                filtered_data = filtered_data.order_by(sort_field)
                
                # Calculate totals
                total_amount = filtered_data.count()
                total_money = filtered_data.aggregate(total=Sum('amount'))['total'] or 0
                
                stats = {
                    'totalAmount': total_amount,
                    'totalMoney': float(total_money),
                    'monthRange': {
                        'start': start_of_month.isoformat(),
                        'end': end_of_month.isoformat()
                    }
                }
                
                # Apply pagination for data
                paginator = self.pagination_class()
                paginator.page_size = page_size
                result_page = paginator.paginate_queryset(filtered_data, request)
                
                # Serialize data
                for revenue in result_page:
                    analytics_data.append({
                        'id': revenue.id,
                        'name': revenue.name or '',
                        'recievername': revenue.recievername or '',
                        'amount': float(revenue.amount or 0),
                        'date': revenue.date.isoformat() if revenue.date else '',
                        'description': revenue.description or '',
                        'reason': revenue.reason or '',
                        'is_verified': revenue.is_verified
                    })
                
                stats['pagination'] = {
                    'count': paginator.page.paginator.count,
                    'total_pages': paginator.page.paginator.num_pages,
                    'current_page': page,
                    'page_size': page_size
                }
            
            response_data = {
                'success': True,
                'view_type': view_type,
                'stats': stats,
                'data': analytics_data,
                'filters': {
                    'selected_day': selected_day,
                    'selected_month': selected_month,
                    'search': search,
                    'sort_by': sort_by,
                    'sort_order': sort_order
                }
            }
            
            print(f"✅ Analytics data prepared - view: {view_type}, records: {len(analytics_data)}")
            
            return Response(response_data)
            
        except Exception as e:
            import traceback
            print(f"=== REVENUE ANALYTICS ERROR ===")
            print(f"Error: {str(e)}")
            print(f"Traceback: {traceback.format_exc()}")
            return Response({
                'success': False,
                'error': f'Failed to fetch revenue analytics: {str(e)}'
            }, status=500)

class RevenueAnalyticsDaysView(APIView):
    def get(self, request):
        """Get days for a specific month (for monthly day filter)"""
        try:
            month = int(request.query_params.get('month', timezone.now().month))
            year = timezone.now().year
            
            # Calculate days in month
            import calendar
            days_in_month = calendar.monthrange(year, month + 1)[1]
            
            days = []
            for day in range(1, days_in_month + 1):
                date_obj = date(year, month + 1, day)
                days.append({
                    'day': day,
                    'name': date_obj.strftime('%A')
                })
            
            return Response({
                'success': True,
                'days': days,
                'month': month,
                'year': year
            })
            
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=500)


# Add to views.py - Cashier Management Views
class CashierManagementView(APIView):
    pagination_class = StandardPagination
    
    def get(self, request):
        try:
            print("=== CASHIER MANAGEMENT API CALLED ===")
            
            # Get query parameters
            search = request.query_params.get('search', '')
            sort_by = request.query_params.get('sort_by', 'name')
            sort_order = request.query_params.get('sort_order', 'asc')
            page = int(request.query_params.get('page', 1))
            page_size = int(request.query_params.get('page_size', 10))
            
            print(f"Params - search: '{search}', sort_by: '{sort_by}', sort_order: '{sort_order}'")
            
            # Build queryset - get users with cashier role or all users for employee management
            queryset = UserAccount.objects.all()
            
            print(f"Initial queryset count: {queryset.count()}")
            
            # Apply search filter
            if search:
                queryset = queryset.filter(
                    Q(name__icontains=search) |
                    Q(email__icontains=search)
                )
                print(f"After search filter: {queryset.count()}")
            
            # Apply sorting
            valid_sort_fields = ['id', 'name', 'email', 'role']
            
            if sort_by in valid_sort_fields:
                if sort_order == 'desc':
                    sort_field = f'-{sort_by}'
                else:
                    sort_field = sort_by
                queryset = queryset.order_by(sort_field)
                print(f"Applied sorting: {sort_field}")
            else:
                queryset = queryset.order_by('name')
                print("Applied default sorting: name")
            
            # Calculate statistics
            total_employees = queryset.count()
            
            # Use aggregation for better performance
            from django.db.models import Count, Q
            
            stats_agg = queryset.aggregate(
                active_count=Count('id', filter=Q(is_active=True)),
                cashier_count=Count('id', filter=Q(role='cashier')),
                admin_count=Count('id', filter=Q(role='admin'))
            )
            
            employee_stats = {
                'totalEmployees': total_employees,
                'activeStaff': stats_agg['active_count'],
                'cashiers': stats_agg['cashier_count'],
                'admins': stats_agg['admin_count']
            }
            
            print(f"Calculated stats: {employee_stats}")
            
            # Apply pagination
            paginator = self.pagination_class()
            paginator.page_size = page_size
            
            result_page = paginator.paginate_queryset(queryset, request)
            print(f"Paginated results: {len(result_page) if result_page else 0} items")
            
            # Serialize data
            employee_data = []
            if result_page:
                for user in result_page:
                    try:
                        employee_data.append({
                            'id': user.id,
                            'name': user.name or '',
                            'email': user.email or '',
                            'role': user.role or 'user',
                            'is_active': user.is_active
                        })
                    except Exception as item_error:
                        print(f"Error processing user {user.id}: {str(item_error)}")
                        continue
            
            print(f"✅ Successfully processed {len(employee_data)} employee records")
            
            response_data = {
                'success': True,
                'employee_stats': employee_stats,
                'employees': employee_data,
                'pagination': {
                    'count': paginator.page.paginator.count,
                    'total_pages': paginator.page.paginator.num_pages,
                    'current_page': page,
                    'page_size': page_size,
                    'next': paginator.get_next_link(),
                    'previous': paginator.get_previous_link(),
                },
                'filters': {
                    'search': search,
                    'sort_by': sort_by,
                    'sort_order': sort_order
                }
            }
            
            return Response(response_data)
            
        except Exception as e:
            import traceback
            print(f"=== CASHIER MANAGEMENT ERROR ===")
            print(f"Error: {str(e)}")
            print(f"Traceback: {traceback.format_exc()}")
            return Response({
                'success': False,
                'error': f'Failed to fetch employee data: {str(e)}'
            }, status=500)

class CashierExportView(APIView):
    def get(self, request):
        try:
            # Get filters from request
            search = request.query_params.get('search', '')
            sort_by = request.query_params.get('sort_by', 'name')
            sort_order = request.query_params.get('sort_order', 'asc')
            
            # Apply the same filtering logic as CashierManagementView
            queryset = UserAccount.objects.all()
            
            if search:
                queryset = queryset.filter(
                    Q(name__icontains=search) |
                    Q(email__icontains=search)
                )
            
            # Apply sorting
            if sort_order == 'desc':
                sort_field = f'-{sort_by}'
            else:
                sort_field = sort_by
            queryset = queryset.order_by(sort_field)
            
            # Prepare export data
            export_data = []
            for user in queryset:
                export_data.append({
                    'ID': user.id,
                    'Name': user.name,
                    'Email': user.email,
                    'Role': user.role or 'user',
                    'Status': 'Active' if user.is_active else 'Inactive',
                    'Is Active': user.is_active
                })
            
            return Response({
                'success': True,
                'export_data': export_data,
                'total_records': len(export_data),
                'exported_at': timezone.now().isoformat()
            })
            
        except Exception as e:
            return Response({
                'success': False,
                'error': f'Failed to export employee data: {str(e)}'
            }, status=500)


class ExpensesReportView(APIView):
    def get(self, request):
        try:
            # Get query parameters
            period = request.query_params.get('period', 'overview')
            search = request.query_params.get('search', '').strip()
            selected_day = request.query_params.get('selectedDay', '')
            selected_month = request.query_params.get('selectedMonth', '')
            selected_month_day = request.query_params.get('selectedMonthDay', '')
            page = int(request.query_params.get('page', 1))
            page_size = int(request.query_params.get('page_size', 20))
            
            # Validate page parameters
            if page < 1:
                page = 1
            if page_size < 1 or page_size > 100:
                page_size = 20
            
            today = timezone.now().date()
            start_of_week = today - timedelta(days=today.weekday())
            start_of_month = today.replace(day=1)
            
            # Base queryset
            queryset = Expense.objects.all().order_by('-date', '-id')
            
            # Apply search filter
            if search:
                queryset = queryset.filter(
                    Q(name__icontains=search) |
                    Q(description__icontains=search)
                )
            
            # Calculate overview statistics
            def calculate_period_stats(date_filter):
                period_queryset = queryset.filter(date_filter)
                agg = period_queryset.aggregate(
                    total=Sum('amount'),
                    count=Count('id')
                )
                return {
                    'total': float(agg['total'] or 0),
                    'count': agg['count'] or 0
                }
            
            overview_stats = {
                'today': calculate_period_stats(Q(date=today)),
                'weekly': calculate_period_stats(Q(date__range=[start_of_week, today])),
                'monthly': calculate_period_stats(Q(date__range=[start_of_month, today])),
                'all_time': calculate_period_stats(Q())
            }
            
            # Initialize response data
            response_data = {
                'success': True,
                'expenses': [],
                'statistics': {
                    'overview': overview_stats,
                    'current_period': {}
                },
                'pagination': {},
                'filters': {
                    'period': period,
                    'search': search,
                    'selectedDay': selected_day,
                    'selectedMonth': selected_month,
                    'selectedMonthDay': selected_month_day
                }
            }
            
            # Handle detailed periods
            if period in ['today', 'weekly', 'monthly']:
                if period == 'today':
                    period_queryset = queryset.filter(date=today)
                elif period == 'weekly':
                    period_queryset = queryset.filter(date__range=[start_of_week, today])
                    if selected_day:
                        try:
                            day_int = int(selected_day)
                            # Convert to Django week_day (1=Sunday, 2=Monday, etc.)
                            period_queryset = period_queryset.filter(date__week_day=day_int + 1)
                        except (ValueError, TypeError):
                            pass
                elif period == 'monthly':
                    period_queryset = queryset.filter(date__range=[start_of_month, today])
                    if selected_month:
                        try:
                            month_int = int(selected_month)
                            period_queryset = period_queryset.filter(date__month=month_int + 1)
                        except (ValueError, TypeError):
                            pass
                    if selected_month_day:
                        try:
                            day_int = int(selected_month_day)
                            period_queryset = period_queryset.filter(date__day=day_int)
                        except (ValueError, TypeError):
                            pass
                
                # Calculate current period statistics
                current_period_agg = period_queryset.aggregate(
                    total_expenses=Count('id'),
                    total_amount=Sum('amount'),
                    verified_count=Count('id', filter=Q(is_verified=True)),
                    pending_count=Count('id', filter=Q(is_verified=False))
                )
                
                response_data['statistics']['current_period'] = {
                    'total_expenses': current_period_agg['total_expenses'] or 0,
                    'total_amount': float(current_period_agg['total_amount'] or 0),
                    'verified_count': current_period_agg['verified_count'] or 0,
                    'pending_count': current_period_agg['pending_count'] or 0
                }
                
                # Apply pagination
                total_count = period_queryset.count()
                total_pages = (total_count + page_size - 1) // page_size
                
                if page > total_pages and total_pages > 0:
                    page = total_pages
                
                start_index = (page - 1) * page_size
                end_index = start_index + page_size
                
                # Get paginated data
                paginated_queryset = period_queryset[start_index:end_index]
                
                # Prepare expenses data
                expenses_data = []
                for expense in paginated_queryset:
                    expenses_data.append({
                        'id': expense.id,
                        'date': expense.date.isoformat() if expense.date else '',
                        'name': expense.name,
                        'amount': float(expense.amount or 0),
                        'description': expense.description or '',
                        'is_verified': expense.is_verified
                    })
                
                response_data['expenses'] = expenses_data
                response_data['pagination'] = {
                    'current_page': page,
                    'page_size': page_size,
                    'total_count': total_count,
                    'total_pages': total_pages,
                    'has_next': page < total_pages,
                    'has_previous': page > 1,
                    'next_page': page + 1 if page < total_pages else None,
                    'previous_page': page - 1 if page > 1 else None,
                    'count': total_count
                }
            
            return Response(response_data, status=200)
            
        except Exception as e:
            import traceback
            print(f"Expenses report error: {str(e)}")
            print(f"Traceback: {traceback.format_exc()}")
            return Response({
                'success': False,
                'error': f'Failed to generate expenses report: {str(e)}'
            }, status=500)


class ExpensesReportExportView(APIView):
    def get(self, request):
        try:
            # Get query parameters
            period = request.query_params.get('period', 'overview')
            search = request.query_params.get('search', '').strip()
            selected_day = request.query_params.get('selectedDay', '')
            selected_month = request.query_params.get('selectedMonth', '')
            selected_month_day = request.query_params.get('selectedMonthDay', '')
            
            today = timezone.now().date()
            start_of_week = today - timedelta(days=today.weekday())
            start_of_month = today.replace(day=1)
            
            # Base queryset
            queryset = Expense.objects.all().order_by('-date', '-id')
            
            # Apply filters (same logic as ExpensesReportView)
            if search:
                queryset = queryset.filter(
                    Q(name__icontains=search) |
                    Q(description__icontains=search)
                )
            
            if period == 'today':
                queryset = queryset.filter(date=today)
            elif period == 'weekly':
                queryset = queryset.filter(date__range=[start_of_week, today])
                if selected_day:
                    try:
                        day_int = int(selected_day)
                        queryset = queryset.filter(date__week_day=day_int + 1)
                    except (ValueError, TypeError):
                        pass
            elif period == 'monthly':
                queryset = queryset.filter(date__range=[start_of_month, today])
                if selected_month:
                    try:
                        month_int = int(selected_month)
                        queryset = queryset.filter(date__month=month_int + 1)
                    except (ValueError, TypeError):
                        pass
                if selected_month_day:
                    try:
                        day_int = int(selected_month_day)
                        queryset = queryset.filter(date__day=day_int)
                    except (ValueError, TypeError):
                        pass
            
            # Prepare export data
            export_data = []
            for expense in queryset:
                export_data.append({
                    'ID': expense.id,
                    'Date': expense.date.strftime('%Y-%m-%d') if expense.date else '',
                    'Name': expense.name,
                    'Amount': float(expense.amount or 0),
                    'Description': expense.description or '',
                    'Status': 'Verified' if expense.is_verified else 'Pending',
                    'Created At': expense.created_at.strftime('%Y-%m-%d %H:%M:%S') if expense.created_at else ''
                })
            
            return Response({
                'success': True,
                'export_data': export_data,
                'total_records': len(export_data),
                'filters_applied': {
                    'period': period,
                    'search': search,
                    'selectedDay': selected_day,
                    'selectedMonth': selected_month,
                    'selectedMonthDay': selected_month_day
                }
            }, status=200)
            
        except Exception as e:
            import traceback
            print(f"Expenses export error: {str(e)}")
            print(f"Traceback: {traceback.format_exc()}")
            return Response({
                'success': False,
                'error': f'Failed to export expenses: {str(e)}'
            }, status=500)
    def get(self, request):
        try:
            # Get the same filters as the report view
            period = request.query_params.get('period', 'overview')
            search = request.query_params.get('search', '')
            selected_day = request.query_params.get('selected_day', '')
            selected_month = request.query_params.get('selected_month', '')
            selected_month_day = request.query_params.get('selected_month_day', '')
            
            # Apply the same filtering logic
            queryset = Expense.objects.all().order_by('-date')
            
            today = timezone.now().date()
            
            if search:
                queryset = queryset.filter(
                    Q(name__icontains=search) |
                    Q(description__icontains=search)
                )
            
            if period == 'today':
                queryset = queryset.filter(date=today)
            elif period == 'weekly':
                start_of_week = today - timedelta(days=today.weekday())
                queryset = queryset.filter(date__range=[start_of_week, today])
                
                if selected_day:
                    queryset = queryset.filter(date__week_day=(int(selected_day) + 2) % 7 + 1)
                    
            elif period == 'monthly':
                start_of_month = today.replace(day=1)
                queryset = queryset.filter(date__range=[start_of_month, today])
                
                if selected_month:
                    queryset = queryset.filter(date__month=int(selected_month) + 1)
                
                if selected_month_day:
                    queryset = queryset.filter(date__day=int(selected_month_day))
            
            # Prepare export data
            export_data = []
            for expense in queryset:
                export_data.append({
                    'ID': expense.id,
                    'Date': expense.date.isoformat(),
                    'Submitted By': expense.name,
                    'Amount': float(expense.amount),
                    'Description': expense.description,
                    'Status': 'Verified' if expense.is_verified else 'Pending',
                    'Verified By': expense.verified_by or 'N/A',
                    'Created At': expense.created_at.isoformat() if expense.created_at else 'N/A'
                })
            
            return Response({
                'success': True,
                'export_data': export_data,
                'total_records': len(export_data),
                'exported_at': timezone.now().isoformat(),
                'filters_applied': {
                    'period': period,
                    'search': search,
                    'selected_day': selected_day,
                    'selected_month': selected_month,
                    'selected_month_day': selected_month_day
                }
            })
            
        except Exception as e:
            return Response({
                'success': False,
                'error': f'Failed to export expenses: {str(e)}'
            }, status=500)


    """Verify exchange was recorded in all systems"""
    def get(self, request, exchange_id):
        try:
            exchange = Exchange.objects.get(id=exchange_id)
            
            # Check if electronics item exists with the new item name
            electronics_item = Electronics.objects.filter(
                name=exchange.new_item_name,
                main_category=exchange.new_item_main_category,
                sub_category=exchange.new_item_sub_category
            ).first()
            
            # Check if buying record exists
            buying_record = Buying.objects.filter(
                name=exchange.new_item_name,
                main_category=exchange.new_item_main_category,
                sub_category=exchange.new_item_sub_category
            ).first()
            
            verification_data = {
                'exchange': {
                    'id': exchange.id,
                    'original_item': exchange.item_name,
                    'new_item': exchange.new_item_name,
                    'quantity': exchange.quantity,
                    'date': exchange.date,
                    'profit': float(exchange.profit) if exchange.profit else 0
                },
                'electronics_inventory': {
                    'exists': electronics_item is not None,
                    'item': {
                        'id': electronics_item.id if electronics_item else None,
                        'name': electronics_item.name if electronics_item else None,
                        'quantity': electronics_item.quantity if electronics_item else None,
                        'buying_price': float(electronics_item.buying_price) if electronics_item else None
                    } if electronics_item else None
                },
                'buying_record': {
                    'exists': buying_record is not None,
                    'record': {
                        'id': buying_record.id if buying_record else None,
                        'name': buying_record.name if buying_record else None,
                        'quantity': buying_record.quantity if buying_record else None,
                        'total_cost': float(buying_record.total_cost) if buying_record else None
                    } if buying_record else None
                },
                'all_systems_ok': electronics_item is not None and buying_record is not None
            }
            
            return Response({
                'success': True,
                'verification': verification_data
            }, status=200)
            
        except Exchange.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Exchange record not found'
            }, status=404)
        except Exception as e:
            return Response({
                'success': False,
                'error': f'Verification failed: {str(e)}'
            }, status=500)

# Enhanced ProcessExchangeView with better debugging
class ProcessExchangeView(APIView):
    def post(self, request):
        try:
            print("=== PROCESS EXCHANGE API CALLED ===")
            print(f"Request data: {request.data}")
            print(f"Request content type: {request.content_type}")
            
            # Check if data is coming through properly
            if not request.data:
                return Response({
                    'error': 'No data received in request',
                    'received_data': str(request.data)
                }, status=400)
            
            with transaction.atomic():
                data = request.data
                
                # Extract data from request with defaults
                original_item_id = data.get('original_item_id')
                if not original_item_id:
                    return Response({'error': 'original_item_id is required'}, status=400)
                
                original_quantity = int(data.get('quantity', 1))
                original_buying_price = float(data.get('original_buying_price', 0))
                
                # New item data
                new_item_name = data.get('new_item_name')
                new_item_main_category_id = data.get('new_item_main_category')
                new_item_sub_category_id = data.get('new_item_sub_category')
                new_item_size = data.get('new_item_size', '')
                
                # Exchange details
                quantity = int(data.get('quantity', 1))
                estimated_exchange_price = float(data.get('estimated_exchange_price', 0))
                additional_payment = float(data.get('additional_payment', 0))
                commission_amount = float(data.get('commission_amount', 0))
                payment_method = data.get('payment_method')
                seller_name = data.get('seller_name', 'Unknown')
                exchange_date = data.get('date')
                
                print(f"Parsed data:")
                print(f"  Original item ID: {original_item_id}")
                print(f"  New item name: {new_item_name}")
                print(f"  Quantity: {quantity}")
                
                # Validate required fields
                required_fields = ['new_item_name', 'new_item_main_category', 'new_item_sub_category']
                missing_fields = [field for field in required_fields if not data.get(field)]
                
                if missing_fields:
                    return Response({
                        'error': f'Missing required fields: {", ".join(missing_fields)}'
                    }, status=400)
                
                # Get original item
                try:
                    original_item = Electronics.objects.get(id=original_item_id)
                    print(f"Found original item: {original_item.name} (ID: {original_item.id})")
                except Electronics.DoesNotExist:
                    return Response({'error': 'Original item not found'}, status=404)
                
                # Validate quantity
                if quantity > original_item.quantity:
                    return Response({
                        'error': f'Cannot exchange more than available quantity ({original_item.quantity})'
                    }, status=400)
                
                # ===== CREATE NEW ELECTRONICS ITEM =====
                print("Creating new electronics item...")
                new_electronics_data = {
                    'name': new_item_name,
                    'size': new_item_size,
                    'quantity': quantity,
                    'buying_price': estimated_exchange_price,
                    'main_category': new_item_main_category_id,
                    'sub_category': new_item_sub_category_id,
                    'added_by': seller_name,
                }
                
                print(f"Electronics data: {new_electronics_data}")
                
                new_electronics_serializer = ElectronicsSerializer(data=new_electronics_data)
                if new_electronics_serializer.is_valid():
                    new_electronics_item = new_electronics_serializer.save()
                    print(f"✅ New electronics item created: {new_electronics_item.id} - {new_electronics_item.name}")
                else:
                    print(f"❌ Electronics creation error: {new_electronics_serializer.errors}")
                    return Response({
                        'error': 'Failed to create new electronics item',
                        'details': new_electronics_serializer.errors
                    }, status=400)
                
                # ===== CREATE BUYING RECORD FOR THE NEW ITEM =====
                print("Creating buying record...")
                buying_data = {
                    'name': new_item_name,
                    'size': new_item_size,
                    'quantity': quantity,
                    'buying_price': estimated_exchange_price,
                    'main_category': new_item_main_category_id,
                    'sub_category': new_item_sub_category_id,
                    'supplier': f"Exchange from {seller_name}",
                    'purchase_order': f"EXCH-{exchange_date}-{original_item_id}",
                    'added_by': seller_name,
                    'date_added': exchange_date or timezone.now().date().isoformat(),
                }
                
                print(f"Buying data: {buying_data}")
                
                buying_serializer = BuyingSerializer(data=buying_data)
                if buying_serializer.is_valid():
                    buying_record = buying_serializer.save()
                    print(f"✅ Buying record created: {buying_record.id}")
                else:
                    print(f"❌ Buying record creation error: {buying_serializer.errors}")
                    return Response({
                        'error': 'Failed to create buying record',
                        'details': buying_serializer.errors
                    }, status=400)
                
                # ===== UPDATE ORIGINAL ITEM QUANTITY =====
                print(f"Updating original item quantity from {original_item.quantity} to {original_item.quantity - quantity}")
                original_item.quantity -= quantity
                original_item.save()
                print(f"✅ Original item quantity updated: {original_item.quantity}")
                
                # ===== CALCULATE PROFIT =====
                total_exchange_value = estimated_exchange_price + additional_payment
                total_original_cost = original_buying_price * quantity
                profit = total_exchange_value - total_original_cost - commission_amount
                
                print(f"Profit calculation:")
                print(f"  Total exchange value: {total_exchange_value}")
                print(f"  Total original cost: {total_original_cost}")
                print(f"  Commission: {commission_amount}")
                print(f"  Profit: {profit}")
                
                # ===== CREATE EXCHANGE RECORD =====
                print("Creating exchange record...")
                exchange_data = {
                    'item_name': original_item.name,
                    'main_category': original_item.main_category.id,
                    'sub_category': original_item.sub_category.id,
                    'size': original_item.size,
                    'new_item_name': new_item_name,
                    'new_item_main_category': new_item_main_category_id,
                    'new_item_sub_category': new_item_sub_category_id,
                    'new_item_size': new_item_size,
                    'quantity': quantity,
                    'seller_name': seller_name,
                    'date': exchange_date or timezone.now().date().isoformat(),
                    'payment_method': payment_method,
                    'estimated_exchange_price': estimated_exchange_price,
                    'additional_payment': additional_payment,
                    'commission_amount': commission_amount,
                    'profit': profit,
                }
                
                print(f"Exchange data: {exchange_data}")
                
                exchange_serializer = ExchangeSerializer(data=exchange_data)
                if exchange_serializer.is_valid():
                    exchange_record = exchange_serializer.save()
                    print(f"✅ Exchange record created: {exchange_record.id}")
                else:
                    print(f"❌ Exchange creation error: {exchange_serializer.errors}")
                    transaction.set_rollback(True)
                    return Response({
                        'error': 'Failed to create exchange record',
                        'details': exchange_serializer.errors
                    }, status=400)
                
                # Prepare success response
                response_data = {
                    'success': True,
                    'message': 'Exchange processed successfully!',
                    'data': {
                        'exchange_id': exchange_record.id,
                        'new_electronics_id': new_electronics_item.id,
                        'buying_record_id': buying_record.id,
                        'original_item_remaining': original_item.quantity,
                        'profit': profit,
                    },
                    'created_records': {
                        'electronics': new_electronics_data,
                        'buying': buying_data,
                        'exchange': exchange_data
                    }
                }
                
                print("🎉 EXCHANGE PROCESS COMPLETED SUCCESSFULLY!")
                return Response(response_data, status=201)
                
        except Exception as e:
            import traceback
            error_traceback = traceback.format_exc()
            print(f"=== EXCHANGE PROCESSING ERROR ===")
            print(f"Error: {str(e)}")
            print(f"Traceback: {error_traceback}")
            return Response({
                'success': False,
                'error': f'Exchange processing failed: {str(e)}',
                'debug_info': str(e)
            }, status=500)
    
