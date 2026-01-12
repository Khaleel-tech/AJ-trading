# from django.urls import path
# from . import views

# urlpatterns = [
#     path("create-bill/", views.create_bill, name="create_bill"),
#     path("bills/", views.bill_list, name="bill_list"), 
# ]

from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path("login/", auth_views.LoginView.as_view(
        template_name="billing/login.html"
    ), name="login"),

    path("logout/", auth_views.LogoutView.as_view(), name="logout"),

    path("dashboard/", views.dashboard, name="dashboard"),

    path("create-bill/", views.create_bill, name="create_bill"),
    path("bills/", views.bill_list, name="bill_list"),
    path("items/add/", views.add_item, name="add_item"),
    # path("items/", views.item_list, name="item_list"),
    path('items/', views.items_list, name='items_list'),
    path('remove-item/<int:id>/', views.remove_item, name='remove_item'),
    path('removed-items/', views.removed_items_list, name='removed_items_list'),
    path('restore-item/<int:id>/', views.restore_item, name='restore_item'),
    path('update-item/<int:id>/', views.update_item, name='update_item'),
    path('bills/', views.bill_list, name='bill_list'),
    path('bills/remove/<int:bill_id>/', views.remove_bill, name='remove_bill'),
    path('bills/removed/', views.removed_bills, name='removed_bills'),
    path('bills/restore/<int:bill_id>/', views.restore_bill, name='restore_bill'),
    path('bills/delete/<int:bill_id>/', views.permanent_delete_bill, name='permanent_delete_bill'),
    path('analytics/day/', views.bills_per_day, name='bills_per_day'),
    path('analytics/month/', views.bills_per_month, name='bills_per_month'),
    path('analytics/year/', views.bills_per_year, name='bills_per_year'),
    path('analytics/', views.analytics_dashboard, name='analytics_dashboard'),
    path('analytics/top-items/quantity/', views.top_items_by_quantity, name='top_items_by_quantity'),
    path('analytics/top-items/weight/', views.top_items_by_weight, name='top_items_by_weight'),
    path('analytics/top-items/revenue/', views.top_items_by_revenue, name='top_items_by_revenue'),
    path('analytics/sales/', views.sales_analytics, name='sales_analytics'),
    path('analytics/fruits/', views.fruits_analytics, name='fruits_analytics'),
    path('analytics/sales/monthly/', views.bills_per_day_in_month, name='bills_per_day_in_month'),
    path('analytics/sales/yearly/', views.bills_per_month_in_year, name='bills_per_month_in_year'),
    path('analytics/revenue/fruits/', views.revenue_by_fruit_range, name='revenue_by_fruit_range'),
    path('analytics/revenue/', views.revenue_analytics, name='revenue_analytics'),



]


