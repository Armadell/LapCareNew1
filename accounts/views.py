from csv import register_dialect
import email
from django.shortcuts import render, redirect, get_object_or_404
from .forms import RegistrationForm
from .models import Account, UserProfile
from django.contrib import auth, messages
from . import verify
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from cart.views import _cart_id
from cart.models import Cart, CartItem
from product.models import Products
from order.models import Order, OrderProduct
from .forms import UserProfileForm, UserForm
import requests  # we install it and used to find some specific pattern in url

# in our case if the url contains next then we must not redirect to dashboard
def verify_user(user):
    if user.is_superadmin == True:
        return False
    else:
        return True


def register(request):
    if request.session.has_key("email"):
        return redirect("home")
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data["first_name"]
            last_name = form.cleaned_data["last_name"]
            phone_number = form.cleaned_data["phone_number"]
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]
            username = email.split("@")[0]
            request.session["first_name"] = first_name
            request.session["last_name"] = last_name
            request.session["email"] = email
            request.session["password"] = password
            request.session["username"] = username
            request.session["checkmobile"] = phone_number
            verify.send(phone_number)

            return redirect("otpcheck")
    else:
        messages.error(request, "Invalid credentials!")
        form = RegistrationForm()

    context = {"form": form}
    return render(request, "User/register.html", context)


def login(request):
    if request.session.has_key("email"):
        return redirect("home")
    if request.method == "POST":

        email = request.POST.get("Email")
        password = request.POST.get("password")
        user = auth.authenticate(email=email, password=password)
        if user is not None:
            try:
                cart = Cart.objects.get(cart_id=_cart_id(request))
                is_cart_item_exists = CartItem.objects.filter(
                    cart=cart
                ).exists()  # check if any cart exists
                if is_cart_item_exists:
                    cart_item = CartItem.objects.filter(
                        cart=cart
                    )  # for assigning cart to the user
                    # for grouping cart items
                    # getting the product variation by cart id
                    product_variation = []
                    for item in cart_item:
                        variation = item.variations.all()  # taking all the variations
                        product_variation.append(list(variation))
                    # getting cart items from user to access his product variations
                    cart_item = CartItem.objects.filter(
                        user=user
                    )  # since logged in not use cart=cart

                    ex_var_list = []
                    id = []  # to increase the cart-item we need id
                    for item in cart_item:  # checking for existing variations
                        existing_variation = item.variations.all()
                        ex_var_list.append(list(existing_variation))
                        # the existing variation is
                        # return queryset so we need to convert into list to append
                        id.append(item.id)
                    # check for product variation for existing variation in lists
                    for pr in product_variation:
                        if pr in existing_variation:
                            index = ex_var_list.index(pr)
                            item_id = id[index]
                            item = CartItem.objects.get(id=item_id)
                            item.quantity += 1
                            item.user = user
                            item.save()
                        else:
                            cart_item = CartItem.objects.filter(cart=cart)
                            for item in cart_item:
                                item.user = user
                                item.save()
            except:
                pass
            request.session["email"] = email
            auth.login(request, user)
            messages.success(request, "you are successfuly logged in")
            url = request.META.get("HTTP_REFERER")  # it is used to grab the previous
            print("url", url)
            # url we came from
            try:
                query = requests.utils.urlparse(url).query  # gives the url in query
                print("query", query)
                # query=next=/cart/checkout
                params = dict(x.split("=") for x in query.split("&"))
                if "next" in params:
                    nextPage = params["next"]
                    print("nextPage", nextPage)
                    return redirect(nextPage)
            except:
                return redirect("dashboard")
        else:
            messages.error(request, "invalid credentials")

            return redirect("login")

    return render(request, "User/login.html")


@login_required(login_url="login")
def logout(request):

    auth.logout(request)
    return redirect("home")


def loginotp(request):

    if request.user.is_authenticated:
        return redirect("home")
    if request.method == "POST":

        mobile = request.POST.get("phone")
        print(mobile)
        request.session["checkmobile"] = mobile

        try:
            p = Account.objects.get(phone_number=mobile)
            print(p)
            if Account.objects.filter(phone_number=mobile):
                print(mobile)
                verify.send(mobile)

                return redirect("otpcheck1")

        except:

            messages.error(request, "Something went wrong!")
            return redirect("login")

    return render(request, "User/loginotp.html")


