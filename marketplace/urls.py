from django.urls import path
from . import views


urlpatterns = [
    path('', views.marketplace, name='marketplace'),
    path('<slug:vendor_slug>/', views.vendor_detail, name='vendor_detail'),

    # ADD TO CART
    path('add_to_cart/<slug:food_slug>/', views.add_to_cart, name='add_to_cart'),
    # DECREASE CART
    path('decrease_cart/<slug:food_slug>/', views.decrease_cart, name='decrease_cart'),
    # DELETE CART ITEM
    path('delete_cart/<slug:food_slug>', views.delete_cart, name='delete_cart')
]
