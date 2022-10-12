from . models import CartItem,Cart
from .views import _cart_id
def counter(request):
    cart_count=0
    if 'admin' in request.path:
        return{}
    else:
        try:
            cart=Cart.objects.filter(cart_id=_cart_id(request))
            if request.user.is_authenticated:#if user is authenticated
                #we get the cart item of that user filter by the user 
                #because there is a user field in cartitem and we already
                #added the cartitem to the auth user whenever the user is
                #logged in 
                cart_items=CartItem.objects.all().filter(user=request.user)
               
            else:
                cart_items=CartItem.objects.all().filter(cart=cart[:1])
            for cart_item in cart_items:
                   cart_count=cart_count+cart_item.quantity
        except Cart.DoesNotExist:
            cart_count=0
    return dict(cart_count=cart_count)

