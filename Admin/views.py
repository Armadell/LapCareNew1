from itertools import product
from re import search
from django.db.models.functions import TruncMonth
from django.db.models import Count
from django.core import serializers
from django.http import HttpResponseRedirect
from multiprocessing import context
from django.contrib.auth import authenticate
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from brand.models import brand as brand2
from product.models import Products
from product.forms import ProductsForm
from django.contrib.auth import login, logout
from category.models import category as category2
from category.forms import categoryForm
from brand.forms import brandForm
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.views.decorators.cache import cache_control, never_cache
from accounts.models import Account
from order.models import Order, OrderProduct, Payment
from cart.forms import CouponForm
from cart.models import Coupon
from rest_framework.views import APIView
from rest_framework.response import Response

# importing the function for converting html to pdf
from .process import html_to_pdf
from django.views.generic import View
from django.template.loader import render_to_string

import datetime

# from datetime import datetime,timedeta
from django.utils import timezone

# imports for creating pdf
from django.http import FileResponse, HttpResponse
import io
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter

User = get_user_model()
import datetime
from django.http import JsonResponse


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def AdminLogin(request):
    if request.session.has_key("superadmin"):
        return redirect("AdminDashboard")

    # if request.user.is_authenticated:
    #      return redirect('AdminDashboard')
    if request.method == "POST":

        email = request.POST.get("Email")
        password = request.POST.get("password")
        user = authenticate(email=email, password=password, is_superadmin=True)
        if user is not None and user.is_superadmin == True:

            request.session["superadmin"] = "username"
            login(request, user)  # logging in the user

            return HttpResponseRedirect("AdminDashboard")

        else:
            messages.error(request, "invalid credentials")

            return redirect("AdminLogin")
    else:
        return render(request, "MyAdmin/login.html")


@login_required(login_url="AdminLogin")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def AdminLogout(request):
    if request.session.has_key("username"):
        del request.session["username"]
        request.session.modified = True
    logout(request)
    return redirect("AdminLogin")


@login_required(login_url="AdminLogin")
def AdminDashboard(request, *args, **kwargs):
    #  if request.session.has_key("username"):

    order_products = OrderProduct.objects.filter(
        Q(status__contains="Delivered")
        | Q(order__payment__payment_method__contains="Paypal")
    ).order_by("-created_at")

    total = 0
    for order in order_products:
        total += order.order.order_total
    total = round(total, 2)

    order_count = Order.objects.all().count()
    product_count = Products.objects.all().count()

    print("orderproduct", order_products)
    print("orderproduct", order_products)
    total_sales = 0
    for order_product in order_products:
        total_sales += order_product.product.price
    total_sales = round(total_sales, 2)
    round(total_sales, 2)
    print(total_sales)
    context = {
        "order_products": order_products,
        "total_sales": total,
        "order_count": order_count,
        "product_count": product_count,
    }
    return render(request, "MyAdmin/home.html", context)


# it is a http response with the datatype of json
class ChartData(APIView):

    authentication_classes = []
    permission_classes = []

    def get(self, request, format=None):

        sales_labels = []
        sales_values = []
        products2 = Products.objects.all()[:8]
        print(products)
        for product2 in products2:
            sales_labels.append(product2.product_name)
            sales_values.append(product2.stock)

        print(sales_labels, sales_values)

        new_count = OrderProduct.objects.filter(status="New").count()
        pending_count = OrderProduct.objects.filter(status="Pending").count()
        placed_count = OrderProduct.objects.filter(status="Placed").count()
        shipped_count = OrderProduct.objects.filter(status="Shipped").count()
        accepted_count = OrderProduct.objects.filter(status="Accepted").count()
        delivered_count = OrderProduct.objects.filter(status="Delivered").count()
        cancelled_count = OrderProduct.objects.filter(status="Cancelled").count()
        qs_count = User.objects.all().count()

        labels = [
            "New",
            "Placed",
            "Shipped",
            "Accepted",
            "Delivered",
            "Cancelled",
            "Pending",
        ]
        default_items = [
            new_count,
            placed_count,
            shipped_count,
            accepted_count,
            delivered_count,
            cancelled_count,
            pending_count,
        ]
        data = {
            "labels": labels,
            "default": default_items,
            "sales_labels": sales_labels,
            "sales_values": sales_values,
        }
        return Response(data)


# display admin informations
@login_required(login_url="AdminLogin")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def AdminProfile(request):
    post = User.objects.all()

    return render(request, "MyAdmin/profile.html", {"context": post})


# display brand informations
@login_required(login_url="AdminLogin")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def brand(request):
    search_post = request.GET.get("search")
    if search_post:
        post = brand2.objects.filter((Q(brand_name__icontains=search_post)))
        context = {
            "brands": post,
        }
    else:

        post = brand2.objects.all()
        context = {
            "brands": post,
        }
    return render(request, "MyAdmin/brand.html", context)


