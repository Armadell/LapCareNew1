from django.urls import path
from . import views
urlpatterns = [
    path('',views.register,name='register'),
    path('login/',views.login,name='login'),
    path('loginotp/',views.loginotp,name='loginotp'),
    path("otpcheck/", views.otpcheck, name="otpcheck"),
    path("otpcheck1/", views.otpcheck1, name="otpcheck1"),
    path('logout/',views.logout,name='logout'),
    path('dashboard/',views.dashboard,name='dashboard'),
    path('my_orders/',views.my_orders,name='my-orders'),
    path('order_history/',views.order_history,name='order-history'),
    path('edit_profile/',views.edit_profile,name='edit-profile'),
    path('change_password/',views.change_password,name='change-password'),
    path("order_detail/<order_id>/", views.order_detail, name="order-detail"),
    
]