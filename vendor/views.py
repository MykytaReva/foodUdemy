from django.shortcuts import render, get_object_or_404, redirect
from .forms import VendorForm
from accounts.forms import UserProfileForm
from accounts.models import UserProfile
from .models import Vendor
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from accounts.utils import check_role_vendor
# from accounts.views import check_role_vendor
from menu.models import Category, FoodItem
from menu.forms import CategoryForm, FoodItemForm
from django.template.defaultfilters import slugify



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
            category.slug = slugify(category_name)
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