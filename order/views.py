from pickletools import read_decimalnl_short
from django.shortcuts import render, redirect
from cart.models import Coupon, UsedCoupon
from product.models import Products
from .forms import OrderForm
from .models import Order, OrderProduct, Payment
from django.http import HttpResponse, JsonResponse
from cart.models import CartItem, coupon_repeated_check
import datetime

import json

# Create your views here.
def place_order(request, total=0, quantity=0):

    current_user = request.user
    # if cart count <= 0 then redirected to the shop page
    cart_items = CartItem.objects.filter(user=current_user, is_active=True)
    cart_count = cart_items.count()
    if cart_count <= 0:
        return redirect("market")
    grand_total = 0
    tax = 0
    reduction = 0

    if "reduction" in request.session:

        reduction = request.session["reduction"]

    else:
        reduction = 0
    discount_list = []
    total_list = []
    for cart_item in cart_items:
        offer = cart_item.product.offer_price()
        discount = cart_item.product.discount_price() * cart_item.quantity
        discount_list.append(discount)
        print("discount for individual", discount)
        print(offer)
        total = offer * cart_item.quantity
        total_list.append(total)
        print("total", total)
        quantity = cart_item.quantity
        total = 0
        sum_total = 0
        try:
            for i in range(0, len(discount_list)):
                sum_total = sum_total + int(discount_list[i])
            for i in range(0, len(total_list)):
                total = total + int(total_list[i])
        except:
            pass

        print(total)
        tax = (2 * total) / 100

        try:
            grand_total = round(total + tax - reduction, 2)
        except:
            grand_total = round(total + tax, 2)
        print("reduction", reduction)
        total_discount = sum_total + reduction
        print("total discount", total_discount)
        try:
            del request.session["reduction"]
        except:
            pass
    if request.method == "POST":
        form = OrderForm(request.POST)
        if form.is_valid():
            # store all billing information inside the order table
            data = Order()
            data.user = current_user
            data.first_name = form.cleaned_data["first_name"]
            data.last_name = form.cleaned_data["last_name"]
            data.phone_number = form.cleaned_data["phone_number"]
            data.email = form.cleaned_data["email"]
            data.address_line_1 = form.cleaned_data["address_line_1"]
            data.address_line_2 = form.cleaned_data["address_line_2"]
            data.country = form.cleaned_data["country"]
            data.state = form.cleaned_data["state"]
            data.city = form.cleaned_data["city"]
            data.pincode = form.cleaned_data["pincode"]
            data.order_note = form.cleaned_data["order_note"]
            data.order_total = grand_total

            data.final_discount = total_discount
            data.tax = tax
            data.ip = request.META.get("REMOTE_ADDR")  # TO GET THE IP OF THE USER
            data.save()  # when we save this will create a primary key
            # genetate order number
            # generate order number
            yr = int(datetime.date.today().strftime("%Y"))
            dt = int(datetime.date.today().strftime("%d"))
            mt = int(datetime.date.today().strftime("%m"))
            d = datetime.date(yr, mt, dt)
            current_date = d.strftime(
                "%Y%m%d"
            )  # 20210305 like this(in string format using strtime)
            order_number = current_date + str(
                data.id
            )  # (we get id because we save the data)
            data.order_number = order_number
            data.save()

            # displaying the data into the templates
            order = Order.objects.get(
                user=current_user, is_ordered=False, order_number=order_number
            )
            context = {
                "order": order,
                "cart_items": cart_items,
                "total": total,
                "tax": tax,
                "grand_total": grand_total,
                "total_discount": total_discount,
            }
            return render(request, "User/payment.html", context)
        else:
            return redirect("check-out")


def payment(request):

    body = json.loads(
        request.body
    )  # we are passing the order to payment and order number which is already
    # generated is get from the json
    order = Order.objects.get(
        user=request.user, is_ordered=False, order_number=body["orderID"]
    )

    # Store transaction details inside Payment model
    payment = Payment(
        user=request.user,
        payment_id=body["transID"],
        payment_method=body["payment_method"],
        amount_paid=order.order_total,  # we already asssign the total to the order ie grand total
        status=body["status"],
    )
    payment.save()

    order.payment = payment  # updating payment in order
    order.is_ordered = True
    order.status = "Completed"
    order.save()

    # Move the cart items to Order Product table
    cart_items = CartItem.objects.filter(user=request.user)

    for item in cart_items:
        orderproduct = OrderProduct()
        # using the orderproduct we can differentiate#orderproduct is an object and order_id is an instance
        orderproduct.order_id = order.id
        # order_id can call because order is the foreign key or orderproduct
        # here the order id is same for every product ie.in a single payment there will be multiple products
        # but have same order id
        orderproduct.payment = (
            payment  # ie _id will give the id of corresponding foreign ke
        )
        orderproduct.user_id = request.user.id
        orderproduct.product_id = item.product_id
        # product is the foreign key of cartitem
        # so we use _id to get the products id so it display product name.why?
        # look at the model and we return the product name as string
        orderproduct.quantity = item.quantity
        orderproduct.product_price = item.product.offer_price()

        orderproduct.ordered = True
        orderproduct.status = "Pending"
        orderproduct.save()

        cart_item = CartItem.objects.get(
            id=item.id
        )  # taking the product vairation by  id
        product_variation = cart_item.variations.all()  # getting the product variation
        orderproduct = OrderProduct.objects.get(id=orderproduct.id)
        orderproduct.variations.set(
            product_variation
        )  # setting the product variation to orderproduct
        orderproduct.save()

        # Reduce the quantity of the sold products
        product = Products.objects.get(id=item.product_id)
        product.stock -= item.quantity
        product.save()

    CartItem.objects.filter(user=request.user).delete()
    # clear cart

    # send the order received email to the customer

    # send order number and transaction id back to sendData method via jsonresponse
    data = {
        "order_number": order.order_number,
        "transID": payment.payment_id,
    }
    return JsonResponse(data)


