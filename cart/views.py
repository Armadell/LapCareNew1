from itertools import product
from django.shortcuts import render, redirect, get_object_or_404
from .models import Cart, CartItem
from product.models import Products, Variation
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from .models import Coupon, UsedCoupon, coupon_repeated_check
from django.contrib import messages


def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart


def add_cart(request, product_id):
    # if user is authenticated
    current_user = request.user
    product = Products.objects.get(id=product_id)
    if current_user.is_authenticated:
        product_variation = []
        if request.method == "POST":
            for item in request.POST:
                key = item
                value = request.POST[key]

                try:
                    variation = Variation.objects.get(
                        variation_category__iexact=key,
                        variation_value__iexact=value,
                        product=product,
                    )
                    product_variation.append(variation)

                except:
                    pass

        is_cart_item_exists = CartItem.objects.filter(
            product=product, user=current_user
        ).exists()  # for not repeating product with same variation again and again
        if is_cart_item_exists:

            cart_item = CartItem.objects.filter(
                product=product, user=current_user
            )  # since logged in not use cart=cart

            ex_var_list = []
            id = []  # to increase the cart-item we need id
            for item in cart_item:  # checking for existing variations
                existing_variation = item.variations.all()
                ex_var_list.append(list(existing_variation))
                # the existing variation is
                # return queryset so we need to convert into list to append
                id.append(item.id)

            if product_variation in ex_var_list:
                # if exist we increase the cart item
                # which id? to give from list of id's
                index = ex_var_list.index(
                    product_variation
                )  # getting the id of current variation
                # from existing variation
                item_id = id[index]
                item = CartItem.objects.get(product=product, id=item_id)
                item.quantity += 1
                item.save()
            else:
                # if not we create new cart item with product variations
                item = CartItem.objects.create(
                    product=product, quantity=1, user=current_user
                )
                if len(product_variation) > 0:
                    item.variations.clear()
                    item.variations.add(
                        *product_variation
                    )  # * is used to make sure it will add all the product variations

                # cart_item.quantity += 1
                item.save()
        else:
            # if cart not exists
            cart_item = CartItem.objects.create(
                product=product,
                quantity=1,
                user=current_user,
            )

            if len(product_variation) > 0:
                cart_item.variations.clear()

                cart_item.variations.add(*product_variation)
            cart_item.save()

        return redirect("cart")

    else:
        # if user is not authenticated
        product_variation = []
        if request.method == "POST":
            for item in request.POST:
                key = item
                value = request.POST[key]
                try:
                    variation = Variation.objects.get(
                        variation_category__iexact=key,
                        variation_value__iexact=value,
                        product=product,
                    )
                    product_variation.append(variation)

                except:
                    pass

        try:
            cart = Cart.objects.get(cart_id=_cart_id(request))
        except Cart.DoesNotExist:
            cart = Cart.objects.create(cart_id=_cart_id(request))
            cart.save()
        is_cart_item_exists = CartItem.objects.filter(
            product=product, cart=cart
        ).exists()  # for not repeating product with same variation again and again

        if is_cart_item_exists:

            cart_item = CartItem.objects.filter(product=product, cart=cart)
            # existing variation ->database
            # current variation->product_variation
            # item_id->database
            # first we check if the current variation is inside the existing variation
            # we will increase the cart item
            ex_var_list = []
            id = []  # to increase the cart-item we need id
            for item in cart_item:  # checking for existing variations
                existing_variation = item.variations.all()
                ex_var_list.append(list(existing_variation))
                # the existing variation is
                # return queryset so we need to convert into list to append
                id.append(item.id)
            print(ex_var_list)
            if product_variation in ex_var_list:
                # if exist we increase the cart item
                # which id? to give from list of id's
                index = ex_var_list.index(
                    product_variation
                )  # getting the id of current variation
                # from existing variation
                item_id = id[index]
                item = CartItem.objects.get(product=product, id=item_id)
                item.quantity += 1
                item.save()
            else:
                # if not we create new cart item with product variations
                item = CartItem.objects.create(product=product, quantity=1, cart=cart)
                if len(product_variation) > 0:
                    item.variations.clear()
                    cart_item.variations.add(
                        *product_variation
                    )  # * is used to make sure it will add all the product variations

                    # cart_item.quantity += 1
                    item.save()
        else:

            cart_item = CartItem.objects.create(
                product=product,
                quantity=1,
                cart=cart,
            )

            if len(product_variation) > 0:
                cart_item.variations.clear()

                cart_item.variations.add(*product_variation)
            cart_item.save()

        return redirect("cart")


def remove_cart(request, product_id, cart_item_id):

    product = get_object_or_404(Products, id=product_id)

    try:

        if request.user.is_authenticated:
            cart_item = CartItem.objects.get(
                product=product, user=request.user, id=cart_item_id
            )
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_item = CartItem.objects.get(
                product=product, cart=cart, id=cart_item_id
            )
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()

    except:
        pass
    return redirect("cart")


def delete_cart(request, product_id, cart_item_id):
    product = get_object_or_404(Products, id=product_id)
    if request.user.is_authenticated:
        cart_item = CartItem.objects.get(
            product=product, user=request.user, id=cart_item_id
        )
    else:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_item = CartItem.objects.get(product=product, cart=cart, id=cart_item_id)
    cart_item.delete()
    return redirect("cart")


