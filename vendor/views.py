from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.template.defaultfilters import slugify
from django.db import IntegrityError
from django.http import HttpResponse, JsonResponse


from accounts.forms import UserProfileForm
from accounts.models import UserProfile
from accounts.utils import check_role_vendor

from orders.models import Order, OrderedFood

from menu.models import Category, FoodItem
from menu.forms import CategoryForm, FoodItemForm

from .forms import VendorForm, OpeningHourForm
from .models import Vendor, OpeningHour


def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'


def get_vendor(request):
    vendor = Vendor.objects.get(user=request.user)
    return vendor


@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def vprofile(request):

    profile = get_object_or_404(UserProfile, user=request.user)
    vendor = get_object_or_404(Vendor, user=request.user)

    if request.method == 'POST':
        profile_form =UserProfileForm(request.POST, request.FILES, instance=profile)
        vendor_form = VendorForm(request.POST, request.FILES, instance=vendor)
        if profile_form.is_valid() and vendor_form.is_valid():
            profile_form.save()
            vendor_form.save()
            messages.success(request, 'settings updated.')
            return redirect('vprofile')
        else:
            print(profile_form.errors)
            print(vendor_form.errors)
    else:
        profile_form = UserProfileForm(instance=profile)
        vendor_form = VendorForm(instance=vendor)

    context = {
        'profile_form': profile_form,
        'vendor_form': vendor_form,
        'profile': profile,
        'vendor': vendor,
    }

    return render(request, 'vendor/vprofile.html', context=context)


@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def menu_builder(request):
    vendor = get_vendor(request)
    categories = Category.objects.filter(vendor=vendor).order_by('created_at')
    context = {
        'categories': categories,
    }
    return render(request, 'vendor/menu_builder.html', context=context)





# def check_user(request, arguments_lists):
#     def check_specific_vendor(user):
#         if 1:
#             return True
#         else:
#             raise PermissionDenied
#     return check_specific_vendor




@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def fooditems_by_category(request, category_slug=None):
    vendor = get_vendor(request)
    category = get_object_or_404(Category, slug=category_slug)
    fooditems = FoodItem.objects.filter(vendor=vendor, category=category)
    context = {
        'fooditems': fooditems,
        'category': category,
    }
    return render(request, 'vendor/fooditems_by_category.html', context=context)


@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def add_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category_name = form.cleaned_data['category_name']
            print(form.cleaned_data)
            category = form.save(commit=False)
            category.vendor = get_vendor(request)
            category.save()
            category.slug = slugify(category_name) + '-' + str(category.id)
            form.save()
            messages.success(request, ' Category added successfuly!')
            return redirect('menu_builder')
        else:
            print(form.errors)
    else:
        form = CategoryForm()
    context = {
        'form': form,
    }
    return render(request, 'vendor/add_category.html', context=context)


@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def edit_category(request, category_slug=None):
    category = get_object_or_404(Category, slug=category_slug)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            category_name = form.cleaned_data['category_name']
            print(form.cleaned_data)
            category = form.save(commit=False)
            category.vendor = get_vendor(request)
            category.slug = slugify(category_name)
            form.save()
            messages.success(request, ' Category updated successfuly!')
            return redirect('menu_builder')
        else:
            print(form.errors)
    else:
        form = CategoryForm(instance=category)
    context = {
        'form': form,
        'category': category,
    }
    return render(request, 'vendor/edit_category.html', context=context)


@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def delete_category(request, category_slug=None):
    category = get_object_or_404(Category, slug=category_slug)
    category.delete()
    messages.success(request, ' Category has been deleted successfuly!')
    return redirect('menu_builder')

@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def add_food(request):
    if request.method == 'POST':
        form = FoodItemForm(request.POST, request.FILES)
        if form.is_valid():
            foodtitle = form.cleaned_data['food_title']
            food = form.save(commit=False)
            food.vendor = get_vendor(request)
            food.slug = slugify(foodtitle)
            form.save()
            messages.success(request, ' Food Item added successfuly!')
            return redirect('fooditems_by_category', food.category.slug)
        else:
            print(form.errors)
    else:
        form = FoodItemForm()
        # modify this form
        form.fields['category'].queryset =  Category.objects.filter(vendor=get_vendor(request))
    context = {
        'form': form,
    }

    return render(request, 'vendor/add_food.html', context)


