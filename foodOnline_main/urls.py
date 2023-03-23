from django.contrib import admin
from django.urls import path, include
from . import views
from django.conf import settings
from django.conf.urls.static import static
from marketplace.views import cart, search, checkout

urlpatterns = [
    # docs
    path('admin/doc/', include('django.contrib.admindocs.urls')),
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('', include('accounts.urls')),
    # path('vendor/', include('vendor.urls')),
    path('marketplace/', include('marketplace.urls')),

     # CART
    path('cart/', cart, name='cart'),

    # SEARCH
    path('search/', search, name='search'),

    # CHECKOUT
    path('chekcout/', checkout, name='checkout'),

    # ORDERS
    path('orders/', include('orders.urls')),


]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)