def otpcheck(request):
    if request.user.is_authenticated:
        return redirect("home")
    if request.method == "POST":
        otp = request.POST["otpcode"]
        mobile = request.session["checkmobile"]
        a = verify.check(mobile, otp)
        if a:
            first_name = request.session["first_name"]
            last_name = request.session["last_name"]
            email = request.session["email"]

            password = request.session["password"]
            username = request.session["username"]
            mobile = request.session["checkmobile"]
            user = Account.objects.create_user(
                first_name=first_name,
                last_name=last_name,
                email=email,
                password=password,
                username=username,
            )
            user.phone_number = mobile
            user.is_active = True
            user.save()

            # creating the user profile
            profile = UserProfile()
            profile.user_id = user.id  # user_id is an
            # instance of profile and it doesnt know about the id of
            # specific user it only refers to it
            profile.profile_picture = "default/default-image.jpg"
            profile.save()
            print(user)
            auth.login(request, user)
            messages.success(request, "Account created successfuly!")
            return redirect("home")
        else:
            return redirect("login")
    return render(request, "User/otpcheck.html")


def otpcheck1(request):
    if request.user.is_authenticated:
        return redirect("home")
    if request.method == "POST":
        otp = request.POST["otpcode"]
        mobile = request.session["checkmobile"]

        a = verify.check(mobile, otp)
        if a:
            user = Account.objects.get(phone_number=mobile)
            auth.login(request, user)
            messages.success(request, "Account created successfuly!")
            return redirect("home")
        else:
            return redirect("login")
    return render(request, "User/otpcheck1.html")


@login_required(login_url="login")
def dashboard(request):
    userprofile = UserProfile.objects.get(user_id=request.user)
    orders = Order.objects.order_by("-created_at").filter(
        user_id=request.user.id, is_ordered=True
    )
    orders_count = orders.count()  # passing count to the dashboard
    context = {"orders_count": orders_count, "userprofile": userprofile}
    return render(request, "User/dashboard.html", context)


@login_required(login_url="login")
def my_orders(request):
    orders = Order.objects.filter(user_id=request.user, is_ordered=True).order_by(
        "-created_at"
    )  # - is descending
    order_products = OrderProduct.objects.filter(
        order__is_ordered=True,
        user=request.user,
        orderproduct_cancel=False,
        return_status=True,
    )
    context = {
        "orders": orders,
        "order_products": order_products,
    }
    return render(request, "User/my_orders.html", context)


from django.db.models import Q


def order_history(request):
    orders = Order.objects.filter(user_id=request.user, is_ordered=True).order_by(
        "-created_at"
    )  # - is descending
    order_products = OrderProduct.objects.filter(
        Q(user=request.user, orderproduct_cancel=True) | Q(return_status=False)
    ).order_by(
        "-created_at"
    )  # - is descending
    print("orderproduct", order_products)
    context = {
        "order_products": order_products,
        "orders": orders,
    }
    return render(request, "User/order_history.html", context)


@login_required(login_url="login")
def edit_profile(request):
    userprofile = get_object_or_404(UserProfile, user=request.user)
    if request.method == "POST":
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(
            request.POST, request.FILES, instance=userprofile
        )
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, "Your profile has been updated")
    else:
        user_form = UserForm(instance=request.user)
        profile_form = UserProfileForm(instance=userprofile)
    context = {
        "user_form": user_form,
        "profile_form": profile_form,
        "userprofile": userprofile,
    }

    return render(request, "User/edit_profile.html", context)


def change_password(request):
    return render(request, "User/change_password.html")


@login_required(login_url="login")
def change_password(request):
    if request.method == "POST":
        current_password = request.POST["current_password"]
        new_password = request.POST["new_password"]
        confirm_password = request.POST["confirm_password"]

        user = Account.objects.get(
            username__exact=request.user.username
        )  # exact is case sensitive

        if new_password == confirm_password:
            success = user.check_password(
                current_password
            )  # check_password is djangos build in method
            # which is used to check the hashed passowrd with the plain text we entered
            if success:
                user.set_password(new_password)
                user.save()
                auth.logout(request)
                messages.success(request, "Password updated successfully")
                return redirect("change_password")
            else:
                messages.error(request, "Please enter valid current password")
                return redirect("change-password")
        else:
            messages.error(request, "Password does not match")
            return redirect("change_password")

    return render(request, "user/change_password.html")


@login_required(login_url="userlogin")
def order_detail(request, order_id):  # order_id is the order number from template
    order_detail = OrderProduct.objects.filter(
        order__order_number=order_id
    )  # with the '__' we can access foreign key objects
    order = Order.objects.get(order_number=order_id)
    subtotal = 0

    for i in order_detail:
        subtotal = subtotal + i.product_price * i.quantity

    context = {
        "order_detail": order_detail,
        "order": order,
        "subtotal": subtotal,
    }

    return render(request, "User/order_detail.html", context)
