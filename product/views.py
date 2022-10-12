from tkinter import E
from unicodedata import category
from django.shortcuts import render, get_object_or_404,redirect
from .models import Products
from category.models import category as category2
from cart.views import _cart_id
from cart.models import CartItem
from django.db.models import Q
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator


# Create your views here.
def market(request, category_slug=None):
    categories = None
    data = None
    if category_slug != None:
        categories = get_object_or_404(category2, slug=category_slug)
        data = (
            Products.objects.all()
            .filter(category=categories, available=True)
            .order_by("id")
        )
        paginator = Paginator(data, 3)
        page = request.GET.get("page")
        paged_products = paginator.get_page(page)  #
        product_count = data.count()
    else:
        data = Products.objects.all().filter(available=True).order_by("id")
        paginator = Paginator(data, 3)  # the no of pages we want in a page
        page = request.GET.get("page")  # takes the value of page from url
        paged_products = paginator.get_page(
            page
        )  # the no of products we want is stored here,it takes the page
        # and return the page object and also it determines the no of products shown in a single page
        product_count = data.count()
    context = {"products": paged_products, "count": product_count}
    return render(request, "User/market.html", context)


def single_product(request, category_slug, product_slug):
    try:
        single_product = Products.objects.get(
            category__slug=category_slug, slug=product_slug
        )
        in_cart = CartItem.objects.filter(
            cart__cart_id=_cart_id(request), product=single_product
        ).exists()

    except Exception as e:
        raise e
    context = {"single_product": single_product, "in_cart": in_cart}
    return render(request, "User/single_product.html", context)


def search(request):
    
    if request.method=="GET" and "keyword" in request.GET:
        keyword = request.GET["keyword"]
        if keyword is not None and keyword != '':
            
            products = Products.objects.order_by("-created_date").filter(
                Q(product_name__icontains=keyword) | Q(description__icontains=keyword)
            )
            product_count = products.count()
            context = {
                "products": products,
                "count": product_count,
            }
            return render(request, "User/market.html", context)
        else:
            return redirect('home')
        