@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def edit_food(request, food_slug=None):
    food = get_object_or_404(FoodItem, slug=food_slug)
    if request.method == 'POST':
        form = FoodItemForm(request.POST, request.FILES, instance=food)
        if form.is_valid():
            foodtitle = form.cleaned_data['food_title']
            food = form.save(commit=False)
            food.vendor = get_vendor(request)
            food.slug = slugify(foodtitle)
            form.save()
            messages.success(request, ' Food Item updated successfuly!')
            return redirect('fooditems_by_category', food.category.slug)
        else:
            print(form.errors)
    else:
        form = FoodItemForm(instance=food)
        form.fields['category'].queryset =  Category.objects.filter(vendor=get_vendor(request))

    context = {
        'form': form,
        'food': food,
    }
    return render(request, 'vendor/edit_food.html', context=context)


@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def delete_food(request, food_slug=None):
    food = get_object_or_404(FoodItem, slug=food_slug)
    food.delete()
    messages.success(request, 'Food Item has been deleted successfuly!')
    return redirect('fooditems_by_category', food.category.slug)



@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def opening_hours(request):
    opeing_hours = OpeningHour.objects.filter(vendor=get_vendor(request))
    form = OpeningHourForm()
    context = {
        'form': form,
        'opening_hours': opeing_hours,
    }
    return render(request, 'vendor/opening_hours.html', context)


@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def add_opening_hours(request):
    # handle the data and save them inside db
    if request.user.is_authenticated:
        # if is_ajax(request=request):
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            day = request.POST.get('day')
            from_hour = request.POST.get('from_hour')
            to_hour = request.POST.get('to_hour')
            is_closed = request.POST.get('is_closed')

            try:
                hour = OpeningHour.objects.create(vendor=get_vendor(request), day=day, from_hour=from_hour, to_hour=to_hour, is_closed=is_closed)
                if hour:
                    day  = OpeningHour.objects.get(id=hour.id)
                    if day.is_closed:
                        response = {'status': 'success', 'id': hour.id, 'day': day.get_day_display(), 'is_closed': 'Closed'}
                    else:
                        response = {'status': 'success', 'id': hour.id, 'day': day.get_day_display(), 'from_hour': hour.from_hour, 'to_hour': hour.to_hour}
                return JsonResponse(response)
            except IntegrityError as e:
                response = {'status':'failed', 'message': from_hour+'-'+to_hour+' already exists for this day!'}
                return JsonResponse(response)
            return HttpResponse('Good Request...')
        else:
            return HttpResponse('Invalid Request...')


@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def remove_opening_hours(request, pk=None):
    if request.user.is_authenticated:
        if is_ajax(request=request):
            hour = get_object_or_404(OpeningHour, pk=pk)
            hour.delete()
    return JsonResponse({'status': 'success', 'id': pk})



def order_detail(request, order_number):
    try:
        order = Order.objects.get(order_number=order_number, is_ordered=True)
        ordered_food = OrderedFood.objects.filter(order=order, fooditem__vendor=get_vendor(request))

        # total_revenue = 0
        # for i in ordered_food:
        #     total_revenue += item.fooditem.price

        context = {
            'order': order,
            'ordered_food': ordered_food,
            'subtotal': order.get_total_by_vendor()['subtotal'],
            'tax_data': order.get_total_by_vendor()['tax_dict'],
            'total': order.get_total_by_vendor()['total'],
        }



        return render(request, 'vendor/order_detail.html', context)
    except:
        return redirect('vendor')


@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def my_orders(request):
    try:
        orders = Order.objects.filter(vendors__in=[get_vendor(request)], is_ordered=True).order_by('created_at')

        context = {
            'orders': orders,

        }
        return render(request, 'vendor/my_orders.html', context)
    except:
        return redirect('vendorDashboard')
