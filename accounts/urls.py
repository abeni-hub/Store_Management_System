# your_app/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    BulkOperationsView,
    BuyingReportsView,
    BuyingSummaryView,
    BuyingViewSet,
    CashierExportView,
    CashierManagementView,
    CategoryManagementView,
    DebitExportView,
    DebitReportView,
    DebitSaleDetailView,
    DebitStatusUpdateView,
    ExchangeDetailView,
    ExchangeExportView,
    ExchangeReportView,
    ExchangeViewSet,
    ExpenseExportView,
    ExpenseListView,
    ExpenseStatisticsView,
    ExpensesReportView,           # KEEP ONLY THIS ONE
    ExpensesReportExportView,     # KEEP ONLY THIS ONE
    ExportDataView,
    InventoryAlertsView,
    InventoryCategoriesView,
    InventoryExportView,
    InventoryItemsView,
    InventorySummaryView,
    LowStockExportView,
    LowStockItemsView,
    OutOfStockItemsView,
    ProcessExchangeView,
    QuickSaleViewSet,
    RevenueAnalyticsDaysView,
    RevenueAnalyticsView,
    RevenueExportView,
    RevenueReportView,
    RevenueVerifyView, 
    RevenueViewSet,
    SaleDetailView,
    SalesAnalyticsView,
    SalesExportView,
    SalesPerformanceInsightsView,
    SalesReportsView,
    SalesStatisticsView, 
    SalesSummaryView,
    TodayTransactionsView,
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
    UserDetail,
    DashboardStatsView,
    DashboardRecentActivityView
)
from .serializers import CustomTokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

router = DefaultRouter()
router.register(r'users', UserAccountViewSet)
router.register(r'users/create', UserCreateViewSet, basename='user-create')
router.register(r'roles', RoleViewSet)
router.register(r'cashiers', CashierCreateViewSet, basename='cashier-create')
router.register(r'categories', CategoryViewSet)
router.register(r'subcategories', SubCategoryViewSet)
router.register(r'electronics', ElectronicsViewSet)
router.register(r'sales', SaleViewSet)
router.register(r'exchange', ExchangeViewSet)
router.register(r'quick-sales', QuickSaleViewSet, basename='quicksale')
router.register(r'buying', BuyingViewSet, basename='buying')
router.register(r'revenue', RevenueViewSet)
router.register(r'sales-summary', SalesSummaryViewSet)
router.register(r'expenses', ExpenseViewSet, basename='expense')

urlpatterns = [
    path('', include(router.urls)),
    
    # Dashboard URLs
    path('dashboard/stats/', DashboardStatsView.as_view(), name='dashboard-stats'),
    path('dashboard/recent-activities/', DashboardRecentActivityView.as_view(), name='dashboard-recent-activities'),
    path('today-transactions/', TodayTransactionsView.as_view(), name='today-transactions'),
    
    # Sales URLs
    path('sales-summary/<str:period>/', SalesSummaryView.as_view(), name='sales-summary'),
    path('sales/<int:pk>/detail/', SaleDetailView.as_view(), name='sale-detail'),
    path('sales-statistics/', SalesStatisticsView.as_view(), name='sales-statistics'),
    path('export/sales/', SalesExportView.as_view(), name='sales-export'),
    path('sales-reports/', SalesReportsView.as_view(), name='sales-reports'),
    path('sales-insights/', SalesPerformanceInsightsView.as_view(), name='sales-insights'),
    path('sales-analytics/', SalesAnalyticsView.as_view(), name='sales-analytics'),
    
    # Inventory URLs
    path('inventory-summary/', InventorySummaryView.as_view(), name='inventory-summary'),
    path('inventory-items/', InventoryItemsView.as_view(), name='inventory-items'),
    path('inventory-categories/', InventoryCategoriesView.as_view(), name='inventory-categories'),
    path('inventory-export/', InventoryExportView.as_view(), name='inventory-export'),
    path('inventory-alerts/', InventoryAlertsView.as_view(), name='inventory-alerts'),
    path('low-stock/', LowStockItemsView.as_view(), name='low-stock'),
    path('low-stock/export/', LowStockExportView.as_view(), name='low-stock-export'),
    path('out-of-stock/', OutOfStockItemsView.as_view(), name='out-of-stock'),
    
    # Buying URLs
    path('buying-summary/', BuyingSummaryView.as_view(), name='buying-summary'),
    path('buying-reports/', BuyingReportsView.as_view(), name='buying-reports'),
    
    # Debit URLs
    path('debit-report/', DebitReportView.as_view(), name='debit-report'),
    path('debit-sales/<int:pk>/', DebitSaleDetailView.as_view(), name='debit-sale-detail'),
    path('debit-sales/<int:pk>/status/', DebitStatusUpdateView.as_view(), name='debit-status-update'),
    path('debit-export/', DebitExportView.as_view(), name='debit-export'),
    
    # Exchange URLs
    path('exchange-report/', ExchangeReportView.as_view(), name='exchange-report'),
    path('exchange-detail/<int:pk>/', ExchangeDetailView.as_view(), name='exchange-detail'),
    path('exchange-export/', ExchangeExportView.as_view(), name='exchange-export'),
    # Add this to your urls.py in the urlpatterns list
path('process-exchange/', ProcessExchangeView.as_view(), name='process-exchange'),
    # Revenue URLs
    path('revenue-report/', RevenueReportView.as_view(), name='revenue-report'),
    path('revenue/<int:pk>/verify/', RevenueVerifyView.as_view(), name='revenue-verify'),
    path('revenue-export/', RevenueExportView.as_view(), name='revenue-export'),
    path('revenue-analytics/', RevenueAnalyticsView.as_view(), name='revenue-analytics'),
    path('revenue-analytics/days/', RevenueAnalyticsDaysView.as_view(), name='revenue-analytics-days'),
    
    # Cashier URLs
    path('cashier-management/', CashierManagementView.as_view(), name='cashier-management'),
    path('cashier-export/', CashierExportView.as_view(), name='cashier-export'),
    
    # Expense URLs - CLEANED UP
    path('expenses-report/', ExpensesReportView.as_view(), name='expenses-report'),
    path('expenses-report/export/', ExpensesReportExportView.as_view(), name='expenses-report-export'),
    path('expense-statistics/', ExpenseStatisticsView.as_view(), name='expense-statistics'),
    path('expense-export/', ExpenseExportView.as_view(), name='expense-export'),
    path('expense-list/', ExpenseListView.as_view(), name='expense-list'),
    
    # Category URLs
    path('category-management/', CategoryManagementView.as_view(), name='category-management'),
    
    # Bulk Operations & Export
    path('bulk-operations/<str:model_type>/', BulkOperationsView.as_view(), name='bulk-operations'),
    path('export-data/<str:model_type>/', ExportDataView.as_view(), name='export-data'),
  
  


    # Authentication
    path('auth/jwt/create/', TokenObtainPairView.as_view(serializer_class=CustomTokenObtainPairSerializer), name='token_obtain_pair'),
    path('user-detail/', UserDetail, name="UserDetail")
]
