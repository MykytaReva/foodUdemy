from django.db.models import Prefetch

from django.http import HttpResponse, JsonResponse

from django.db.models import Q

from django.contrib.auth.decorators import login_required

from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.measure import D
from django.contrib.gis.db.models.functions import Distance

from django.shortcuts import redirect
from django.shortcuts import render, get_object_or_404

from vendor.models import Vendor, OpeningHour
from menu.models import Category, FoodItem
from orders.forms import OrderForm
from orders.models import Order
from accounts.models import UserProfile

from .models import Cart
from .context_processors import get_cart_counter, get_cart_amount

from datetime import date, datetime



# is_ajax has been deprecated
def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'


def marketplace(request):
    vendors = Vendor.objects.filter(is_approved=True, user__is_active=True)[:8]
    vendor_count = vendors.count()
    context = {
        'vendors': vendors,
        'vendor_count': vendor_count,
    }
    return render(request, 'marketplace/listings.html', context)


def vendor_detail(request, vendor_slug=None):
    vendor = get_object_or_404(Vendor, vendor_slug=vendor_slug)
    categories = Category.objects.filter(vendor=vendor).prefetch_related(
        Prefetch(
            'fooditems',
            queryset = FoodItem.objects.filter(is_available=True)
        )
    )

    opening_hours = OpeningHour.objects.filter(vendor=vendor).order_by('day', '-from_hour')


     # Check current day's opening hours.
    today_date = date.today()
    today = today_date.isoweekday()

    current_opening_hours = OpeningHour.objects.filter(vendor=vendor, day=today)

    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(user=request.user)
    else:
        cart_items = None
    context = {
        'vendor': vendor,
        'categories': categories,
        'cart_items': cart_items,
        'opening_hours': opening_hours,
        'current_opening_hours': current_opening_hours,

    }
    return render(request, 'marketplace/vendor_detail.html', context)


def add_to_cart(request, food_slug):
    if request.user.is_authenticated:
        if is_ajax(request=request):
            # Check if the food item exists
            try:
                fooditem = FoodItem.objects.get(slug=food_slug)
                # Check if the user has already added that food to the cart
                try:
                    chkCart = Cart.objects.get(user=request.user, fooditem=fooditem)
                    # Increase the cart quantity
                    chkCart.quantity += 1
                    chkCart.save()
                    return JsonResponse({
                        'status': 'Success',
                        'message': 'Increased the cart quantity',
                        'cart_counter':get_cart_counter(request),
                        'qty':chkCart.quantity,
                        'cart_amount': get_cart_amount(request),
                        })
                except:
                    chkCart = Cart.objects.create(user=request.user, fooditem=fooditem, quantity=1)
                    return JsonResponse({
                        'status': 'Success',
                        'message': 'Added the food to the cart',
                        'cart_counter':get_cart_counter(request),
                        'qty':chkCart.quantity,
                        'cart_amount': get_cart_amount(request),
                        })
            except:
                return JsonResponse({'status':'Failed', 'message': 'This food does not exist!'})
        else:
            return JsonResponse({'status': 'Failed', 'message': 'Invalid request!'})

    else:
        return JsonResponse({'status': 'login_required', 'message': 'Please login to continue'})


def decrease_cart(request, food_slug):
    if request.user.is_authenticated:
        if is_ajax(request=request):
            # Check if the food item exists
            try:
                fooditem = FoodItem.objects.get(slug=food_slug)
                # Check if the user has already added that food to the cart
                try:
                    chkCart = Cart.objects.get(user=request.user, fooditem=fooditem)
                    if chkCart.quantity > 1:
                        # decrease the cart quantity
                        chkCart.quantity -= 1
                        chkCart.save()
                    else:
                        chkCart.delete()
                        chkCart.quantity = 0
                    return JsonResponse({
                        'status': 'Success',
                        'cart_counter':get_cart_counter(request),
                        'qty':chkCart.quantity,
                        'cart_amount': get_cart_amount(request),
                        })
                except:
                    return JsonResponse({
                        'status': 'Failed',
                        'message': 'You do not have this item in your cart!',
                        'qty':chkCart.quantity,
                        'cart_amount': get_cart_amount(request),
                        })
            except:
                return JsonResponse({'status':'Failed', 'message': 'This food does not exist!'})
        else:
            return JsonResponse({'status': 'Failed', 'message': 'Invalid request!'})

    else:
        return JsonResponse({'status': 'login_required', 'message': 'Please login to continue'})

@login_required(login_url='login')
def cart(request):
    cart_items = Cart.objects.filter(user=request.user).order_by('created_at')
    context = {
        'cart_items': cart_items,
    }
    return render(request, 'marketplace/cart.html', context)


def delete_cart(request, food_slug):
    if request.user.is_authenticated:
        if is_ajax(request=request):
            try:
                #check if the cart item exists
                cart_item = Cart.objects.get(user=request.user, fooditem__slug=food_slug)
                if cart_item:
                    cart_item.delete()
                    return JsonResponse({
                        'status': 'Success',
                        'message': 'Cart item has been deleted!',
                        'cart_counter': get_cart_counter(request),
                        'cart_amount': get_cart_amount(request),
                    })
            except:
                return JsonResponse({'status': 'Failed', 'message': 'Cart Item does not exist!'})
        else:
            return JsonResponse({'status': 'Failed', 'message': 'Invalid request!'})


def search(request):
    if not 'address' in request.GET:
        return redirect('marketplace')
    else:
        address = request.GET['address']
        latitude = request.GET['lat']
        longtitude = request.GET['lng']
        radius = request.GET['radius']
        keyword = request.GET['keyword']

        # get vendor ids that has the food item the user is looking for
        fetch_vendors_by_fooditems = FoodItem.objects.filter(food_title__icontains=keyword, is_available=True).values_list('vendor',flat=True)
        # vendors = Vendor.objects.filter(vendor_name__icontains=keyword, is_approved=True, user__is_active=True)

        vendors = Vendor.objects.filter(Q(id__in=fetch_vendors_by_fooditems) | Q(vendor_name__icontains=keyword, is_approved=True, user__is_active=True))
        if latitude and longtitude and radius:
            pnt = GEOSGeometry('POINT(%s %s)' % (longtitude, latitude))

            vendors = Vendor.objects.filter(
                Q(id__in=fetch_vendors_by_fooditems) |
                Q(vendor_name__icontains=keyword, is_approved=True, user__is_active=True),
                user_profile__location__distance_lte=(pnt, D(km=radius))
            ).annotate(distance=Distance("user_profile__location", pnt)).order_by('distance')

            for v in vendors:
                v.kms = round(v.distance.km, 1)

        vendor_count = vendors.count()
        context = {
            'vendors': vendors,
            'vendor_count': vendor_count,
            'source_location': address,
        }
        return render(request, 'marketplace/listings.html', context)


@login_required(login_url='login')
def checkout(request):
    cart_items = Cart.objects.filter(user=request.user).order_by('created_at')
    cart_count = cart_items.count()
    if cart_count <= 0:
        return redirect('marketplace')

    user_profile = UserProfile.objects.get(user=request.user)
    default_values = {
        'first_name': request.user.first_name,
        'last_name': request.user.last_name,
        'phone': request.user.phone_number,
        'email': request.user.email,
        'address': user_profile.address,
        'country': user_profile.country,
        'state': user_profile.state,
        'city': user_profile.city,
        'pin_code': user_profile.pin_code,
    }
    form = OrderForm(initial=default_values)

    context = {
        'form': form,
        'cart_items': cart_items,
    }
    return render(request, 'marketplace/checkout.html', context)