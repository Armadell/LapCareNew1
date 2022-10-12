from django.urls import path
from . import views
from .views import ChartData, Generate_sales_pdf

urlpatterns = [
    path("", views.AdminLogin, name="AdminLogin"),
    path("AdminDashboard/", views.AdminDashboard, name="AdminDashboard"),
    path("Adminprofile/", views.AdminProfile, name="AdminProfile"),
    path("AdminLogout/", views.AdminLogout, name="AdminLogout"),
    path("brand/", views.brand, name="brand"),
    path("products/", views.products, name="products"),
    path("category/", views.category, name="category"),
    path("addcategory/", views.Addcategory, name="addcategory"),
    path("addbrand/", views.Addbrand, name="addbrand"),
    path("addproduct/", views.Addproducts, name="addproduct"),
    path("updatebrand/<int:pk>", views.Updatebrand, name="updatebrand"),
    path("deletebrand/<int:pk>", views.Deletebrand, name="deletebrand"),
    path("Updatecategory/<int:pk>/", views.Updatecategory, name="updatecategory"),
    path("Deletecategory/<int:pk>/", views.Deletecategory, name="deletecategory"),
    path("Updateproduct/<int:pk>/", views.Updateproducts, name="Updateproduct"),
    path("Deleteproduct/<int:pk>/", views.Deleteproducts, name="deleteproduct"),
    path("usermanagement/", views.usermanagement, name="usermanagement"),
    path("userblock/<int:pk>/", views.userblock, name="block"),
    path("userunblock/<int:pk>/", views.userunblock, name="unblock"),
    path("Order_management/", views.order_management, name="order-management"),
    path(
        "admin_cancel_order/<int:order_num>/",
        views.admin_cancel_order,
        name="admin_cancel_order",
    ),
    path("status/<int:id>/", views.status, name="status"),
    path("viewcoupon/", views.viewcoupon, name="viewcoupon"),
    path("deletecoupon/<int:id>/", views.deletecoupon, name="delete-coupon"),
    path("addadmincoupon/", views.addcoupon, name="addcoupon"),
    path("api/chart/data/", ChartData.as_view(), name="chart-data"),
    path("sales_pdf/", Generate_sales_pdf.as_view(), name="sales-pdf"),
    path("sales_csv/", views.Generate_sales_csv, name="sales-csv"),
]
