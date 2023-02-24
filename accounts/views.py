from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required, user_passes_test


from .forms import UserForm
from .models import User, UserProfile


from vendor.models import Vendor
from vendor.forms import VendorForm


from .utils import detectUser, check_role_vendor, check_role_customer






def registerUser(request):
    if request.user.is_authenticated:
        messages.warning(request, 'You are already logged in!')
        return redirect('custDashboard')
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            # using the form
            # password = form.cleaned_data['password']
            # print(form.cleaned_data)
            # user = form.save(commit=False)
            # user.set_password(password)
            # user.role = User.CUSTOMER
            # form.save()

            # create user using method
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            user = User.objects.create_user(
                email=email,
                first_name=first_name,
                last_name=last_name,
                username=username,
                password=password
            )
            user.role = User.CUSTOMER
            user.save()

            messages.success(request, 'Account created, check your inbox for the activation email.')

            return redirect('registerUser')
        else:
            print('Invalid form:')
            print(form.errors)
    else:
        form = UserForm()
    # form = UserForm()
    # form.save()
    context = {
        'form': form,
    }
    return render(request, 'accounts/registerUser.html', context=context)


def registerVendor(request):
    if request.user.is_authenticated:
        messages.warning(request, 'You are already logged in!')
        return redirect('vendorDashboard')
    if request.method == 'POST':
        # store the data and create the user
        form = UserForm(request.POST)
        v_form = VendorForm(request.POST, request.FILES)
        if form.is_valid() and v_form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            user = User.objects.create_user(
                email=email,
                first_name=first_name,
                last_name=last_name,
                username=username,
                password=password
            )
            user.role = User.VENDOR
            user.save()

            vendor = v_form.save(commit=False)
            vendor.user = user
            user_profile = UserProfile.objects.get(user=user)
            vendor.user_profile = user_profile
            # vendor.vendor_name = form.cleaned_data['vendor_name']
            # vendor.vendor_license = form.cleaned_data['vendor_license']

            vendor.save()
            messages.success(request, 'Your account has been created successfully! Please wait for the approval')
            return redirect('home')
        else:
            print('invalid form')
            print(form.errors)
    else:
        form = UserForm()
        v_form = VendorForm()

    context = {
        'form': form,
        'v_form': v_form,
    }

    return render(request, 'accounts/registerVendor.html', context=context)


def login(request):
    if request.user.is_authenticated:
        messages.warning(request, 'You are already logged in!')
        return redirect('myAccount')
    elif request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        user = auth.authenticate(email=email, password=password)
        if user is not None:
            auth.login(request, user)
            messages.success(request, 'You are now logged in.')
            return redirect('custDashboard')
        else:
            messages.error(request, 'Invalid login credentials')
            return redirect('login')
    return render(request, 'accounts/login.html')


def logout(request):
    auth.logout(request)
    messages.info(request, 'You are logged out.')
    return redirect('login')


@login_required(login_url='login')
def myAccount(request):
    user = request.user
    redirectUrl = detectUser(user)
    return redirect(redirectUrl)


@login_required(login_url='login')
@user_passes_test(check_role_customer)
def custDashboard(request):
    return render(request, 'accounts/custDashboard.html')


@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def vendorDashboard(request):
    return render(request, 'accounts/vendorDashboard.html')
