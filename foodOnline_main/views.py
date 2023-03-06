from django.shortcuts import render
from django.http import HttpResponse
from vendor.models import Vendor
from menu.models import Category
def home(request):
    vendors = Vendor.objects.filter(is_approved=True, user__is_active=True)[:8]
    categories = Category.objects.all()
    print(vendors)
    context = {
        'vendors': vendors,
        'categories': categories,
    }
    return render(request, 'home.html', context)