def cart(request, total=0, quantity=0, cart_items=None):
    try:

        tax = 0
        grand_total = 0
        if request.user.is_authenticated:

            cart_items = CartItem.objects.filter(user=request.user, is_active=True)
            try:
                is_coupon_repeated = coupon_repeated_check.objects.filter(
                    user_name=request.user,
                    is_repeated=True,
                    coupon_name=request.session["coupon_code"],
                ).exists()
            except:
                pass

            if "coupon_code" in request.session and not is_coupon_repeated:
                print("inside session")

                is_coupon_repeated = coupon_repeated_check()
                is_coupon_repeated.user_name = request.user
                is_coupon_repeated.is_repeated = True
                is_coupon_repeated.coupon_name = request.session["coupon_code"]

                is_coupon_repeated.save()
                coupon = Coupon.objects.get(coupon_code=request.session["coupon_code"])
                print("inside elsre")

                reduction = coupon.discount
                print('reduction ==',reduction)
                request.session['reduction'] = reduction

                messages.success(request, "coupon code  added")
            else:

                reduction = 0

        else:
            reduction = 0
            cart = Cart.objects.get(cart_id=_cart_id(request))  # iit is used to assign
            # the cart item to the cart using the current session
            # id of the browser
            cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        discount_list = []
        total_list = []
        total = 0
        for cart_item in cart_items:
            offer = cart_item.product.offer_price()

            print("offer", offer)
            discount = cart_item.product.discount_price() * cart_item.quantity
            print("discount", discount)
            discount_list.append(discount)

            total = offer * cart_item.quantity
            total_list.append(total)
            print("inside loop total", total)

            quantity = cart_item.quantity
            print("inside loop quantity", quantity)

        print("outside loop total", total)
        print("outside loop quantity", quantity)

        sum_total = 0
        total=0
        
        try:
            print("total lenght", len(total_list))
            for i in range(0, len(discount_list)):
                sum_total = sum_total + int(discount_list[i])  # taking total discount.
                print("inside sum total", sum_total)
            print("outsude total", sum_total)
            for i in range(0, len(total_list)):
                total = total + int(total_list[i])

                print("loop inside the total", total)
        except:
            pass

        print(total)
        tax = (2 * total) / 100

        grand_total = round(total + tax - reduction, 2)
        print("grand total", grand_total)
        print("reduction", reduction)
        total_discount = sum_total + reduction
        coupon_code = 0
        try:
            coupon_code = request.session["reduction"]
        except:
            pass
        print(coupon_code)
       

    except ObjectDoesNotExist:
        pass
    context = {
        "total": total,
        "quantity": quantity,
        "cart_items": cart_items,
        "grand_total": grand_total,
        "tax": tax,
        "coupon_code": coupon_code,
        "discount": total_discount,
    }

    return render(request, "User/cart.html", context)


@login_required(login_url="login")
def check_out(request, total=0, quantity=0, cart_items=None):

    try:
        tax = 0
        grand_total = 0
        grand_total = 0
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user, is_active=True)
            if "coupon_code" in request.session:

                coupon = Coupon.objects.get(coupon_code=request.session["coupon_code"])
                reduction = coupon.discount
                print("red", reduction)

            else:
                reduction = 0
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))  # iit is used to assign
            # the cart item to the cart using the current session
            # id of the browser
            cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        org_total = 0
        discount = 0

        for cart_item in cart_items:
            offer = cart_item.product.offer_price()
            discount = cart_item.product.discount_price()
            print("from model", discount)
            total += offer * cart_item.quantity
            quantity = cart_item.quantity
        for cart_item in cart_items:

            org_total += cart_item.product.price * cart_item.quantity
        print(org_total)
        print(total)
        tax = (2 * total) / 100

        grand_total = round(total + tax - reduction, 2)
        discount = org_total - grand_total
        print("discount", discount)
    except ObjectDoesNotExist:
        pass
    context = {
        "total": total,
        "quantity": quantity,
        "cart_items": cart_items,
        "grand_total": grand_total,
        "tax": tax,
        "discount": discount,
    }
    return render(request, "User/checkout.html", context)
    # apply coupon the reauest is comming from add coupon form as post


def coupon_apply(request):

    if request.method == "POST":
        print("hello")
        coupon_code = request.POST.get("coupon_code")
        print(coupon_code)
        try:
            if Coupon.objects.get(coupon_code=coupon_code):
                coupon_exist = Coupon.objects.get(coupon_code=coupon_code)
                try:

                    if UsedCoupon.objects.get(user=request.user, coupon=coupon_exist):

                        return redirect("cart")

                except:

                    request.session["coupon_code"] = coupon_code
                    is_coupon_repeated = coupon_repeated_check.objects.filter(
                        user_name=request.user,
                        is_repeated=True,
                        coupon_name=request.session["coupon_code"],
                    ).exists()
                    if is_coupon_repeated:
                        messages.error(request, "coupon code already added")
                        del request.session["coupon_code"]

        except:

            pass
    return redirect("cart")
