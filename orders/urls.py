from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('create/', views.OrderCreateView.as_view(), name='order_create'),
    path('', views.OrderListView.as_view(), name='order_list'),
    path('<int:order_id>/', views.OrderDetailView.as_view(), name='order_detail'),
]


