from django.urls import path
from . import views
urlpatterns = [
    path('',views.market,name='market'),
    path('category/<slug:category_slug>/',views.market,name='market_by_category'),
    path('category/<slug:category_slug>/<slug:product_slug>/',views.single_product,name='single_product_view'),
    path('search/',views.search,name='search')

]