def order_complete(request):
    order_number = request.GET.get("order_number")
    transID = request.GET.get("payment_id")

    try:
        order = Order.objects.get(
            order_number=order_number, is_ordered=True, order_cancel=False
        )
        order_products = OrderProduct.objects.filter(order_id=order.id)
        payment = Payment.objects.get(payment_id=transID)
        for i in order_products:
            sub_total = i.product_price * i.quantity
        context = {
            "order": order,
            "order_products": order_products,
            "order_number": order.order_number,
            "transID": payment.payment_id,
            "payment": payment,
            "sub_total": sub_total,
            "reduction": order.final_discount,
        }

        return render(request, "User/order_complete.html", context)
    except (Payment.DoesNotExist, Order.DoesNotExist):
        return redirect("home")


def cod_payment(request, order_num):
    current_user = request.user
    # generate order number
    try:
        order = Order.objects.get(
            user=current_user, is_ordered=False, order_number=order_num
        )
        payment = Payment(
            user=request.user,
            payment_method="Cash on delivery",
            amount_paid=order.order_total,  # we already asssign the total to the order ie grand totdeldal
            status="pending",
        )
        payment.save()
        order.is_ordered = True

        order.payment = payment
        order.status = "completed"
        order.save()

        # Move the cart items to Order Product table
        cart_items = CartItem.objects.filter(user=current_user)

        for item in cart_items:
            orderproduct = OrderProduct()
            # using the orderproduct we can differentiate#orderproduct is an object and order_id is an instance
            orderproduct.order_id = order.id

            # order_id can call because order is the foreign key or orderproduct
            # here the order id is same for every product ie.in a single payment there will be multiple products
            # but have same order id
            # ie _id will give the id of corresponding foreign key

            orderproduct.user_id = current_user.id
            orderproduct.product_id = (
                item.product_id
            )  # product is the foreign key of cartitem
            # so we use _id to get the products id so it display product name.why?
            # look at the model and we return the product name as string
            orderproduct.quantity = item.quantity
            orderproduct.product_price = item.product.price
            orderproduct.ordered = True
            orderproduct.save()

            cart_item = CartItem.objects.get(
                id=item.id
            )  # taking the product vairation by  id
            product_variation = (
                cart_item.variations.all()
            )  # getting the product variation
            orderproduct = OrderProduct.objects.get(id=orderproduct.id)
            orderproduct.variations.set(
                product_variation
            )  # setting the product variation to orderproduct
            orderproduct.status = "Pending"
            orderproduct.save()

            # Reduce the quantity of the sold products
            product = Products.objects.get(id=item.product_id)
            product.stock -= item.quantity
            product.save()

        CartItem.objects.filter(user=request.user).delete()

        order = Order.objects.get(
            order_number=order_num, is_ordered=True, order_cancel=False
        )
        order_products = OrderProduct.objects.filter(order_id=order.id)

        for i in order_products:
            sub_total = i.product_price * i.quantity
        context = {
            "order": order,
            "order_products": order_products,
            "order_number": order.order_number,
            "sub_total": sub_total,
        }
        return render(request, "User/cod.html", context)
    except:
        return redirect("dashboard")


def cancel_order(request, id):

    # getting the order to decrease the count when user presses the cancel option
    order_number = id
    print("order_number", order_number)
    order_products = OrderProduct.objects.get(user=request.user, pk=order_number)

    # getting order product for getting the quantity of items

    order_products.orderproduct_cancel = True
    order_products.status = "Canceled"
    order_products.save()

    order_products.product.stock = order_products.quantity + 1
    order_products.product.save()

    return redirect("my-orders")


# coupon functionalities
def return_order(request, id):
    order_number = id

    order_products = OrderProduct.objects.get(user=request.user, pk=order_number)
    print("return order", order_products)
    order_products.orderproduct_cancel = True
    order_products.return_status = False
    order_products.status = "Canceled"
    order_products.save()

    order_products.product.stock = order_products.quantity + 1
    order_products.product.save()

    return redirect("my-orders")