# display product informations
@login_required(login_url="AdminLogin")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def products(request):
    search_product = request.GET.get("search")
    if search_product:
        post = Products.objects.filter(
            (
                Q(product_name__icontains=search_product)
                and Q(price__icontains=search_product)
            )
        )

        context = {"product": post}
    else:
        post = Products.objects.all().filter(available=True)
        context = {"product": post}
    return render(request, "MyAdmin/product.html", context)


# display category information
@login_required(login_url="AdminLogin")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def category(request):
    post = category2.objects.all()
    # context={
    #     'categories':post
    # }
    return render(request, "MyAdmin/category.html", {"categories": post})


# create a new category,brand,product
@login_required(login_url="AdminLogin")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def Addcategory(request):
    form = categoryForm()
    if request.method == "POST":
        form = categoryForm(request.POST)

        if form.is_valid():

            form.save()
            messages.error(request, "the category is already present!")
            return redirect("category")
        else:

            messages.error(request, "the category is already present!")
            return redirect("addcategory")

    context = {"form": form}
    return render(request, "MyAdmin/Addcategory.html", context)


@login_required(login_url="AdminLogin")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def Addbrand(request):
    form = brandForm()
    if request.method == "POST":
        form = brandForm(request.POST, request.FILES)

        if form.is_valid():
            form.save()

            return redirect("brand")

        else:
            messages.error(request, "the brand is already present!")
            return redirect("addbrand")

    context = {"form": form}
    return render(request, "MyAdmin/Addbrand.html", context)


@login_required(login_url="AdminLogin")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def Addproducts(request):
    form = ProductsForm()
    if request.method == "POST":
        form = ProductsForm(request.POST, request.FILES)

        if form.is_valid():
            form.save()

            return redirect("products")

        else:
            messages.error(request, "the product is already present!")
            return redirect("addproduct")

    context = {"form": form}
    return render(request, "MyAdmin/Addproduct.html", context)


@login_required(login_url="AdminLogin")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
# update category,product and brand
def Updatecategory(request, pk):
    data = category2.objects.get(id=pk)
    form = categoryForm(instance=data)

    if request.method == "POST":
        form = categoryForm(request.POST, instance=data)
        if form.is_valid():
            form.save()
            return redirect("category")
    context = {"form": form}
    return render(request, "MyAdmin/Updatecategory.html", context)


@login_required(login_url="AdminLogin")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def Updatebrand(request, pk):
    data = brand2.objects.get(id=pk)
    form = brandForm(instance=data)
    if request.method == "POST":
        form = brandForm(request.POST, request.FILES, instance=data)
        if form.is_valid():
            form.save()
            return redirect("brand")
    context = {"form": form, "data": data}

    return render(request, "MyAdmin/Updatebrand.html", context)


@login_required(login_url="AdminLogin")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def Updateproducts(request, pk):
    data = Products.objects.get(id=pk)
    form = ProductsForm(instance=data)
    if request.method == "POST":
        form = ProductsForm(request.POST, request.FILES, instance=data)
        if form.is_valid():
            form.save()
            return redirect("products")
    context = {"form": form, "data": data}

    return render(request, "MyAdmin/Updateproduct.html", context)


@login_required(login_url="AdminLogin")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def Deletecategory(request, pk):
    data = category2.objects.get(id=pk)
    if request.method == "POST":

        data.is_delete = False
        data.save()
        return redirect("category")
    context = {"item": data}
    return render(request, "MyAdmin/Deletecategory.html", context)


@login_required(login_url="AdminLogin")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def Deletebrand(request, pk):
    data = brand2.objects.get(id=pk)
    if request.method == "POST":
        data.is_delete = False
        data.save()
        return redirect("brand")
    context = {"item": data}
    return render(request, "MyAdmin/Deletebrand.html", context)


@login_required(login_url="AdminLogin")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def Deleteproducts(request, pk):
    data = Products.objects.get(id=pk)
    if request.method == "POST":
        data.is_delete = False
        data.save()
        return redirect("products")
    context = {"item": data}
    return render(request, "MyAdmin/Deleteproduct.html", context)


def usermanagement(request):
    data = Account.objects.all().filter(is_superadmin=False)

    context = {"data": data}
    return render(request, "MyAdmin/usermanagement.html", context)


def userblock(request, pk):
    if request.user.is_authenticated:
        data = Account.objects.get(id=pk)
        data.is_active = False
        data.save()
        return redirect("usermanagement")


def userunblock(request, pk):
    if request.user.is_authenticated:
        data = Account.objects.get(id=pk)
        data.is_active = True
        data.save()
        return redirect("usermanagement")


def order_management(request):
    order_products = OrderProduct.objects.all()
    print(order_products)
    orders = Order.objects.all()
    print(orders)
    context = {
        "orders": orders,
        "order_products": order_products,
    }
    return render(request, "MyAdmin/order_management.html", context)


