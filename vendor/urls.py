from django.urls import path
from . import views
from accounts import views as AccountViews


urlpatterns = [
    path('', AccountViews.vendorDashboard, name='vendor'),
    path('profile/', views.vprofile, name='vprofile'),
    path('menu-builder/', views.menu_builder, name='menu_builder'),
    path('menu-builder/category/search/<slug:category_slug>/', views.fooditems_by_category, name='fooditems_by_category'),

    # Category CRUD
    path('menu-builder/category/add/', views.add_category, name='add_category'),
    path('menu-builder/category/edit/<slug:category_slug>/', views.edit_category, name='edit_category'),
    path('menu-builder/category/delete/<slug:category_slug>/', views.delete_category, name='delete_category'),

    # Food CRUD
    # path('menu-builder/category/add/', views.add_category, name='add_category'),
    # path('menu-builder/category/edit/<slug:category_slug>/', views.edit_category, name='edit_category'),
    # path('menu-builder/category/delete/<slug:category_slug>/', views.delete_category, name='delete_category'),

]

