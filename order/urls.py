from django.urls import path
from . import views
urlpatterns = [
    path('place_order/',views.place_order,name='place-order'),
    path('payment/',views.payment,name='payment'),
    path('order_complete/',views.order_complete,name='order-complete'), 
    path('cod_payment/<int:order_num>/',views.cod_payment,name="cod_payment"),
    path('cancel_order/<int:id>/',views.cancel_order,name="cancel_order"),
    path('return_order/<int:id>/',views.return_order,name='return_order')
]