# def order_table(request):
#     order_products = list(OrderProduct.objects.values())#we use list because query obj is not serialized

#     print(order_products)
#     orders = list(Order.objects.values())
#     print(orders)
#     context = {
#         "orders": orders,
#         "order_products": order_products,
#     }
#     return JsonResponse(context,safe=False)


def admin_cancel_order(request, order_num):
    # getting the order to decrease the count when user presses the cancel option
    order_number = order_num
    print("order_number")
    order = Order.objects.get(order_number=order_number)
    print(order)
    # getting order product for getting the quantity of items
    order_products = OrderProduct.objects.filter(order_id=order.id)
    print(order_products)
    order.order_cancel = True
    order.status = "Cancelled"
    order.save()

    for order_product in order_products:
        order_product.product.stock += order_product.quantity
        order_product.product.save()

    return redirect("order-management")


# updating the status in ordermanagement
def status(request, id):
    if request.method == "POST":
        status = request.POST[
            "status"
        ]  # status is name and it have a value that corresponds to
        # a staus name
        print(status)
        print(id)
        OrderProduct.objects.filter(id=id).update(status=status)
        return redirect("order-management")


@login_required(login_url="AdminLogin")
def viewcoupon(request):

    values = Coupon.objects.all()
    return render(request, "MyAdmin/couponlist.html", {"values": values})


@login_required(login_url="AdminLogin")
def deletecoupon(request, id):

    my_coupon = Coupon.objects.get(id=id)
    my_coupon.delete()
    return redirect(viewcoupon)


@login_required(login_url="AdminLogin")
def addcoupon(request):

    if request.method == "POST":
        coupon_form = CouponForm(request.POST, request.FILES)
        if coupon_form.is_valid():
            coupon_form.save()
            messages.success(request, "Your coupon has been added sucessfully")
        else:
            messages.error(request, "Error")

        return redirect(viewcoupon)
    coupon_form = CouponForm()

    context = {"coupon_form": coupon_form}
    return render(request, "MyAdmin/addcoupon.html", context)


# generation pdf for sales report
# creating class based views for sales report
class Generate_sales_pdf(View):
    def get(self, request, *args, **kwargs):
        order_products = OrderProduct.objects.filter(
            Q(status__contains="Delivered")
            | Q(order__payment__payment_method__contains="Paypal")
        ).order_by("-created_at")
        open("templates/MyAdmin/sales_pdf.html", "w").write(
            render_to_string(
                "MyAdmin/temp_sales_pdf.html", {"order_products": order_products}
            )
        )
        pdf = html_to_pdf("MyAdmin/sales_pdf.html")
        return HttpResponse(pdf, content_type="application/pdf")


# import os

# os.add_dll_directory(r"C:\Program Files\GTK3-Runtime Win64\bin")
# from django.core.files.storage import FileSystemStorage
# from django.http import HttpResponse
# from django.template.loader import render_to_string
# from weasyprint import HTML
# import tempfile
# def sales_export_pdf(request):
#     response = HttpResponse(content_type="application/pdf")
#     response[
#         "Content-Disposition"
#     ] = "inline; attachement; filename=sales_Report.pdf"

#     response["Content-Transfer-Encoding"] = "binary"

#     order_products = OrderProduct.objects.filter(
#         Q(status__contains="Delivered")
#         | Q(order__payment__payment_method__contains="Paypal")
#         ).order_by("-created_at")

#     html_string = render_to_string(
#         "MyAdmin/temp_sales_pdf.html", {"order_products":order_products, "total": 0}
#     )

#     html = HTML(string=html_string)

#     result = html.write_pdf()

#     with tempfile.NamedTemporaryFile(delete=True) as output:
#         output.write(result)
#         output.flush()
#         output = open(output.name, "rb")
#         response.write(output.read())

#     return response


# converting html to csv file
import csv


def Generate_sales_csv(request):
    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(
        content_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="somefilename.csv"'},
    )
    order_products = OrderProduct.objects.filter(
        Q(status__contains="Delivered")
        | Q(order__payment__payment_method__contains="Paypal")
    ).order_by("-created_at")
    writer = csv.writer(response)
    writer.writerow(
        [
            "Order",
            "Products",
            "Billing Name",
            "Quantity",
            "Phone",
            "Price",
            "Date",
            "Payment Method",
            "Order Status",
            "Discount",
            "Selling Price",
        ]
    )
    for order in order_products:
        writer.writerow(
            [
                order.order.order_number,
                order.product.product_name,
                order.order.full_name,
                order.quantity,
                order.order.phone_number,
                order.product.price,
                order.created_at,
                order.order.payment.payment_method,
                order.status,
                order.order.final_discount,
                order.order.order_total,
            ]
        )

    return response
